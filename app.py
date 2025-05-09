import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import streamlit.components.v1 as components


st.set_page_config(page_title="POA 2025", layout="wide")
st.title("📅 Cronograma POA 2026")

# 1 Definir días festivos seleccionables

festivos_predeterminados = ["01/01/2025", "01/05/2025", "16/09/2025", "25/12/2025"]
options=pd.date_range("2025-01-01", "2025-12-31").strftime("%d/%m/%Y")
dias_festivos = st.multiselect("Selecciona días festivos", options=options, default=festivos_predeterminados)
dias_festivos = pd.to_datetime(dias_festivos, format="%d/%m/%Y")



# 2 Datos de ejemplo
import os

uploaded_file = st.file_uploader("Selecciona un archivo Excel", type="xlsx")

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    df["Inicio"] = pd.to_datetime(df["Inicio"], format="%d/%m/%Y")
    # No convertir la columna 'Fin' ya que se calculará posteriormente
else:
    default_data = {
        "Tarea": ["1. Planeación", "2. Programación y presupuestación", "3. Priorización", "4. Integración Final de Proyecto de Inversión 2026", "Análisis", "Diseño", "Desarrollo", "Pruebas"],
        "Etapa": ["Planeación", "Programación y presupuestación", "Priorización", "Integración Final de Proyecto de Inversión 2026", "Planeación", "Planeación", "Planeación", "Planeación"],
        "Inicio": ["02/05/2025", "18/08/2025", "01/10/2025", "01/11/2025", "02/05/2025", "05/05/2025", "12/05/2025", "19/05/2025"],
        "Bloquear inicio": [False, False, False, False, False, False, True, False],
        "Predecesora": ["", "1. Planeación", "2. Programación y presupuestación", "3. Priorización", "", "Análisis", "Diseño", "Desarrollo"],
        "Avance (%)": [0, 0, 0, 0, 100, 75, 50, 25],
        "Duración (días)": [60, 44, 22, 49, 3, 5, 5, 5],
        "Tipo": ["Actividad", "Actividad", "Actividad", "Actividad", "Hito", "Actividad", "Actividad", "Actividad"]
    }
    df = pd.DataFrame(default_data)
    df["Inicio"] = pd.to_datetime(df["Inicio"], format="%d/%m/%Y")


# 3 Función para sumar solo días hábiles
def agregar_dias_habiles(fecha, dias):
    fecha = pd.to_datetime(fecha)  # Asegurar que es un objeto Timestamp
    while dias > 0:
        fecha = fecha + pd.Timedelta(days=1)
        if fecha.weekday() < 5 and fecha not in dias_festivos:
            dias -= 1
    return fecha


def calcular_duracion_habil(inicio, fin):
    inicio = pd.to_datetime(inicio, format="%d/%m/%Y")
    fin = pd.to_datetime(fin, format="%d/%m/%Y")
    duracion = 0
    while inicio <= fin:
        if inicio.weekday() < 5 and inicio not in dias_festivos:
            duracion += 1
        inicio += pd.Timedelta(days=1)
    return duracion


# 4 Cálculo inicial de fechas
df["Inicio Actualizado"] = df["Inicio"]
df["Fin"] = df.apply(lambda row: agregar_dias_habiles(row["Inicio Actualizado"], row["Duración (días)"] - 1), axis=1)

for i in range(len(df)):
    if df.loc[i, "Predecesora"]:
        predecesora = df[df["Tarea"] == df.loc[i, "Predecesora"]]
        if not predecesora.empty:
            if not df.loc[i, "Bloquear inicio"]:
                duracion_habil_predecesora = predecesora.iloc[0]["Duración (días)"]
                df.loc[i, "Inicio Actualizado"] = agregar_dias_habiles(predecesora.iloc[0]["Inicio Actualizado"], duracion_habil_predecesora)
            else:
                df.loc[i, "Inicio Actualizado"] = df.loc[i, "Inicio"]
        df.loc[i, "Fin"] = agregar_dias_habiles(df.loc[i, "Inicio Actualizado"], df.loc[i, "Duración (días)"] - 1)

df["Desfase (días)"] = (df["Inicio Actualizado"] - df["Inicio"]).dt.days


st.subheader("Editor de Cronograma")

# 5 Calculadora de Duración de Días

# Entradas de fecha de inicio y fecha final en una sola línea
col1, col2, col3 = st.columns(3)

with col1:
    fecha_inicio = st.date_input("Fecha de inicio")
with col2:
    fecha_final = st.date_input("Fecha final")

# Función para calcular la duración en días hábiles
def calcular_duracion_habil(fecha_inicio, fecha_final):
    fecha_inicio = pd.to_datetime(fecha_inicio, format="%d/%m/%Y")
    fecha_final = pd.to_datetime(fecha_final, format="%d/%m/%Y")
    duracion = 0
    while fecha_inicio <= fecha_final:
        if fecha_inicio.weekday() < 5 and fecha_inicio not in dias_festivos:
            duracion += 1
        fecha_inicio += pd.Timedelta(days=1)
    return duracion

