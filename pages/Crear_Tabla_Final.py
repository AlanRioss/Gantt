import streamlit as st
import pandas as pd

st.title("Crear tabla final y descargar")

# Crear tabla final combinando tablas existentes
if "tabla" in st.session_state and "tabla_extra" in st.session_state:
    tabla_final = pd.concat([st.session_state.tabla, st.session_state.tabla_extra], ignore_index=True)
    st.write(tabla_final)

    # Botón de descarga
    @st.cache_data
    def convertir_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convertir_csv(tabla_final)
    st.download_button(
        label="Descargar tabla final como CSV",
        data=csv,
        file_name="tabla_final.csv",
        mime="text/csv"
    )
else:
    st.warning("Primero debes ingresar datos en las tablas.")
