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

        with open("temp_rnt.pdf", "wb") as f:
            f.write(uploaded_file.read())

        detalle_mensual, resumen_anual, paginas_con_error = extraer_bases_rnt("temp_rnt.pdf")

        if not resumen_anual:
            st.warning("No se han encontrado registros.")
        else:

            df_resumen = pd.DataFrame(resumen_anual)
            df_detalle = pd.DataFrame(detalle_mensual)

            # 🔎 Mostrar páginas con problemas de lectura
            if paginas_con_error:
                st.error(
                    f"⚠️ No se pudieron leer correctamente las páginas: {paginas_con_error}"
                )

            # 🔎 NUEVO: Detectar meses faltantes
            if not df_detalle.empty:
                meses_detectados = sorted(df_detalle["Mes"].unique())
                meses_esperados = list(range(1, 13))
                meses_faltantes = [m for m in meses_esperados if m not in meses_detectados]

                if meses_faltantes:
                    st.error(
                        f"⚠️ Faltan meses en el PDF: {meses_faltantes}. "
                        f"Puede haber páginas no legibles o mal formateadas."
                    )

            st.success(f"Se han detectado {len(df_resumen)} trabajadores")

            # =========================
            # MÉTRICAS GENERALES
            # =========================

            col1, col2, col3 = st.columns(3)

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

            with col3:
                st.metric(
                    "Solidaridad Total Anual",
                    f"{df_resumen['Base_Solidaridad_Anual'].sum():,.2f} €"
                )

            st.markdown("---")

            # =========================
            # RESUMEN ANUAL COMPLETO
            # =========================

            st.subheader("📊 Resumen Anual por Trabajador")
            st.dataframe(df_resumen, width="stretch")

            st.markdown("---")

            # =========================
            # DETALLE MENSUAL COMPLETO
            # =========================

            st.subheader("📅 Detalle Mensual")
            st.dataframe(
                df_detalle.sort_values(["DNI", "Año", "Mes"]),
                width="stretch"
            )

            st.markdown("---")

            # =========================================================
            # 🔎 FILTRO POR DNI
            # =========================================================

            st.subheader("🎯 Filtrar por DNI")

            lista_dnis = sorted(df_resumen["DNI"].unique())

            dnis_seleccionados = st.multiselect(
                "Selecciona uno o varios DNIs:",
                options=lista_dnis
            )

            if dnis_seleccionados:
                df_resumen_filtrado = df_resumen[df_resumen["DNI"].isin(dnis_seleccionados)]
                df_detalle_filtrado = df_detalle[df_detalle["DNI"].isin(dnis_seleccionados)]
            else:
                df_resumen_filtrado = df_resumen
                df_detalle_filtrado = df_detalle

            st.markdown("### 📌 Resumen Anual Filtrado")
            st.dataframe(df_resumen_filtrado, width="stretch")

            st.markdown("### 📌 Detalle Mensual Filtrado")
            st.dataframe(
                df_detalle_filtrado.sort_values(["DNI", "Año", "Mes"]),
                width="stretch"
            )

            # =========================
            # EXPORTAR EXCEL COMPLETO
            # =========================

            def convertir_excel(df_res, df_det):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df_res.to_excel(writer, index=False, sheet_name="Resumen_Anual")
                    df_det.to_excel(writer, index=False, sheet_name="Detalle_Mensual")
                return output.getvalue()

            excel_completo = convertir_excel(df_resumen, df_detalle)

            st.download_button(
                label="📥 Descargar Excel Completo",
                data=excel_completo,
                file_name="resultado_rnt_completo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # =========================
            # EXPORTAR EXCEL FILTRADO
            # =========================

            excel_filtrado = convertir_excel(df_resumen_filtrado, df_detalle_filtrado)

            st.download_button(
                label="📥 Descargar Excel Filtrado",
                data=excel_filtrado,
                file_name="resultado_rnt_filtrado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )