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

        # 🔹 NUEVA ESTRUCTURA
        detalle_mensual, resumen_anual = extraer_bases_rnt("temp_rnt.pdf")

        if not resumen_anual:
            st.warning("No se han encontrado registros.")
        else:

            df_resumen = pd.DataFrame(resumen_anual)
            df_detalle = pd.DataFrame(detalle_mensual)

            st.success(f"Se han detectado {len(df_resumen)} trabajadores")

            # =========================
            # MÉTRICAS GENERALES
            # =========================

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Base CC Total Anual",
                    f"{df_resumen['Base_CC_Anual'].sum():,.2f} €"
                )

            with col2:
                st.metric(
                    "Base AT Total Anual",
                    f"{df_resumen['Base_AT_Anual'].sum():,.2f} €"
                )

            st.markdown("---")

            # =========================
            # RESUMEN ANUAL
            # =========================

            st.subheader("📊 Resumen Anual por Trabajador")
            st.dataframe(df_resumen, width="stretch")

            st.markdown("---")

            # =========================
            # DETALLE MENSUAL
            # =========================

            st.subheader("📅 Detalle Mensual")
            st.dataframe(
                df_detalle.sort_values(["DNI", "Año", "Mes"]),
                width="stretch"
            )

            # =========================
            # EXPORTAR A EXCEL
            # =========================

            def convertir_excel(df_resumen, df_detalle):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df_resumen.to_excel(writer, index=False, sheet_name="Resumen_Anual")
                    df_detalle.to_excel(writer, index=False, sheet_name="Detalle_Mensual")
                return output.getvalue()

            excel_data = convertir_excel(df_resumen, df_detalle)

            st.download_button(
                label="📥 Descargar Excel Completo",
                data=excel_data,
                file_name="resultado_rnt_completo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )