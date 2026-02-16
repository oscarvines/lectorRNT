import pdfplumber
import re
from collections import defaultdict

def extraer_bases_rnt(pdf_path):

    resultados = defaultdict(lambda: {"Base_CC": 0.0, "Base_AT": 0.0})

    with pdfplumber.open(pdf_path) as pdf:
        texto_completo = ""

        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                texto_completo += texto + "\n"

    # Detectar bloques por trabajador
    patron_trabajador = re.findall(
        r"(\d{11,12})\s+(\d{10}[A-Z]).*?BASE DE CONTINGENCIAS COMUNES\s+([\d.,]+).*?BASE DE ACCIDENTES DE TRABAJO\s+([\d.,]+)",
        texto_completo,
        re.DOTALL
    )

    for naf, dni, base_cc, base_at in patron_trabajador:

        base_cc = float(base_cc.replace(".", "").replace(",", "."))
        base_at = float(base_at.replace(".", "").replace(",", "."))

        clave = dni

        resultados[clave]["Base_CC"] += base_cc
        resultados[clave]["Base_AT"] += base_at

    # Convertimos a lista
    salida = []
    for dni, datos in resultados.items():
        salida.append({
            "DNI": dni,
            "Base_CC_Total": round(datos["Base_CC"], 2),
            "Base_AT_Total": round(datos["Base_AT"], 2)
        })

    return salida