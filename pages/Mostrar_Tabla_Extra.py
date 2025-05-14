import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Mostrar tabla extra y gráfica de avance programado")

# Cargar o inicializar la tabla extra
if "tabla_extra" not in st.session_state:
    st.session_state.tabla_extra = pd.DataFrame({
        "Tarea": ["Tarea A", "Tarea B"],
        "Inicio": ["2025-06-01", "2025-06-05"],
        "Fin": ["2025-06-03", "2025-06-10"],
        "Avance": [50, 75]
    })

# Mostrar y editar la tabla extra
st.session_state.tabla_extra = st.data_editor(
    st.session_state.tabla_extra,
    num_rows="dynamic",
    use_container_width=True
)

# Mostrar gráfica de avance programado
if "tabla_extra" in st.session_state:
    df_extra = st.session_state.tabla_extra.copy()
    fig_avance = px.bar(df_extra, x="Tarea", y="Avance", title="Gráfica de Avance Programado")
    st.plotly_chart(fig_avance, use_container_width=True)
