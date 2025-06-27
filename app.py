import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from math import exp, cos, sin, radians, sqrt
import io

# Configuración de página
st.set_page_config(
    page_title="RMR14 UNI - Trabajo Escalonado Geomecánica",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado - simplificado
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Funciones de cálculo RMR (importadas de notebooks)
@st.cache_data
def load_default_data():
    """Cargar datos por defecto"""
    try:
        return pd.read_csv('data/consolidated_data.csv')
    except:
        return None

def calculate_rqd_from_frequency(num_discontinuities, total_length_m):
    """Calcular RQD desde frecuencia de discontinuidades"""
    if total_length_m <= 0:
        return 0
    lambda_freq = num_discontinuities / total_length_m
    rqd = 100 * exp(-0.1 * lambda_freq) * (0.1 * lambda_freq + 1)
    return max(0, min(100, rqd))

def get_rqd_rating(rqd):
    if rqd >= 90: return 20
    elif rqd >= 75: return 17
    elif rqd >= 50: return 13
    elif rqd >= 25: return 8
    else: return 3

def get_spacing_rating(spacing_mm):
    if spacing_mm >= 2000: return 20
    elif spacing_mm >= 600: return 15
    elif spacing_mm >= 200: return 10
    elif spacing_mm >= 60: return 8
    else: return 5

def get_discontinuity_condition_rating(aperture_code, roughness_code, weathering_code, infilling_code):
    base_rating = 30
    aperture_penalty = (aperture_code - 1) * 2
    roughness_penalty = (roughness_code - 1) * 1.5
    weathering_penalty = (weathering_code - 1) * 3
    infilling_penalty = 0 if infilling_code <= 2 else (5 if infilling_code == 3 else 3)
    total_rating = base_rating - aperture_penalty - roughness_penalty - weathering_penalty - infilling_penalty
    return max(0, min(30, total_rating))

def get_groundwater_rating(groundwater_code):
    ratings = {1: 15, 2: 10, 3: 7, 4: 4, 5: 0}
    return ratings.get(groundwater_code, 7)

def calculate_station_rmr(data, station):
    """Calcular RMR14 para una estación específica"""
    df_station = data[data['Station'] == station].copy()
    
    # Parámetros básicos
    num_discontinuities = len(df_station)
    total_length = df_station['Distance_m'].max()
    
    # Conversiones
    persistence_conversion = {1: 0.5, 2: 2.0, 3: 6.5, 4: 15.0, 5: 25.0}
    spacing_conversion = {1: 10, 2: 40, 3: 130, 4: 400, 5: 800}
    
    # Calcular RQD
    rqd = calculate_rqd_from_frequency(num_discontinuities, total_length)
    
    # Calcular espaciado promedio
    df_station['Spacing_mm_real'] = df_station['Spacing_mm'].map(spacing_conversion)
    spacing_avg = df_station['Spacing_mm_real'].mean()
    
    # Ratings
    rating_strength = 7  # R4 - 75 MPa
    rating_rqd = get_rqd_rating(rqd)
    rating_spacing = get_spacing_rating(spacing_avg)
    
    rating_conditions = get_discontinuity_condition_rating(
        df_station['Aperture_mm'].mean(),
        df_station['Roughness'].mean(),
        df_station['Weathering'].mean(),
        df_station['Infilling_Type'].mean()
    )
    
    rating_groundwater = get_groundwater_rating(int(df_station['Groundwater'].mean()))
    orientation_adjustment = -5
    
    rmr_total = (rating_strength + rating_rqd + rating_spacing + 
                rating_conditions + rating_groundwater + orientation_adjustment)
    
    # Clasificación
    if rmr_total >= 81: classification = "Clase I - Muy buena"
    elif rmr_total >= 61: classification = "Clase II - Buena"
    elif rmr_total >= 41: classification = "Clase III - Regular"
    elif rmr_total >= 21: classification = "Clase IV - Mala"
    else: classification = "Clase V - Muy mala"
    
    return {
        'Station': station,
        'RMR_Total': rmr_total,
        'Classification': classification,
        'RQD': rqd,
        'Spacing_mm': spacing_avg,
        'Num_Discontinuities': num_discontinuities,
        'Total_Length': total_length,
        'Ratings': {
            'Strength': rating_strength,
            'RQD': rating_rqd,
            'Spacing': rating_spacing,
            'Conditions': rating_conditions,
            'Groundwater': rating_groundwater,
            'Orientation': orientation_adjustment
        }
    }

# Header principal simplificado
st.markdown("# 🏔️ RMR14 - Análisis Geotécnico Cerros UNI")

# Sidebar
st.sidebar.markdown("## ⚙️ Configuración")

# Opción de datos
data_option = st.sidebar.radio(
    "Seleccionar fuente de datos:",
    ["Usar datos de ejemplo (Cerros UNI)", "Cargar archivo CSV personalizado"]
)

# Cargar datos
if data_option == "Usar datos de ejemplo (Cerros UNI)":
    data = load_default_data()
    if data is None:
        st.error("No se pudieron cargar los datos de ejemplo. Por favor, carga un archivo CSV.")
        st.stop()
    st.sidebar.success("✅ Datos de Cerros UNI cargados")
else:
    uploaded_file = st.sidebar.file_uploader(
        "Cargar archivo CSV",
        type=['csv'],
        help="El archivo debe tener las columnas: Station, Dip_Direction_degrees, Dip_degrees, Spacing_mm, etc."
    )
    
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.sidebar.success(f"✅ Archivo cargado: {len(data)} registros")
    else:
        st.info("👆 Por favor, carga un archivo CSV o usa los datos de ejemplo")
        st.stop()

# Tabs principales
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Vista General", "🔢 Análisis RMR14", "👨‍👩‍👧‍👦 Familias de Discontinuidades", "📋 Datos Detallados", "📚 Catálogo RMR14", "ℹ️ Acerca de"])

with tab1:
    st.markdown("## 📈 Resumen Ejecutivo")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Métricas generales
    total_stations = data['Station'].nunique()
    total_records = len(data)
    
    with col1:
        st.metric("🏔️ Estaciones", total_stations)
    
    with col2:
        st.metric("📏 Registros totales", total_records)
    
    # Calcular RMR promedio
    rmr_results = []
    for station in data['Station'].unique():
        result = calculate_station_rmr(data, station)
        rmr_results.append(result)
    
    avg_rmr = np.mean([r['RMR_Total'] for r in rmr_results])
    
    with col3:
        st.metric("⭐ RMR14 Promedio", f"{avg_rmr:.1f}")
    
    with col4:
        classification_counts = {}
        for r in rmr_results:
            cls = r['Classification']
            classification_counts[cls] = classification_counts.get(cls, 0) + 1
        most_common = max(classification_counts.items(), key=lambda x: x[1])
        st.metric("🎯 Clasificación Dominante", most_common[0].split(' - ')[1])
    
    # Gráfico de resumen
    st.markdown("### 📊 RMR14 por Estación")
    
    df_summary = pd.DataFrame(rmr_results)
    
    fig = px.bar(
        df_summary, 
        x='Station', 
        y='RMR_Total',
        color='Classification',
        title="RMR14 por Estación",
        labels={'RMR_Total': 'RMR14 Total', 'Station': 'Estación'}
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Mapa de calor de orientaciones
    st.markdown("### 🧭 Distribución de Orientaciones")
    
    fig_polar = go.Figure()
    
    for station in data['Station'].unique():
        df_station = data[data['Station'] == station].dropna(subset=['Dip_Direction_degrees'])
        if len(df_station) > 0:
            fig_polar.add_trace(go.Scatterpolar(
                r=[1] * len(df_station),
                theta=df_station['Dip_Direction_degrees'],
                mode='markers',
                name=f'Estación {station}',
                marker=dict(size=8)
            ))
    
    fig_polar.update_layout(
        polar=dict(
            radialaxis=dict(visible=False),
            angularaxis=dict(direction="clockwise", period=360)
        ),
        height=500,
        title="Distribución de Orientaciones por Estación"
    )
    
    st.plotly_chart(fig_polar, use_container_width=True)

with tab2:
    st.markdown("## 🔢 Análisis Detallado RMR14")
    
    # Selector de estación
    selected_station = st.selectbox(
        "Seleccionar estación para análisis detallado:",
        data['Station'].unique(),
        format_func=lambda x: f"Estación {x}"
    )
    
    # Calcular RMR para estación seleccionada
    station_result = calculate_station_rmr(data, selected_station)
    
    # Mostrar resultados
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### 📍 Estación {selected_station}")
        
        # Breakdown de ratings
        ratings = station_result['Ratings']
        
        breakdown_data = pd.DataFrame({
            'Parámetro': ['Resistencia UCS', 'RQD', 'Espaciado', 'Condiciones', 'Agua Subterránea', 'Orientación'],
            'Rating': [ratings['Strength'], ratings['RQD'], ratings['Spacing'], 
                      ratings['Conditions'], ratings['Groundwater'], ratings['Orientation']],
            'Valor': [f"75 MPa (R4)", f"{station_result['RQD']:.1f}%", 
                     f"{station_result['Spacing_mm']:.0f} mm", "Promedio códigos",
                     "Según códigos", "Desfavorable"]
        })
        
        fig_breakdown = px.bar(
            breakdown_data,
            x='Parámetro',
            y='Rating',
            color='Rating',
            title=f"Desglose RMR14 - Estación {selected_station}",
            color_continuous_scale='RdYlGn'
        )
        
        fig_breakdown.update_layout(height=400)
        st.plotly_chart(fig_breakdown, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Resultado Final")
        st.markdown(f"## **{station_result['RMR_Total']:.1f}**")
        st.markdown(f"**{station_result['Classification']}**")
        
        st.markdown("### 📊 Parámetros Clave")
        st.metric("RQD Calculado", f"{station_result['RQD']:.1f}%")
        st.metric("Discontinuidades", station_result['Num_Discontinuities'])
        st.metric("Longitud Total", f"{station_result['Total_Length']:.2f} m")
        st.metric("Espaciado Promedio", f"{station_result['Spacing_mm']:.0f} mm")

with tab3:
    st.markdown("## 👨‍👩‍👧‍👦 Análisis de Familias de Discontinuidades")
    
    st.markdown("""
    ### 🔍 Metodología de Análisis
    - **Agrupación**: Clustering angular con tolerancia ±15°
    - **Criterio**: Mínimo 3 miembros por familia
    - **Análisis**: Propiedades estadísticas y RMR específico por familia
    """)
    
    # Funciones para análisis de familias (adaptadas del notebook)
    def calculate_angular_distance(dip_dir1, dip_dir2):
        """Calcula distancia angular considerando naturaleza circular"""
        diff = abs(dip_dir1 - dip_dir2)
        return min(diff, 360 - diff)

    def identify_families(orientations, tolerance=15, min_members=3):
        """Identifica familias basado en orientaciones similares"""
        n = len(orientations)
        visited = [False] * n
        families = []
        
        for i in range(n):
            if visited[i]:
                continue
                
            current_family = [i]
            visited[i] = True
            
            for j in range(i + 1, n):
                if visited[j]:
                    continue
                    
                distances = [calculate_angular_distance(orientations[k], orientations[j]) 
                           for k in current_family]
                avg_distance = np.mean(distances)
                
                if avg_distance <= tolerance:
                    current_family.append(j)
                    visited[j] = True
            
            if len(current_family) >= min_members:
                families.append(current_family)
        
        return families

    def analyze_family_properties(df_family):
        """Analiza propiedades estadísticas de una familia"""
        return {
            'Count': len(df_family),
            'Dip_Direction_mean': df_family['Dip_Direction_degrees'].mean(),
            'Dip_Direction_std': df_family['Dip_Direction_degrees'].std(),
            'Spacing_code_mean': df_family['Spacing_mm'].mean(),
            'Persistence_code_mean': df_family['Persistence_m'].mean(),
            'Aperture_code_mean': df_family['Aperture_mm'].mean(),
            'Roughness_code_mean': df_family['Roughness'].mean(),
            'Weathering_code_mean': df_family['Weathering'].mean(),
            'Infilling_code_mean': df_family['Infilling_Type'].mean(),
            'Groundwater_code_mean': df_family['Groundwater'].mean()
        }

    def calculate_family_rmr(family_properties, station_length):
        """Calcula RMR específico para una familia"""
        rating_strength = 7  # R4 - 75 MPa
        
        family_rqd = calculate_rqd_from_frequency(family_properties['Count'], station_length)
        rating_rqd = get_rqd_rating(family_rqd)
        
        spacing_conversion = {1: 10, 2: 40, 3: 130, 4: 400, 5: 800}
        spacing_mm = spacing_conversion.get(int(family_properties['Spacing_code_mean']), 130)
        rating_spacing = get_spacing_rating(spacing_mm)
        
        rating_conditions = get_discontinuity_condition_rating(
            family_properties['Aperture_code_mean'],
            family_properties['Roughness_code_mean'],
            family_properties['Weathering_code_mean'],
            family_properties['Infilling_code_mean']
        )
        
        rating_groundwater = get_groundwater_rating(int(family_properties['Groundwater_code_mean']))
        orientation_adjustment = -5
        
        rmr_total = (rating_strength + rating_rqd + rating_spacing + 
                    rating_conditions + rating_groundwater + orientation_adjustment)
        
        return {
            'RMR_total': rmr_total,
            'RQD_family': family_rqd,
            'Spacing_mm': spacing_mm,
            'ratings': {
                'strength': rating_strength,
                'rqd': rating_rqd,
                'spacing': rating_spacing,
                'conditions': rating_conditions,
                'groundwater': rating_groundwater
            }
        }
    
    # Realizar análisis de familias
    all_families_results = []
    
    for station in data['Station'].unique():
        df_station = data[data['Station'] == station].copy()
        df_valid = df_station.dropna(subset=['Dip_Direction_degrees'])
        
        if len(df_valid) == 0:
            continue
            
        orientations = df_valid['Dip_Direction_degrees'].tolist()
        families = identify_families(orientations, tolerance=15, min_members=3)
        
        station_length = df_station['Distance_m'].max()
        
        for family_idx, family_indices in enumerate(families, 1):
            df_family = df_valid.iloc[family_indices]
            family_properties = analyze_family_properties(df_family)
            family_rmr = calculate_family_rmr(family_properties, station_length)
            
            family_result = {
                'Station': station,
                'Family': f'F{family_idx}',
                'Count': family_properties['Count'],
                'Dip_Direction_mean': family_properties['Dip_Direction_mean'],
                'Dip_Direction_std': family_properties['Dip_Direction_std'],
                'RMR_total': family_rmr['RMR_total'],
                'RQD_family': family_rmr['RQD_family'],
                'Spacing_mm': family_rmr['Spacing_mm']
            }
            all_families_results.append(family_result)
    
    df_families = pd.DataFrame(all_families_results)
    
    if not df_families.empty:
        # Crear columna para identificación
        df_families['Family_Station'] = 'Est' + df_families['Station'].astype(str) + '_' + df_families['Family']
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏔️ Familias Identificadas", len(df_families))
        
        with col2:
            st.metric("📊 RMR Promedio", f"{df_families['RMR_total'].mean():.1f}")
        
        with col3:
            st.metric("👥 Miembros Promedio", f"{df_families['Count'].mean():.1f}")
        
        with col4:
            rmr_range = f"{df_families['RMR_total'].min():.1f} - {df_families['RMR_total'].max():.1f}"
            st.metric("📈 Rango RMR", rmr_range)
        
        st.markdown("---")
        
        # Visualizaciones
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 RMR14 por Familia")
            fig_families = px.bar(
                df_families, 
                x='Family_Station', 
                y='RMR_total',
                color='Station',
                title="RMR14 por Familia de Discontinuidades",
                labels={'RMR_total': 'RMR14 Total', 'Family_Station': 'Familia'},
                text='RMR_total'
            )
            fig_families.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_families.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_families, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Miembros vs RMR")
            fig_scatter = px.scatter(
                df_families, 
                x='Count', 
                y='RMR_total',
                color='Station',
                size='RQD_family',
                hover_data=['Family_Station', 'Dip_Direction_mean'],
                title="Número de Miembros vs RMR14",
                labels={'Count': 'Número de Miembros', 'RMR_total': 'RMR14 Total'}
            )
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Distribución de orientaciones por familia
        st.markdown("### 🧭 Distribución de Orientaciones por Familia")
        
        fig_polar_families = go.Figure()
        
        colors = px.colors.qualitative.Set3
        for i, (_, family) in enumerate(df_families.iterrows()):
            station = family['Station']
            family_name = family['Family']
            df_station = data[data['Station'] == station]
            df_valid = df_station.dropna(subset=['Dip_Direction_degrees'])
            orientations = df_valid['Dip_Direction_degrees'].tolist()
            families = identify_families(orientations, tolerance=15, min_members=3)
            
            if len(families) > int(family_name[1:]) - 1:
                family_indices = families[int(family_name[1:]) - 1]
                family_orientations = [orientations[idx] for idx in family_indices]
                
                fig_polar_families.add_trace(go.Scatterpolar(
                    r=[1] * len(family_orientations),
                    theta=family_orientations,
                    mode='markers',
                    name=family['Family_Station'],
                    marker=dict(size=8, color=colors[i % len(colors)])
                ))
        
        fig_polar_families.update_layout(
            polar=dict(
                radialaxis=dict(visible=False),
                angularaxis=dict(direction="clockwise", period=360)
            ),
            height=500,
            title="Orientaciones de Familias de Discontinuidades"
        )
        
        st.plotly_chart(fig_polar_families, use_container_width=True)
        
        # Tabla detallada de familias
        st.markdown("### 📋 Detalle de Familias Identificadas")
        
        # Formatear tabla para mejor presentación
        df_display = df_families.copy()
        df_display['Orientación'] = df_display['Dip_Direction_mean'].round(1).astype(str) + '° (±' + df_display['Dip_Direction_std'].round(1).astype(str) + '°)'
        df_display['RMR14'] = df_display['RMR_total'].round(1)
        df_display['RQD'] = df_display['RQD_family'].round(1).astype(str) + '%'
        df_display['Espaciado'] = df_display['Spacing_mm'].astype(str) + ' mm'
        
        df_table = df_display[['Station', 'Family', 'Count', 'Orientación', 'RMR14', 'RQD', 'Espaciado']]
        df_table.columns = ['Estación', 'Familia', 'Miembros', 'Orientación Media', 'RMR14', 'RQD', 'Espaciado']
        
        st.dataframe(df_table, use_container_width=True)
        
        # Resumen estadístico
        st.markdown("### 📈 Resumen Estadístico")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **Análisis General:**
            - Total familias: {len(df_families)}
            - RMR promedio: {df_families['RMR_total'].mean():.1f}
            - RMR mínimo: {df_families['RMR_total'].min():.1f}
            - RMR máximo: {df_families['RMR_total'].max():.1f}
            """)
        
        with col2:
            st.markdown(f"""
            **Distribución por Estación:**
            - Estación 1: {len(df_families[df_families['Station']==1])} familias
            - Estación 2: {len(df_families[df_families['Station']==2])} familias
            - Estación 3: {len(df_families[df_families['Station']==3])} familias
            - Estación 4: {len(df_families[df_families['Station']==4])} familias
            """)
        
        # Comparación familias vs estación
        st.markdown("### ⚖️ Comparación: Familias vs Promedio de Estación")
        
        # Calcular RMR promedio por estación
        station_rmr = []
        for station in data['Station'].unique():
            result = calculate_station_rmr(data, station)
            station_rmr.append({'Station': station, 'RMR_Station': result['RMR_Total']})
        
        df_station_rmr = pd.DataFrame(station_rmr)
        df_comparison = df_families.merge(df_station_rmr, on='Station')
        df_comparison['RMR_Difference'] = df_comparison['RMR_total'] - df_comparison['RMR_Station']
        
        fig_comparison = px.bar(
            df_comparison, 
            x='Family_Station', 
            y=['RMR_Station', 'RMR_total'],
            title="Comparación RMR: Familias vs Promedio de Estación",
            labels={'value': 'RMR14', 'Family_Station': 'Familia'},
            barmode='group'
        )
        fig_comparison.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Interpretación
        st.markdown("### 🔍 Interpretación Geotécnica")
        st.info("""
        **Observaciones principales:**
        - Se identificaron 9 familias de discontinuidades con orientaciones dominantes
        - Las familias muestran RMR14 variable (62.8 - 80.5), indicando heterogeneidad local
        - El análisis por familias permite identificar zonas de mejor/peor calidad dentro de cada estación
        - Las familias con mayor número de miembros tienden a tener orientaciones más consistentes (menor desviación)
        """)
        
    else:
        st.warning("⚠️ No se identificaron familias suficientes con los criterios establecidos (mín. 3 miembros, tolerancia ±15°)")
        st.markdown("""
        **Posibles razones:**
        - Orientaciones muy dispersas
        - Pocas discontinuidades por estación
        - Criterios muy restrictivos
        
        **Recomendaciones:**
        - Aumentar tolerancia angular (±20° o ±25°)
        - Reducir número mínimo de miembros a 2
        - Analizar estaciones individualmente
        """)

with tab4:
    st.markdown("## 📋 Datos Detallados")
    
    # Mostrar datos raw
    st.markdown("### 📄 Datos Consolidados")
    st.dataframe(data, use_container_width=True)
    
    # Opción de descarga
    csv = data.to_csv(index=False)
    st.download_button(
        label="📥 Descargar datos como CSV",
        data=csv,
        file_name=f"rmr14_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )
    
    # Estadísticas básicas
    st.markdown("### 📈 Estadísticas Descriptivas")
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    st.dataframe(data[numeric_cols].describe(), use_container_width=True)

with tab5:
    st.markdown("## 📚 Catálogo RMR14 - Tablas de Referencia")
    
    st.markdown("### 🔍 Sistema de Clasificación Geomecánica")
    st.markdown("""
    El sistema RMR14 utiliza tablas de referencia estandarizadas para evaluar cada parámetro.
    Esta sección presenta las tablas oficiales utilizadas en el análisis de Cerros UNI.
    """)
    
    # Crear dos columnas para las tablas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💪 Parámetro 1: Resistencia UCS")
        resistance_data = {
            "Resistencia (MPa)": [">250", "100-250", "50-100", "25-50", "5-25", "1-5", "<1"],
            "Clase": ["R6", "R5", "R4", "R3", "R2", "R1", "R0"],
            "Rating": [15, 12, 7, 4, 2, 1, 0],
            "Descripción": ["Extremadamente fuerte", "Muy fuerte", "Fuerte", "Moderadamente fuerte", "Débil", "Muy débil", "Extremadamente débil"]
        }
        st.dataframe(pd.DataFrame(resistance_data), use_container_width=True)
        
        st.markdown("#### 📏 Parámetro 3: Espaciado de Discontinuidades")
        spacing_data = {
            "Espaciado": [">2 m", "0.6-2 m", "200-600 mm", "60-200 mm", "<60 mm"],
            "Descripción": ["Muy amplio", "Amplio", "Moderado", "Cerrado", "Muy cerrado"],
            "Rating": [20, 15, 10, 8, 5]
        }
        st.dataframe(pd.DataFrame(spacing_data), use_container_width=True)
        
        st.markdown("#### 💧 Parámetro 5: Condiciones de Agua Subterránea")
        water_data = {
            "Código": [1, 2, 3, 4, 5],
            "Condición": ["Completamente seco", "Húmedo", "Goteo", "Flujo", "Flujo intenso"],
            "Descripción": ["Sin agua", "Ligeramente húmedo", "Goteo ocasional", "Flujo continuo", "Flujo abundante"],
            "Rating": [15, 10, 7, 4, 0]
        }
        st.dataframe(pd.DataFrame(water_data), use_container_width=True)
    
    with col2:
        st.markdown("#### 🔧 Parámetro 2: RQD (Rock Quality Designation)")
        rqd_data = {
            "RQD (%)": ["90-100", "75-90", "50-75", "25-50", "<25"],
            "Calidad": ["Excelente", "Buena", "Regular", "Pobre", "Muy pobre"],
            "Rating": [20, 17, 13, 8, 3]
        }
        st.dataframe(pd.DataFrame(rqd_data), use_container_width=True)
        
        st.markdown("#### 🔗 Parámetro 4: Condición de las Discontinuidades")
        st.markdown("**4a. Persistencia (Longitud)**")
        persistence_data = {
            "Código": [1, 2, 3, 4, 5],
            "Persistencia": ["<1 m", "1-3 m", "3-10 m", "10-20 m", ">20 m"],
            "Conversión (m)": [0.5, 2.0, 6.5, 15.0, 25.0],
            "Rating": [6, 4, 2, 1, 0]
        }
        st.dataframe(pd.DataFrame(persistence_data), use_container_width=True)
        
        st.markdown("**4b. Apertura**")
        aperture_data = {
            "Código": [1, 2, 3, 4, 5],
            "Apertura": ["Cerrada", "<0.1 mm", "0.1-1.0 mm", "1-5 mm", ">5 mm"],
            "Rating": [6, 5, 3, 1, 0]
        }
        st.dataframe(pd.DataFrame(aperture_data), use_container_width=True)
        
        st.markdown("**4c. Rugosidad**")
        roughness_data = {
            "Código": [1, 2, 3, 4, 5],
            "Rugosidad": ["Muy rugosa", "Rugosa", "Ligeramente rugosa", "Lisa", "Espejo de falla"],
            "Rating": [6, 5, 3, 1, 0]
        }
        st.dataframe(pd.DataFrame(roughness_data), use_container_width=True)
    
    st.markdown("---")
    
    # Tabla de clasificación final
    st.markdown("### 🎯 Clasificación Final RMR")
    
    col3, col4 = st.columns([1, 1])
    
    with col3:
        classification_data = {
            "Clase": ["I", "II", "III", "IV", "V"],
            "RMR Total": ["81-100", "61-80", "41-60", "21-40", "0-20"],
            "Calidad": ["Muy buena", "Buena", "Regular", "Mala", "Muy mala"]
        }
        st.dataframe(pd.DataFrame(classification_data), use_container_width=True)
    
    with col4:
        st.markdown("#### 🔄 Ajuste por Orientación")
        orientation_data = {
            "Orientación": ["Muy favorable", "Favorable", "Regular", "Desfavorable", "Muy desfavorable"],
            "Túneles": [0, -2, -5, -10, -12],
            "Taludes": [0, -5, -25, -50, -60]
        }
        st.dataframe(pd.DataFrame(orientation_data), use_container_width=True)
    
    st.markdown("---")
    
    # Códigos de campo utilizados
    st.markdown("### 🏔️ Códigos de Campo Utilizados - Cerros UNI")
    
    st.markdown("#### 📊 Diccionario de Códigos Aplicados")
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("**Tipos de Estructura:**")
        st.markdown("""
        - **J**: Junta (diaclasa)
        - **F**: Falla
        - **E**: Espalte (foliación)
        """)
        
        st.markdown("**Relleno de Discontinuidades:**")
        fill_data = {
            "Código": [1, 2, 3, 4, 5],
            "Tipo de Relleno": ["Sin relleno", "Relleno duro <5mm", "Relleno duro >5mm", "Relleno blando <5mm", "Relleno blando >5mm"],
            "Rating": [6, 4, 2, 2, 0]
        }
        st.dataframe(pd.DataFrame(fill_data), use_container_width=True)
    
    with col6:
        st.markdown("**Meteorización:**")
        weathering_data = {
            "Código": [1, 2, 3, 4, 5],
            "Grado": ["Inalterada", "Ligeramente alterada", "Moderadamente alterada", "Muy alterada", "Descompuesta"],
            "Rating": [6, 5, 3, 1, 0]
        }
        st.dataframe(pd.DataFrame(weathering_data), use_container_width=True)
        
        st.markdown("**Conversión de Espaciado:**")
        spacing_conversion = {
            "Código": [1, 2, 3, 4, 5],
            "Espaciado Real (mm)": [10, 40, 130, 400, 800],
            "Descripción": ["Muy cerrado", "Cerrado", "Moderado", "Amplio", "Muy amplio"]
        }
        st.dataframe(pd.DataFrame(spacing_conversion), use_container_width=True)
    
    st.markdown("---")
    st.info("📋 **Nota:** Todas las tablas están basadas en la metodología estándar RMR14 de Bieniawski (1989) y han sido aplicadas consistentemente en el análisis de las 4 estaciones de Cerros UNI.")

with tab6:
    st.markdown("## ℹ️ Acerca de este Trabajo")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📚 Marco Teórico: RMR de Bieniawski (1989)
        
        El sistema de clasificación geomecánica **RMR (Rock Mass Rating)**, desarrollado por 
        Bieniawski en 1973 y refinado hasta su versión más utilizada en 1989 (RMR89), constituye 
        una metodología cuantitativa para evaluar la calidad de un macizo rocoso desde una 
        perspectiva estructural, geológica e ingenieril.
        
        #### 🎯 Propósito
        Su propósito es proporcionar un índice numérico representativo del comportamiento del 
        macizo ante excavaciones subterráneas, taludes o cimentaciones.
        
        #### 🔍 Fundamentos Geológicos
        Desde el punto de vista geológico, el macizo rocoso se concibe como un medio discontinuo, 
        compuesto por bloques delimitados por fracturas, diaclasas y planos de debilidad. La 
        naturaleza y distribución de estas discontinuidades, así como la litología del material 
        intacto, condicionan su resistencia global y su estabilidad.
        
        #### 📊 Los 5 Parámetros Fundamentales
        El RMR toma en cuenta cinco parámetros fundamentales que reflejan estas características:
        
        1. **Resistencia a compresión uniaxial** del material intacto
        2. **Índice de calidad de la roca (RQD)**
        3. **Espaciamiento de discontinuidades**
        4. **Condición de las discontinuidades** (persistencia, rugosidad, apertura, relleno, alteración)
        5. **Condiciones de agua** en las discontinuidades
        
        #### ⚖️ Sistema de Puntuación
        Desde la perspectiva geomecánica, cada uno de estos parámetros se traduce en un puntaje 
        parcial que refleja su influencia sobre el comportamiento mecánico del macizo. La suma de 
        estos puntajes, junto con un ajuste por la orientación relativa de las discontinuidades 
        respecto al diseño estructural, proporciona un valor total que varía entre 0 y 100.
        
        #### 🏗️ Clasificación de Calidad
        Este valor permite clasificar el macizo en una de cinco categorías de calidad:
        - **Clase I (81-100):** Muy buena
        - **Clase II (61-80):** Buena  
        - **Clase III (41-60):** Regular
        - **Clase IV (21-40):** Mala
        - **Clase V (0-20):** Muy mala
        
        Facilitando decisiones sobre sostenimiento, excavación y modelamiento.
        """)
        
        st.markdown("""
        ### 🏔️ Aplicación en Cerros UNI
        
        #### 📍 Ubicación del Estudio
        El presente trabajo aplica la metodología RMR14 a los **Cerros UNI**, ubicados en las 
        instalaciones de la Universidad Nacional de Ingeniería, como parte del Trabajo Escalonado 
        de Geomecánica.
        
        #### 🔬 Metodología Aplicada
        - **Levantamiento de campo:** 4 estaciones geológicas
        - **Digitalización completa:** 60 discontinuidades estructurales
        - **Análisis de familias:** Clustering angular con tolerancia ±15°
        - **Cálculo RQD alternativo:** Método empírico desde frecuencia de discontinuidades
        - **Plataforma interactiva:** Desarrollo web para análisis geotécnico
        
        #### 🎓 Contexto Académico
        Este trabajo forma parte de la asignatura **GE-823A: Geomecánica** de la Escuela 
        Profesional de Ingeniería Geológica, demostrando la aplicación práctica de conceptos 
        teóricos en un caso de estudio real dentro del campus universitario.
        """)
    
    with col2:
        st.markdown("""
        ### 👥 Información del Proyecto
        
        **🏛️ Institución:**  
        Universidad Nacional de Ingeniería
        
        **🎓 Facultad:**  
        Ingeniería Geológica, Minera y Metalúrgica
        
        **📚 Curso:**  
        GE-823A: Geomecánica
        
        **👨‍🏫 Docente:**  
        Msc. Ing. Joseph Andrew Soria Medina
        
        **📅 Fecha:**  
        27 de junio de 2025
        
        ---
        
        ### ✍️ Autores
        
        **Campos Bravo, Ronald Diego**  
        **Villacorta Leiva, Gabriela Cristina**  
        **Mandujano Gutierrez, Victor Jean Pierre**
        
        ---
        
        ### 🛠️ Tecnologías Utilizadas
        
        - **Python** - Análisis de datos
        - **Streamlit** - Interfaz web interactiva  
        - **Plotly** - Visualizaciones avanzadas
        - **Pandas** - Manipulación de datos
        - **NumPy** - Cálculos numéricos
        - **Jupyter** - Desarrollo y prototipado
        
        ---
        
        ### 📊 Resultados Principales
        
        **🏔️ Clasificación general:**  
        Clase II - Buena (RMR: 61.8 - 76.3)
        
        **📏 Datos procesados:**  
        60 discontinuidades en 4 estaciones
        
        **👨‍👩‍👧‍👦 Familias identificadas:**  
        9 familias estructurales principales
        
        **🔍 Metodología innovadora:**  
        RQD calculado desde frecuencia de discontinuidades
        """)
        
        st.markdown("""
        ### 🌟 Validación Académica
        
        El RMR ha sido ampliamente validado con base en observaciones empíricas en obras 
        subterráneas a nivel mundial, convirtiéndose en un estándar de referencia. Su carácter 
        sistemático, adaptable y empírico lo hace aplicable tanto en etapas de prospección como 
        en diseño y monitoreo.
        
        Además, sirve como base para correlaciones con otros sistemas como Q (de Barton) y 
        GSI (Hoek y Brown), integrando así el análisis estructural con modelos de resistencia 
        y deformabilidad en medios fracturados.
        """, help="Información basada en Bieniawski (1989) y aplicaciones modernas")

# Footer académico
st.markdown("---")
st.markdown("""
### 🏔️ RMR14 Análisis Geotécnico - Cerros UNI

**Universidad Nacional de Ingeniería** • Facultad de Ingeniería Geológica, Minera y Metalúrgica

Trabajo Escalonado de Geomecánica GE-823A • Basado en metodología Bieniawski 2014 • Junio 2025

*Plataforma web desarrollada para digitalización y análisis interactivo de discontinuidades estructurales*
""", help="Aplicación desarrollada como parte del trabajo académico de geomecánica") 