import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="POA 2026",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Bienvenido al Cronograma POA 2026")

# Descripción de la aplicación
st.markdown("""
Esta aplicación permite cargar, editar y visualizar cronogramas de actividades con base en días hábiles y dependencias.

Usa el menú lateral para navegar entre las siguientes secciones:

- ✏️ **Editor de Cronograma**: Carga y edita tu archivo CSV con las tareas.
- 📈 **Gráfico Gantt**: Visualiza el cronograma en un diagrama de Gantt.
- 📊 **Resumen de Avances**: Consulta el progreso de cada tarea.
- 📥 **Exportar Cronograma**: Descarga el cronograma editado como archivo CSV.
""")