# Mostrar la duración calculada en una columna adicional
with col3:
    if fecha_inicio and fecha_final:
        duracion = calcular_duracion_habil(fecha_inicio, fecha_final)
        st.write(f"Duración: {duracion} días")


# 6 Editor interactivo de la tabla

edited_df = st.data_editor(
    df[["Etapa", "Tarea", "Tipo", "Inicio", "Duración (días)", "Predecesora", "Bloquear inicio", "Avance (%)"]],
    column_config={
        "Etapa": st.column_config.SelectboxColumn("Etapa", options=[
            "Planeación", 
            "Programación y presupuestación", 
            "Priorización", 
            "Integración Final de Proyecto de Inversión 2026"
        ], required=True),
        "Tarea": st.column_config.TextColumn("Tarea"),
        "Tipo": st.column_config.SelectboxColumn("Tipo", options=["Hito", "Actividad"], required=True),
        "Inicio": st.column_config.DateColumn("Inicio"),
        "Duración (días)": st.column_config.NumberColumn("Duración (días)", min_value=1, step=1),
        "Predecesora": st.column_config.SelectboxColumn("Predecesora", options=df["Tarea"].tolist()),
        "Bloquear inicio": st.column_config.CheckboxColumn("Bloquear inicio"),
        "Avance (%)": st.column_config.NumberColumn("Avance (%)", min_value=0, max_value=100, step=1)
    },
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True
)

# 7 Actualización del DataFrame con los cambios realizados en el editor

from datetime import datetime

# Actualizar el DataFrame con los cambios realizados en el editor
processed_df = edited_df.copy()
processed_df["Inicio"] = pd.to_datetime(processed_df["Inicio"], format="%d/%m/%Y")
processed_df["Inicio Actualizado"] = processed_df["Inicio"]

# Ajustar la duración de los hitos primero
for i in range(len(processed_df)):
    if processed_df.loc[i, 'Tipo'] == 'Hito':
        processed_df.loc[i, 'Fin'] = processed_df.loc[i, 'Inicio Actualizado']
        processed_df.loc[i, 'Duración (días)'] = 1  # Asignar duración de 1 día para evitar división por cero

# Luego calcular el Inicio Actualizado
for i, row in processed_df.iterrows():
    predecesora = row["Predecesora"]
    bloquear = row["Bloquear inicio"]

    if predecesora:
        pre_row = processed_df[processed_df["Tarea"] == predecesora]
        if not pre_row.empty and not bloquear:
            duracion_habil_predecesora = pre_row.iloc[0]["Duración (días)"]
            processed_df.at[i, "Inicio Actualizado"] = agregar_dias_habiles(pre_row.iloc[0]["Inicio Actualizado"], duracion_habil_predecesora)
        else:
            processed_df.at[i, "Inicio Actualizado"] = row["Inicio"]
    else:
        processed_df.at[i, "Inicio Actualizado"] = row["Inicio"]

# Calcular el campo Fin basado en el Inicio Actualizado y la Duración
processed_df["Fin"] = processed_df.apply(lambda row: agregar_dias_habiles(row["Inicio Actualizado"], row["Duración (días)"] - 1), axis=1)

# Nueva columna para representar los días de avance completados
processed_df["Días Completados"] = (processed_df["Duración (días)"] * processed_df["Avance (%)"] / 100).astype(int)

# Nueva Sección: Calcular Avance Programado
def calcular_avance_programado(row):
    # Obtener la fecha actual
    fecha_actual = datetime.now()
    
    # Calcular días transcurridos considerando solo días hábiles
    dias_transcurridos = 0
    fecha_inicio = row["Inicio Actualizado"]
    
    while fecha_inicio <= fecha_actual:
        if fecha_inicio.weekday() < 5 and fecha_inicio not in dias_festivos:
            dias_transcurridos += 1
        fecha_inicio += pd.Timedelta(days=1)
    
    # Calcular el avance programado
    if row["Duración (días)"] > 0:
        avance_programado = (dias_transcurridos / row["Duración (días)"]) * 100
    else:
        avance_programado = 100  # Para hitos, el avance programado es 100%
    
    # Asegurarse de que el avance programado no sea mayor que 100%
    if avance_programado > 100:
        avance_programado = 100
    
    return avance_programado

# Aplicar el cálculo del avance programado al DataFrame procesado
processed_df["Avance Programado (%)"] = processed_df.apply(calcular_avance_programado, axis=1)

# Nueva Sección: Calcular Desviación
def calcular_desviacion(row):
    return row["Avance (%)"] - row["Avance Programado (%)"]

