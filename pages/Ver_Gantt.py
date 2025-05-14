import streamlit as st
import plotly.express as px
import pandas as pd

st.title("Visualización Gantt")

if "tabla" in st.session_state:
    df = st.session_state.tabla.copy()
    df["Inicio"] = pd.to_datetime(df["Inicio"])
    df["Fin"] = pd.to_datetime(df["Fin"])

    fig = px.timeline(df, x_start="Inicio", x_end="Fin", y="Tarea", title="Diagrama de Gantt")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Primero debes ingresar datos en la tabla.")
