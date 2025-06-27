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
    page_title="RMR14 Análisis Geotécnico - Cerros UNI",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
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

# Header principal
st.markdown('<h1 class="main-header">🏔️ RMR14 Análisis Geotécnico - Cerros UNI</h1>', unsafe_allow_html=True)

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
tab1, tab2, tab3, tab4 = st.tabs(["📊 Vista General", "🔢 Análisis RMR14", "👨‍👩‍👧‍👦 Familias de Discontinuidades", "📋 Datos Detallados"])

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
        
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="color: #1f77b4; margin: 0;">RMR14 Total</h2>
            <h1 style="color: #d62728; margin: 0;">{station_result['RMR_Total']:.1f}</h1>
            <p style="margin: 0;"><strong>{station_result['Classification']}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📊 Parámetros Clave")
        st.metric("RQD Calculado", f"{station_result['RQD']:.1f}%")
        st.metric("Discontinuidades", station_result['Num_Discontinuities'])
        st.metric("Longitud Total", f"{station_result['Total_Length']:.2f} m")
        st.metric("Espaciado Promedio", f"{station_result['Spacing_mm']:.0f} mm")

with tab3:
    st.markdown("## 👨‍👩‍👧‍👦 Análisis de Familias de Discontinuidades")
    st.info("🚧 Esta sección implementaría el análisis completo de familias con clustering angular y visualizaciones interactivas.")
    
    # Aquí se puede agregar el análisis de familias completo

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

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    🏔️ <strong>RMR14 Análisis Geotécnico</strong> | 
    Desarrollado para análisis de discontinuidades en macizos rocosos | 
    Basado en metodología Bieniawski 2014
</div>
""", unsafe_allow_html=True) 