# Aplicar el cálculo de la desviación al DataFrame procesado
processed_df["Desviación (%)"] = processed_df.apply(calcular_desviacion, axis=1)

# Nueva Sección: Calcular Ponderación
def calcular_ponderacion(row, duracion_total_proyecto):
    return (row["Duración (días)"] / duracion_total_proyecto) * 100

# Calcular la duración total del proyecto
duracion_total_proyecto = processed_df["Duración (días)"].sum()

# Aplicar el cálculo de la ponderación al DataFrame procesado
processed_df["Ponderación (%)"] = processed_df.apply(lambda row: calcular_ponderacion(row, duracion_total_proyecto), axis=1)


# 8 Función para obtener icono de avance

def obtener_icono_avance(row):
    if row['Inicio Actualizado'] > datetime.now():
        return f"{row['Tarea']} ⏸️ "  # Stand by icono
    elif row['Avance (%)'] == 100:
        return f"{row['Tarea']} ✅ ({row['Avance (%)']}%)"  # Completado
    elif row['Fin'] < datetime.now() and row['Avance (%)'] < 100:
        return f"{row['Tarea']} 🔴 ({row['Avance (%)']}%)"  # Fecha de fin pasada y avance < 100%
    elif row['Desviación (%)'] >= 0:
        return f"{row['Tarea']} 🟢 ({row['Desviación (%)']}%)"  # Desviación positiva o cero
    else:
        return f"{row['Tarea']} 🟡 ({row['Desviación (%)']}%)"  # Desviación leve negativa

processed_df["Tarea con Icono"] = processed_df.apply(obtener_icono_avance, axis=1)




# Mantener el orden original de las tareas
processed_df["Orden"] = processed_df.index  # Crear un índice para mantener el orden



# 9 Botón para guardar y aplicar cambios

if st.button("Guardar y aplicar cambios"):
    # Seleccionar solo los campos que están en la tabla interactiva
    campos_a_guardar = ["Etapa", "Tarea", "Tipo", "Inicio", "Duración (días)", "Predecesora", "Bloquear inicio", "Avance (%)"]
    processed_df[campos_a_guardar].to_excel("C:/Users/DGCYSIPARIOSPU/mi_cronograma/datos_proyecto.xlsx", index=False)
    st.success("Datos guardados exitosamente.")

st.subheader("Gantt POA 2026")


# 10 Crear el Gantt

# 10 Crear el Gantt

# Crear un filtro para seleccionar las etapas a mostrar
etapas_filtradas = st.multiselect(
    "Selecciona las etapas a mostrar",
    options=processed_df["Etapa"].unique(),
    default=processed_df["Etapa"].unique()
)

# Filtrar el DataFrame según las etapas seleccionadas
df_filtrado = processed_df[processed_df["Etapa"].isin(etapas_filtradas)]

# Crear botones de rango de tiempo
rangos = {
    "Próx 7 días": datetime.now() + pd.Timedelta(days=7),
    "Próx 14 días": datetime.now() + pd.Timedelta(days=14),
    "Próx mes": datetime.now() + pd.DateOffset(months=1),
    "Todo": df_filtrado["Fin"].max()
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




st.subheader("Avances")

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



# 13 Crear tabla final y agregar botón de descarga

campos_finales = ["Etapa", "Tarea", "Tipo", "Inicio", "Inicio Actualizado", "Fin", "Duración (días)", "Predecesora", "Avance (%)", "Avance Programado (%)", "Desviación (%)", "Ponderación (%)"]

tabla_final = processed_df[campos_finales]
tabla_final["Inicio Actualizado"] = tabla_final["Inicio Actualizado"].dt.strftime("%d/%m/%Y")
tabla_final["Fin"] = tabla_final["Fin"].dt.strftime("%d/%m/%Y")

# Mostrar la tabla final con formato de presentación
tabla_final_presentacion = tabla_final.copy()
tabla_final_presentacion["Inicio Actualizado"] = pd.to_datetime(tabla_final_presentacion["Inicio Actualizado"], format="%d/%m/%Y").dt.strftime("%d/%b/%Y")
tabla_final_presentacion["Fin"] = pd.to_datetime(tabla_final_presentacion["Fin"], format="%d/%m/%Y").dt.strftime("%d/%b/%Y")

st.subheader("Cronograma POA 2026")
st.dataframe(tabla_final_presentacion)

# Agregar botón para descargar la tabla final
def convertir_df_a_excel(df):
    import io
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return buffer.getvalue()

if st.button("Descargar Tabla Final"):
    datos_excel = convertir_df_a_excel(tabla_final)
    st.download_button(
        label="Descargar Excel",
        data=datos_excel,
        file_name="tabla_final.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# Agregar botón para descargar la tabla final

# Mostrar la tabla final
#st.dataframe(processed_df)
