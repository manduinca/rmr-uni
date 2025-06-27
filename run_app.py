#!/usr/bin/env python3
"""
Script helper para ejecutar la aplicación web RMR14
"""

import subprocess
import sys
import os

def check_requirements():
    """Verificar que las dependencias estén instaladas"""
    try:
        import streamlit
        import plotly
        return True
    except ImportError as e:
        print(f"❌ Error: Faltan dependencias - {e}")
        print("📝 Ejecuta: pip install -r requirements.txt")
        return False

def check_data():
    """Verificar que existan los datos de ejemplo"""
    data_path = "data/consolidated_data.csv"
    if not os.path.exists(data_path):
        print(f"⚠️  Advertencia: No se encontró {data_path}")
        print("📝 La app funcionará pero requerirá cargar datos manualmente")
        return False
    return True

def main():
    print("🏔️  RMR14 Web App - Iniciando...")
    print("=" * 50)
    
    # Verificaciones
    if not check_requirements():
        sys.exit(1)
    
    has_data = check_data()
    
    print(f"✅ Dependencias: OK")
    print(f"{'✅' if has_data else '⚠️ '} Datos: {'OK' if has_data else 'Faltantes'}")
    print()
    print("🚀 Iniciando Streamlit...")
    print("📱 La app se abrirá en: http://localhost:8501")
    print("🛑 Para detener: Ctrl+C")
    print("=" * 50)
    
    # Ejecutar Streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 App detenida por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 