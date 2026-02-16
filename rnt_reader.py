import pdfplumber
import re
from collections import defaultdict


def extraer_bases_rnt(pdf_path, debug_dni=None):

    resultados = defaultdict(lambda: {"Base_CC": 0.0, "Base_AT": 0.0})

    trabajador_actual = None

    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if not texto:
                continue

            lineas = texto.split("\n")

            for linea in lineas:

                # Detectar inicio de trabajador (NAF + DNI)
                match_trabajador = re.match(r"(\d{11,12})\s+(\d{9,10}[A-Z])", linea)
                if match_trabajador:
                    trabajador_actual = match_trabajador.group(2)
                    continue

                if not trabajador_actual:
                    continue

                # Ignorar totales
                if "SUMA DE BASES" in linea:
                    trabajador_actual = None
                    continue

                # BASE CC
                if "BASE DE CONTINGENCIAS COMUNES" in linea:
                    match_base = re.search(r"([\d.,]+)$", linea)
                    if match_base:
                        valor = float(match_base.group(1).replace(".", "").replace(",", "."))
                        resultados[trabajador_actual]["Base_CC"] += valor

                        if debug_dni == trabajador_actual:
                            print("CC capturada:", valor)

                # BASE AT
                if "BASE DE ACCIDENTES DE TRABAJO" in linea:
                    match_base = re.search(r"([\d.,]+)$", linea)
                    if match_base:
                        valor = float(match_base.group(1).replace(".", "").replace(",", "."))
                        resultados[trabajador_actual]["Base_AT"] += valor

                        if debug_dni == trabajador_actual:
                            print("AT capturada:", valor)

    salida = []

    for dni, datos in resultados.items():
        salida.append({
            "DNI": dni,
            "Base_CC_Total": round(datos["Base_CC"], 2),
            "Base_AT_Total": round(datos["Base_AT"], 2)
        })

    return salida