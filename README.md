# 🏔️ RMR14 - Análisis Geotécnico de Cerros UNI

Análisis completo de discontinuidades estructurales y cálculo RMR14 (Rock Mass Rating 2014) para macizos rocosos.

## 🚀 **NUEVO: Aplicación Web Interactiva**

### 🌐 **Interfaz Web User-Friendly**
Ahora disponible una **aplicación web interactiva** que hace el análisis RMR14 accesible sin configuración técnica:

- **🔗 Acceso directo:** Sin registro ni cuentas necesarias
- **📊 Dashboards interactivos:** Visualizaciones y análisis en tiempo real
- **📁 Carga de datos:** Usa tus propios CSV o ejemplos de Cerros UNI
- **📱 Mobile-friendly:** Funciona en móviles, tablets y desktop
- **📋 Exportar resultados:** Descarga análisis como archivos CSV

### 🏃‍♂️ **Inicio Rápido - Web App**
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación web
streamlit run app.py
# O usar script helper
python run_app.py

# Abrir: http://localhost:8501
```

### 🌍 **Deploy en Línea (Gratis)**
Ver [README_DEPLOYMENT.md](README_DEPLOYMENT.md) para opciones de hosting gratuito en Streamlit Cloud, Heroku, etc.

---

## 📊 **Datos del Proyecto**

### 🏔️ **Estaciones Analizadas: Cerros UNI**
- **Estación 1:** Cerros UNI (atrás de Pegado FIGMI) - 15 registros
- **Estación 2:** Cerros UNI (Bajo Tanque antiguo) - 15 registros  
- **Estación 3:** Cerros UNI (Bajo Nuevo Tanque) - 15 registros
- **Estación 4:** Cerros UNI - 15 registros
- **Total:** 60 discontinuidades estructurales digitalizadas

### 📋 **Variables Capturadas**
- Distancia, tipo de estructura (J=Junta, F=Falla, E=Espalte)
- Orientaciones (Dip Direction/Dip en grados)
- Espaciado, persistencia, apertura, rugosidad
- Relleno, meteorización, agua subterránea

---

## 🔢 **Metodología RMR14**

### 📊 **Resultados por Estación**
| Estación | RMR14 | Clasificación | RQD | Discontinuidades |
|----------|-------|---------------|-----|------------------|
| 1        | 63.1  | Clase II - Buena | 78.2% | 15 |
| 2        | 64.2  | Clase II - Buena | 81.3% | 15 |
| 3        | 61.8  | Clase II - Buena | 73.4% | 15 |
| 4        | 76.3  | Clase II - Buena | 92.1% | 15 |

### 🏗️ **Parámetros Aplicados**
- **Resistencia UCS:** R4 (75 MPa) - 7 puntos
- **RQD:** Calculado desde frecuencia de discontinuidades
- **Espaciado:** Rating según conversión de códigos
- **Condiciones:** Rating detallado por familia
- **Agua subterránea:** Según códigos de campo
- **Orientación:** Ajuste -5 (desfavorable)

---

## 👨‍👩‍👧‍👦 **Análisis de Familias**

### 🎯 **9 Familias Identificadas**
Clustering automático con tolerancia ±15° y mínimo 3 miembros por familia:

- **Familia 1:** 045°/65° (6 miembros) - RMR: 71.2
- **Familia 2:** 135°/45° (4 miembros) - RMR: 68.8
- **Familia 3:** 270°/80° (5 miembros) - RMR: 73.5
- *[...y 6 familias más]*

---

## 📁 **Estructura del Proyecto**

```
rmr14/
├── 🌐 app.py                     # Aplicación web Streamlit
├── 🚀 run_app.py                 # Script helper para ejecutar
├── 📊 notebooks/
│   ├── rmr14_calculation.ipynb   # Cálculo RMR14 por estación
│   └── families_analysis.ipynb   # Análisis de familias
├── 📄 data/
│   ├── station_1.csv - station_4.csv
│   ├── consolidated_data.csv     # Datos consolidados
│   └── codes_dictionary.csv      # Diccionario de códigos
├── ⚙️ .streamlit/
│   └── config.toml               # Configuración web app
├── 📝 README_DEPLOYMENT.md       # Guía de despliegue web
└── 📋 requirements.txt           # Dependencias
```

---

## 🛠️ **Instalación y Uso**

### 1. **Configuración Inicial**
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. **Opción A: Aplicación Web (Recomendado)**
```bash
# Ejecutar web app
streamlit run app.py

# Abrir navegador: http://localhost:8501
```

### 3. **Opción B: Notebooks Jupyter**
```bash
# Ejecutar Jupyter
jupyter notebook

# Abrir:
# - notebooks/rmr14_calculation.ipynb
# - notebooks/families_analysis.ipynb
```

---

## 🎯 **Características Principales**

### ✅ **Análisis RMR14 Completo**
- Cálculo automático para múltiples estaciones
- RQD alternativo desde frecuencia de discontinuidades
- Conversión automática de códigos de campo
- Clasificación geotécnica automática

### ✅ **Análisis de Familias Estructurales**  
- Clustering angular automático
- Estadísticas por familia vs. promedio estación
- Visualizaciones polares interactivas
- Identificación de orientaciones dominantes

### ✅ **Visualizaciones Avanzadas**
- Gráficos polares de orientaciones
- Histogramas de distribución de parámetros
- Mapas de calor de correlaciones
- Diagramas de barras comparativos

### ✅ **Web Interface Profesional**
- Dashboard interactivo multi-tab
- Carga de datos personalizada
- Exportación de resultados
- Responsive design

---

## 🌍 **Deploy y Compartir**

La forma más **rápida y user-friendly** de compartir tu análisis:

1. **Streamlit Cloud (Gratis):** Deploy automático desde GitHub
2. **Heroku (Básico gratis):** Hosting con mayor control
3. **Local sharing:** Red local para demos

Ver guía completa en [README_DEPLOYMENT.md](README_DEPLOYMENT.md)

---

## 📊 **Resultados y Conclusiones**

- **Macizo rocoso de calidad BUENA** (Clase II) en todas las estaciones
- **RMR14 promedio: 66.4** (rango: 61.8 - 76.3)
- **9 familias principales** identificadas con orientaciones dominantes
- **Metodología digitalizada** lista para aplicar en otros proyectos

---

## 🤝 **Contribuir**

Este proyecto implementa una metodología completa y reutilizable para análisis RMR14. ¡Las contribuciones son bienvenidas!

---

## 📄 **Licencia**

MIT License - Ver [LICENSE](LICENSE) para detalles. 