from rnt_reader import extraer_bases_rnt

datos = extraer_bases_rnt("RNT2024.pdf", debug_dni="1049843655X")

print("\nRESULTADO FINAL:\n")

for d in datos:
    if d["DNI"] == "1049843655X":
        print(d)