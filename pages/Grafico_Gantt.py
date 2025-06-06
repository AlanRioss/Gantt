import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import streamlit.components.v1 as components
import os

st.title("📈 Gráfico Gantt")

processed_df = st.session_state['processed_df']

    # 10 Crear el Gantt

# Crear un filtro para seleccionar las etapas a mostrar
etapas_filtradas = st.multiselect(
    "Selecciona las etapas a mostrar",
    options=processed_df["Etapa"].unique(),
    default=processed_df["Etapa"].unique()
)


st.session_state['etapas_filtradas'] = etapas_filtradas


# Filtrar el DataFrame según las etapas seleccionadas
df_filtrado = processed_df[processed_df["Etapa"].isin(etapas_filtradas)]

# Crear botones de rango de tiempo
rangos = {
    "Todo": df_filtrado["Fin"].max(),
    "Próx 7 días": datetime.now() + pd.Timedelta(days=7),
    "Próx 14 días": datetime.now() + pd.Timedelta(days=14),
    "Próx mes": datetime.now() + pd.DateOffset(months=1)
}

# Seleccionar el rango de tiempo
rango_seleccionado = st.selectbox("Selecciona el rango de tiempo", list(rangos.keys()))

# Filtrar las tareas según el rango de tiempo seleccionado
if rango_seleccionado != "Todo":
    df_filtrado = df_filtrado[(df_filtrado["Inicio Actualizado"] <= rangos[rango_seleccionado]) & (df_filtrado["Fin"] >= datetime.now())]

# Determinar el rango del eje X
if rango_seleccionado == "Todo":
    rango_inicio = df_filtrado["Inicio Actualizado"].min()
else:
    rango_inicio = datetime.now()

# Definir un diccionario de colores personalizados
color_discrete_map = {
    "Planeación": "#186F65",
    "Programación y presupuestación": "#B5CB99",
    "Priorización": "#FCE09B",
    "Integración Final de Proyecto de Inversión 2026": "#B2533E"
}

# Crear el Gantt
fig = px.timeline(
    df_filtrado,
    x_start="Inicio Actualizado",
    x_end="Fin",
    y="Tarea con Icono",
    color="Etapa",
    color_discrete_map=color_discrete_map,
    category_orders={"Etapa": [
        "Planeación", 
        "Programación y presupuestación",
        "Priorización",
        "Integración Final de Proyecto de Inversión 2026"
    ]},
)

# Establecer el orden original de las tareas en el eje Y
fig.update_yaxes(categoryorder="array", categoryarray=df_filtrado.sort_values("Orden", ascending=False)["Tarea con Icono"].tolist())

# Agregar línea vertical para el día actual
fig.add_vline(x=datetime.now(), line_width=2, line_dash="dash", line_color="#99A98F")

# Agregar líneas anguladas y punteadas que conecten actividades con sus predecesoras
for i, row in df_filtrado.iterrows():
    if row['Predecesora']:
        pre_row = df_filtrado[df_filtrado['Tarea'] == row['Predecesora']]
        if not pre_row.empty:
            fig.add_trace(go.Scatter(
                x=[pre_row.iloc[0]['Fin'], pre_row.iloc[0]['Fin'], row['Inicio Actualizado']],
                y=[pre_row.iloc[0]['Tarea con Icono'], row['Tarea con Icono'], row['Tarea con Icono']],
                mode='lines',
                line=dict(color='#99A799', width=2, dash='dot'),
                showlegend=False
            ))

# Agregar hitos como estrellas sin mostrar en la leyenda
for i, row in df_filtrado.iterrows():
    if row["Tipo"] == "Hito":
        fig.add_trace(go.Scatter(
            x=[row["Inicio Actualizado"]],
            y=[row["Tarea con Icono"]],
            mode='markers',
            marker=dict(symbol='star', size=15, color='#D06224'),
            name=row["Tarea"],
            showlegend=False  # No mostrar en la leyenda
        ))

# Agregar líneas guía horizontales al nivel de cada tarea
fig.update_layout(
    height=800,  # Ajustar la altura de la gráfica
    xaxis=dict(
        range=[rango_inicio, rangos[rango_seleccionado]],  # Ajustar el rango del eje X
        showgrid=True,
        gridcolor='#E5DCC3',
        gridwidth=1,
        type="date"
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='#E5DCC3',
        gridwidth=1
    )
)

# Agregar marcadores para el avance en el punto correspondiente al progreso
for i, row in df_filtrado.iterrows():
    if row["Tipo"] != "Hito":
        progress_point = row["Inicio Actualizado"] + (row["Fin"] - row["Inicio Actualizado"]) * (row["Avance (%)"] / 100)
        fig.add_trace(go.Scatter(
            x=[progress_point],
            y=[row["Tarea con Icono"]],
            mode='markers+text',
            marker=dict(symbol='arrow-bar-right', size=10, color='#506D84'),
            text=[f"{row['Avance (%)']}%    "],
            textposition="middle left",
            showlegend=False  # No mostrar en la leyenda
        ))

# Mostrar el gráfico
st.plotly_chart(fig, use_container_width=True)

