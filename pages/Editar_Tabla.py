import streamlit as st
import pandas as pd

st.title("Editar tabla de tareas")

# Cargar o inicializar la tabla
if "tabla" not in st.session_state:
    st.session_state.tabla = pd.DataFrame({
        "Tarea": ["Tarea 1", "Tarea 2"],
        "Inicio": ["2025-05-01", "2025-05-05"],
        "Fin": ["2025-05-03", "2025-05-10"]
    })

# Mostrar y editar la tabla
st.session_state.tabla = st.data_editor(
    st.session_state.tabla,
    num_rows="dynamic",
    use_container_width=True
)
