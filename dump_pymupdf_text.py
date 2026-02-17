import fitz

def volcar_pdf_a_txt(pdf_path, output_txt):

    doc = fitz.open(pdf_path)

    texto_total = ""

    for num_pagina, pagina in enumerate(doc, start=1):
        texto = pagina.get_text("text")

        texto_total += f"\n\n================ PÁGINA {num_pagina} ================\n\n"
        texto_total += texto

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(texto_total)

    print(f"TXT generado en: {output_txt}")


if __name__ == "__main__":
    volcar_pdf_a_txt("RNT2024.pdf", "RNT2024_pymupdf.txt")