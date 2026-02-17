import pdfplumber

def dump_pdfplumber(pdf_path, output_txt):

    texto_total = ""

    with pdfplumber.open(pdf_path) as pdf:
        for i, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text()
            texto_total += f"\n\n===== PÁGINA {i} =====\n\n"
            if texto:
                texto_total += texto

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(texto_total)

    print("TXT generado:", output_txt)


if __name__ == "__main__":
    dump_pdfplumber("RNT2024.pdf", "RNT2024_plumber.txt")