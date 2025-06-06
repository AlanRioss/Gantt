import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import streamlit.components.v1 as components
import os

st.title("📥 Exportar Cronograma")
processed_df = st.session_state['processed_df']


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

