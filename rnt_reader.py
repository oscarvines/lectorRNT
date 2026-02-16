import pdfplumber
import re
from collections import defaultdict


def _parse_importe(s: str) -> float:
    return float(s.replace(".", "").replace(",", "."))


def _extraer_importe_en_linea_o_siguiente(lineas, i, max_offset=3):
    """
    1) Intenta extraer el importe al final de la misma línea.
    2) Si no está, mira hasta max_offset líneas siguientes PERO solo si la línea es "solo un número".
       (Evita capturar importes de otras filas como fechas, SUMA DE BASES, etc.)
    """
    # 1) misma línea
    m = re.search(r"([\d]{1,3}(?:\.[\d]{3})*,[\d]{2})\s*$", lineas[i])
    if m:
        return _parse_importe(m.group(1))

    # 2) siguientes líneas, solo si es una línea numérica pura
    for offset in range(1, max_offset + 1):
        if i + offset >= len(lineas):
            break
        candidata = lineas[i + offset].strip()

        # si la línea es SOLO un importe (ej: "1.374,83")
        if re.fullmatch(r"[\d]{1,3}(?:\.[\d]{3})*,[\d]{2}", candidata):
            return _parse_importe(candidata)

    return None


def extraer_bases_rnt(pdf_path, debug_dni=None):

    resultados = defaultdict(lambda: {"Base_CC": 0.0, "Base_AT": 0.0})
    trabajador_actual = None

    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if not texto:
                continue

            lineas = texto.split("\n")

            for i, linea in enumerate(lineas):

                # Detectar inicio de trabajador (NAF + DNI)
                match_trabajador = re.match(r"(\d{11,12})\s+(\d{9,10}[A-Z])", linea)
                if match_trabajador:
                    trabajador_actual = match_trabajador.group(2)
                    # OJO: NO hacemos continue, porque esta misma línea puede contener la BASE CC

                if not trabajador_actual:
                    continue

                # Ignorar totales
                if "SUMA DE BASES" in linea:
                    trabajador_actual = None
                    continue

                # =========================
                # BASE CC
                # =========================
                if "BASE DE CONTINGENCIAS COMUNES" in linea:
                    valor = _extraer_importe_en_linea_o_siguiente(lineas, i, max_offset=3)

                    if valor is not None:
                        resultados[trabajador_actual]["Base_CC"] += valor
                        if debug_dni == trabajador_actual:
                            print("CC capturada:", valor)

                # =========================
                # BASE AT
                # =========================
                if "BASE DE ACCIDENTES DE TRABAJO" in linea:
                    valor = _extraer_importe_en_linea_o_siguiente(lineas, i, max_offset=3)

                    if valor is not None:
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