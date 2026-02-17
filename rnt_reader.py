import pdfplumber
import re
import unicodedata
import pytesseract
from pdf2image import convert_from_path
from collections import defaultdict


def _parse_importe(s: str) -> float:
    return float(s.replace(".", "").replace(",", "."))


def _extraer_importe_en_linea_o_siguiente(lineas, i, max_offset=3):

    # 1) misma línea
    m = re.search(r"([\d]{1,3}(?:\.[\d]{3})*,[\d]{2})\s*$", lineas[i])
    if m:
        return _parse_importe(m.group(1))

    # 2) siguientes líneas solo si es importe puro
    for offset in range(1, max_offset + 1):
        if i + offset >= len(lineas):
            break
        candidata = lineas[i + offset].strip()

        if re.fullmatch(r"[\d]{1,3}(?:\.[\d]{3})*,[\d]{2}", candidata):
            return _parse_importe(candidata)

    return None


def _extraer_texto_con_ocr(pdf_path, page_number):

    images = convert_from_path(
        pdf_path,
        first_page=page_number + 1,
        last_page=page_number + 1
    )

    texto = pytesseract.image_to_string(images[0], lang="spa")
    return texto


def extraer_bases_rnt(pdf_path, debug_dni=None):

    # 🔹 Estructura mensual
    detalle = defaultdict(lambda: {"Base_CC": 0.0, "Base_AT": 0.0})

    trabajador_actual = None
    mes_actual = None
    año_actual = None

    with pdfplumber.open(pdf_path) as pdf:
        for num_pagina, pagina in enumerate(pdf.pages):

            texto = pagina.extract_text()

            # OCR si es página escaneada
            if not texto or "(cid:" in texto or texto.count("") > 3:
                print(f"⚠️ Usando OCR en página {num_pagina + 1}")
                texto = _extraer_texto_con_ocr(pdf_path, num_pagina)

            if not texto:
                continue

            # 🔎 Detectar periodo (ej: 10/2024-10/2024)
            match_periodo = re.search(r"Periodo de liquidación\s+(\d{2})/(\d{4})", texto)
            if match_periodo:
                mes_actual = match_periodo.group(1)
                año_actual = match_periodo.group(2)

            lineas = texto.split("\n")

            for i, linea in enumerate(lineas):

                # Limpieza caracteres
                linea = unicodedata.normalize("NFKD", linea)
                linea = linea.encode("ascii", "ignore").decode()

                # Detectar trabajador
                match_trabajador = re.match(r"(\d{11,12})\s+(\d{9,10}[A-Z])", linea)
                if match_trabajador:
                    trabajador_actual = match_trabajador.group(2)

                if not trabajador_actual or not mes_actual:
                    continue

                # Ignorar totales
                if "SUMA DE BASES" in linea:
                    trabajador_actual = None
                    continue

                clave = (trabajador_actual, año_actual, mes_actual)

                # =========================
                # BASE CC
                # =========================
                if "BASE DE CONTINGENCIAS COMUNES" in linea:
                    valor = _extraer_importe_en_linea_o_siguiente(lineas, i)

                    if valor is not None:
                        detalle[clave]["Base_CC"] += valor
                        if debug_dni == trabajador_actual:
                            print("CC capturada:", valor)

                # =========================
                # BASE AT
                # =========================
                if "BASE DE ACCIDENTES DE TRABAJO" in linea:
                    valor = _extraer_importe_en_linea_o_siguiente(lineas, i)

                    if valor is not None:
                        detalle[clave]["Base_AT"] += valor
                        if debug_dni == trabajador_actual:
                            print("AT capturada:", valor)

    # =========================
    # GENERAR DETALLE MENSUAL
    # =========================

    detalle_mensual = []
    for (dni, año, mes), valores in detalle.items():
        detalle_mensual.append({
            "DNI": dni,
            "Año": int(año),
            "Mes": int(mes),
            "Base_CC": round(valores["Base_CC"], 2),
            "Base_AT": round(valores["Base_AT"], 2)
        })

    # =========================
    # GENERAR RESUMEN ANUAL
    # =========================

    resumen = defaultdict(lambda: {"Base_CC": 0.0, "Base_AT": 0.0})

    for item in detalle_mensual:
        clave = (item["DNI"], item["Año"])
        resumen[clave]["Base_CC"] += item["Base_CC"]
        resumen[clave]["Base_AT"] += item["Base_AT"]

    resumen_anual = []
    for (dni, año), valores in resumen.items():
        resumen_anual.append({
            "DNI": dni,
            "Año": año,
            "Base_CC_Anual": round(valores["Base_CC"], 2),
            "Base_AT_Anual": round(valores["Base_AT"], 2)
        })

    return detalle_mensual, resumen_anual