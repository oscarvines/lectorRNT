import streamlit as st
import pandas as pd
from rnt_reader import extraer_bases_rnt
from io import BytesIO

st.set_page_config(page_title="Lector RNT", layout="wide")

st.title("📄 Lector RNT – Bases de Cotización")

st.markdown("---")

uploaded_file = st.file_uploader("Sube el RNT en PDF", type=["pdf"])

if uploaded_file:

    with st.spinner("Procesando RNT..."):

        # Guardamos temporalmente el archivo
        with open("temp_rnt.pdf", "wb") as f:
            f.write(uploaded_file.read())

        datos = extraer_bases_rnt("temp_rnt.pdf")

        if not datos:
            st.warning("No se han encontrado registros.")
        else:

            df = pd.DataFrame(datos)

            st.success(f"Se han detectado {len(df)} trabajadores")

            # Métricas
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Base CC Total", f"{df['Base_CC_Total'].sum():,.2f} €")

            with col2:
                st.metric("Base AT Total", f"{df['Base_AT_Total'].sum():,.2f} €")

            st.markdown("## 📊 Resultados")
            st.dataframe(df, use_container_width=True)

            # Botón descarga Excel
            def convertir_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name="RNT")
                return output.getvalue()

            excel_data = convertir_excel(df)

            st.download_button(
                label="📥 Descargar Excel",
                data=excel_data,
                file_name="resultado_rnt.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )