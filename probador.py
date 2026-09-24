import re
from pypdf import PdfReader


def extraer_datos_remesa(texto):
    datos = {}

    # 1. PLACA: Busca la combinación de 3 letras y 3 números ANTES de "Vehículo:"
    match_placa = re.search(
        r"([A-Z]{3}\s*[-]?\s*\d{3}|[A-Z]{3}\s*[-]?\s*\d{2}[A-Z0-9])(?=\s*Veh[íi]culo:)",
        texto,
        re.IGNORECASE,
    )
    if not match_placa:
        match_placa = re.search(
            r"\b([A-Z]{3}\d{3}|[A-Z]{3}\d{2}[A-Z0-9])\b", texto
        )

    # 2. CONDUCTOR: Extrae el nombre que está ANTES de "Conductor:" (omite la cédula)
    match_conductor = re.search(
        r"(?:\d[\d\.\s]*)?([A-ZÁÉÍÓÚÑa-z\s]{4,40})(?=\s*Conductor:)", texto
    )

    # 3. ORIGEN: Captura la ciudad ubicada justo encima de "Destinatario:"
    match_origen = re.search(
        r"([A-ZÁÉÍÓÚÑ]{3,25})\s*[\r\n]+\s*Destinatario:", texto
    )

    # 4. DESTINO: Captura el texto después de "Destino:"
    match_destino = re.search(
        r"Destino:\s*([A-ZÁÉÍÓÚÑa-z\s]{3,25})", texto, re.IGNORECASE
    )

    # 5. DESTINATARIO: Extrae la empresa receptor (ej. PUBLI MASTER SJ S.A.S)
    match_destinatario = re.search(
        r"(?:\d{8,10}\s+)?([A-Z0-9ÁÉÍÓÚÑ\s\.\-&]{3,50}(?:S\.A\.S|SAS|S\.A\.|LTDA))",
        texto,
        re.IGNORECASE,
    )

    # Asignación y limpieza
    datos["vehiculo"] = (
        match_placa.group(1).upper().replace(" ", "").replace("-", "")
        if match_placa
        else "NO ENCONTRADO"
    )

    if match_conductor:
        nombre_cond = re.sub(r"\s+", " ", match_conductor.group(1)).strip()
        datos["conductor"] = nombre_cond if nombre_cond else "NO ENCONTRADO"
    else:
        datos["conductor"] = "NO ENCONTRADO"

    datos["origen"] = (
        match_origen.group(1).strip().upper() if match_origen else "NO ENCONTRADO"
    )
    datos["destino"] = (
        match_destino.group(1).split("\n")[0].strip().upper()
        if match_destino
        else "NO ENCONTRADO"
    )
    datos["destinatario"] = (
        re.sub(r"\s+", " ", match_destinatario.group(1)).strip().upper()
        if match_destinatario
        else "NO ENCONTRADO"
    )

    return datos


# Prueba local con el archivo
if __name__ == "__main__":
    reader = PdfReader("REMESA.pdf")
    texto_pdf = ""
    for page in reader.pages:
        texto_pdf += page.extract_text() + "\n"

    resultado = extraer_datos_remesa(texto_pdf)

    print("\n================ RESULTADO DE LA EXTRACCIÓN ================\n")
    for clave, valor in resultado.items():
        print(f"• {clave.capitalize()}: {valor}")
    print("\n===========================================================\n")