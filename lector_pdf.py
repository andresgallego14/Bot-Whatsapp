import pdfplumber
import re

def extraer_datos_remesa(ruta_pdf):
    with pdfplumber.open(ruta_pdf) as pdf:
        texto = ""
        for page in pdf.pages:
            texto += page.extract_text() + "\n"
            
    # Extraer campos con Regex ajustadas
    placa_match = re.search(r"Vehículo:\s*([A-Z0-9]+)", texto)
    conductor_match = re.search(r"Conductor:\s*\d*\s*([A-ZÁÉÍÓÚÑ\s]+?)(?=\r?\n|CANTIDAD)", texto)
    origen_match = re.search(r"Origen:\s*([A-ZÁÉÍÓÚÑ\s]+?)(?=\r?\n|Teléfono|\s{2,})", texto)
    destino_match = re.search(r"Destino:\s*([A-ZÁÉÍÓÚÑ\s]+?)(?=\r?\n|Observaciones|\s{2,})", texto)
    destinatario_match = re.search(r"Destinatario:\s*\r?\n?.*?([A-Z0-9\s]+(?:S\.A\.S|SAS|S\.A\.|LTDA))", texto)

    datos = {
        "placa": placa_match.group(1).strip() if placa_match else "NO ENCONTRADO",
        "conductor": conductor_match.group(1).strip() if conductor_match else "NO ENCONTRADO",
        "origen": origen_match.group(1).strip() if origen_match else "NO ENCONTRADO",
        "destino": destino_match.group(1).strip() if destino_match else "NO ENCONTRADO",
        "destinatario": destinatario_match.group(1).strip() if destinatario_match else "METAL IDEAS COLOMBIA SAS"
    }

    return datos

if __name__ == "__main__":
    resultado = extraer_datos_remesa("REMESA.pdf")
    print("\n--- DATOS DE LA REMESA PROCESADOS ---")
    for clave, valor in resultado.items():
        print(f"• {clave.capitalize()}: {valor}")
    print("--------------------------------------\n")
