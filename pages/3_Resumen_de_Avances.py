import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import streamlit.components.v1 as components
import os

st.title("📊 Resumen de Avances")

processed_df = st.session_state['processed_df']

# Verifica si los datos editados están disponibles
# 11 Mostrar la tabla extra

etapas_df = processed_df.groupby("Etapa").agg({
    "Inicio Actualizado": "min",
    "Fin": "max",
    "Avance (%)": "mean"
}).reset_index()

etapas_df.rename(columns={"Inicio Actualizado": "Inicio", "Avance (%)": "Avance"}, inplace=True)

# Ordenar las etapas según el orden especificado
orden_etapas = ["Planeación", "Programación y presupuestación", "Priorización", "Integración Final de Proyecto de Inversión 2026"]
etapas_df["Orden"] = etapas_df["Etapa"].apply(lambda x: orden_etapas.index(x))
etapas_df = etapas_df.sort_values("Orden").drop(columns=["Orden"])

# Formatear las fechas para presentación
etapas_df["Inicio"] = etapas_df["Inicio"].dt.strftime("%d/%m/%Y")
etapas_df["Fin"] = etapas_df["Fin"].dt.strftime("%d/%m/%Y")

# Mostrar la tabla extra

st.dataframe(etapas_df)



#Gráfica de Avance Programado
#st.header("Avance Programado vs Avance Real")


# Calcular los campos Avance Ponderado y Avance Programado Ponderado
processed_df["Avance Ponderado (%)"] = (processed_df["Avance (%)"] * processed_df["Ponderación (%)"]) / 100
processed_df["Avance Programado Ponderado (%)"] = (processed_df["Avance Programado (%)"] * processed_df["Ponderación (%)"]) / 100

# Filtrar las tareas que ya han comenzado
tareas_comenzadas = processed_df[processed_df["Avance Programado (%)"] > 0]

# Ordenar las tareas por fecha de inicio actualizado
tareas_comenzadas = tareas_comenzadas.sort_values("Inicio Actualizado")

# Calcular los valores acumulativos
tareas_comenzadas["Avance Ponderado Acumulativo (%)"] = tareas_comenzadas["Avance Ponderado (%)"].cumsum()
tareas_comenzadas["Avance Programado Ponderado Acumulativo (%)"] = tareas_comenzadas["Avance Programado Ponderado (%)"].cumsum()

# Crear la gráfica de líneas para el avance programado y el avance ponderado acumulativo
fig_line = go.Figure()

# Agregar el avance programado ponderado acumulativo a la gráfica
fig_line.add_trace(go.Scatter(
    x=tareas_comenzadas["Inicio Actualizado"].dt.strftime("%d/%m/%Y"),
    y=tareas_comenzadas["Avance Programado Ponderado Acumulativo (%)"],
    mode='lines+markers+text',
    name='Avance Programado',
    line=dict(color='#314E52'),
    text=tareas_comenzadas["Avance Programado Ponderado Acumulativo (%)"].round(2).astype(str) + '%',
    textposition='top center'

))

# Agregar el avance ponderado acumulativo a la gráfica
fig_line.add_trace(go.Scatter(
    x=tareas_comenzadas["Inicio Actualizado"].dt.strftime("%d/%m/%Y"),
    y=tareas_comenzadas["Avance Ponderado Acumulativo (%)"],
    mode='lines+markers+text',
    name='Avance Real',
    line=dict(color='#F2A154'),
    text=tareas_comenzadas["Avance Ponderado Acumulativo (%)"].round(2).astype(str) + '%',
    textposition='bottom center'

))

# Configurar la gráfica
fig_line.update_layout(
    title="Avance Programado vs Avance Real",
    xaxis_title="Fecha",
    yaxis_title="Avance (%)",
    xaxis=dict(showgrid=True, gridcolor='#D8D2C2', gridwidth=1),
    yaxis=dict(showgrid=True, gridcolor='#D8D2C2', gridwidth=1)
)

# Mostrar la gráfica
st.plotly_chart(fig_line, use_container_width=True)
