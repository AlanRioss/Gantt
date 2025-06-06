import streamlit as st
import pandas as pd
import os

from io import BytesIO

st.title("✏️ Editor de Cronograma")



uploaded_file = st.file_uploader("Selecciona un archivo Excel", type="xlsx")

# 1 Definir días festivos seleccionables

festivos_predeterminados = ["01/05/2025","16/09/2025","25/12/2025","24/06/2025","25/07/2025","28/07/2025","29/07/2025","30/07/2025","31/07/2025","01/08/2025"]
options=pd.date_range("2025-01-01", "2025-12-31").strftime("%d/%m/%Y")
dias_festivos = st.multiselect("Selecciona días festivos", options=options, default=festivos_predeterminados)
dias_festivos = pd.to_datetime(dias_festivos, format="%d/%m/%Y")


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



st.subheader("💾 Guardar y aplicar cambios")

# Entrada para el nombre del archivo
nombre_archivo = st.text_input("Nombre del archivo Excel:", value="datos_proyecto.xlsx")

# Botón para generar y descargar

if st.button("Guardar"):
    campos_a_guardar = ["Etapa", "Tarea", "Tipo", "Inicio", "Duración (días)", "Predecesora", "Bloquear inicio", "Avance (%)"]
    df_a_guardar = processed_df[campos_a_guardar]

# Crear archivo Excel en memoria
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
         df_a_guardar.to_excel(writer, index=False)
    buffer.seek(0)

    # Mostrar botón de descarga
    st.download_button(
        label="📥 Descargar archivo Excel",
        data=buffer,
        file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# Guardar en sesión
    st.session_state['df'] = df
    st.session_state['processed_df'] = processed_df
    st.success("Datos editados guardados en la sesión.")
