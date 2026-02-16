import pdfplumber

def guardar_texto_pdf_en_txt(pdf_path, output_txt_path):
    with pdfplumber.open(pdf_path) as pdf:
        texto = ""
        for i, page in enumerate(pdf.pages, start=1):
            texto += f"\n\n===== PÁGINA {i} =====\n\n"
            texto += (page.extract_text() or "") + "\n"

    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(texto)

    print("TXT generado correctamente en:", output_txt_path)


if __name__ == "__main__":
    pdf_path = "RNT2024.pdf"
    output_txt_path = "rnt_extraido.txt"

    guardar_texto_pdf_en_txt(pdf_path, output_txt_path)