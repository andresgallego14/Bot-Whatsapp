import os
import requests
from flask import Flask, request, jsonify
from pypdf import PdfReader
import re 

app = Flask(__name__)

VERIFY_TOKEN = "satrack_bot_token_2026"
PHONE_NUMBER_ID = "1276025325598759"
WHATSAPP_TOKEN = "EAATgAPck5N4BSl0k2gBZCQHIDsK3cvtZAZB1s5CnEt6k56My4KkpzCZAh2yxZC2ZAi5Jh95CJdPL24cG0KjUb9vgVKU6T0w6pZCtV3sXsXIGf5qfgd6Q709qNPV3IcZA2dlL2KP8h4ZCcFcZAG6eyfyMLztsNkVQAQwpZCarvvWcPvildFwn3OCM9R1PL1RY4FbppT6thKJZAoVYeBvn1Lrsi2nHeccqHP94EaY8jPIHWpUoyAOCzqEUtxaEy20eExeH26ZBz2YR67VIkFWkHhbEYsHBWdmGd"

@app.route('/', methods=['GET'])
def home():
    return "Servidor activo y escuchando en /webhook", 200

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Token de verificación inválido", 403

    elif request.method == 'POST':
        data = request.get_json()
        print("Mensaje recibido:", data)

        try:
            entry = data['entry'][0]
            changes = entry['changes'][0]
            value = changes['value']
            
            if 'messages' in value:
                message = value['messages'][0]
                from_number = message['from']
                msg_type = message['type']
                
                if msg_type == 'text':
                    msg_body = message['text']['body']
                    print(f"Texto de {from_number}: {msg_body}")
                    enviar_respuesta(from_number, f"¡Hola! Recibí tu texto: '{msg_body}'.")

                elif msg_type == 'document':
                    doc = message['document']
                    media_id = doc['id']
                    file_name = doc.get('filename', 'archivo.pdf')
                    mime_type = doc['mime_type']
                    
                    print(f"Documento recibido de {from_number}: {file_name} (Tipo: {mime_type})")

                    if 'pdf' in mime_type:
                        descargar_y_procesar_pdf(media_id, file_name, from_number)
                    else:
                        enviar_respuesta(from_number, "Recibí el archivo, pero por ahora solo proceso documentos PDF.")

        except Exception as e:
            print("Error procesando el mensaje:", e)

        return jsonify({"status": "success"}), 200

def descargar_y_procesar_pdf(media_id, file_name, from_number):
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    
    url_meta = f"https://graph.facebook.com/v20.0/{media_id}"
    response = requests.get(url_meta, headers=headers)
    
    if response.status_code == 200:
        file_url = response.json().get("url")
        
        file_response = requests.get(file_url, headers=headers)
        if file_response.status_code == 200:
            local_path = f"/tmp/{file_name}"
            with open(local_path, "wb") as f:
                f.write(file_response.content)
            
            print(f"PDF descargado exitosamente en: {local_path}")
            enviar_respuesta(from_number, f"He recibido tu PDF '{file_name}'. Procesando la remesa...")
            
            texto_pdf = extraer_texto_pdf(local_path)
            if texto_pdf:
                info = extraer_datos_remesa(texto_pdf)
                
                mensaje_respuesta = (
                    f"📋 *Remesa procesada con éxito*\n\n"
                    f"🚗 *Placa:* {info['vehiculo']}\n"
                    f"👤 *Conductor:* {info['conductor']}\n"
                    f"📍 *Origen:* {info['origen']}\n"
                    f"🏁 *Destino:* {info['destino']}\n"
                    f"🏢 *Destinatario:* {info['destinatario']}"
                )
                enviar_respuesta(from_number, mensaje_respuesta)
            else:
                enviar_respuesta(from_number, "No pude extraer el texto del PDF.")
        else:
            print("Error al descargar el contenido binario del archivo.")
            enviar_respuesta(from_number, "Ocurrió un error al descargar tu archivo PDF.")
    else:
        print("Error al obtener la URL del medio en Meta.")
        enviar_respuesta(from_number, "No pude recuperar la información del archivo enviado.")

def enviar_respuesta(to_number, text_response):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text_response}
    }
    response = requests.post(url, json=payload, headers=headers)
    print("Respuesta enviada a Meta:", response.json())

def extraer_texto_pdf(ruta_archivo):
    try:
        lector = PdfReader(ruta_archivo)
        texto_completo = ""
        for pagina in lector.pages:
            texto_extraido = pagina.extract_text()
            if texto_extraido:
                texto_completo += texto_extraido + "\n"
        return texto_completo
    except Exception as e:
        print(f"Error leyendo el PDF: {e}")
        return None

def extraer_datos_remesa(texto):
    datos = {}

    # 1. PLACA: Exige OBLIGATORIAMENTE 3 letras al inicio (ej. KUF879, KUF-879, KUF 879)
    match_placa = re.search(
        r"\b([A-Z]{3}\s*[-]?\s*\d{3}|[A-Z]{3}\s*[-]?\s*\d{2}[A-Z0-9])\b",
        texto,
        re.IGNORECASE,
    )

    # 2. CONDUCTOR: Busca el campo e ignora la cédula si está antes del nombre
    match_conductor = re.search(
        r"Conductor[\s:]*(?:\d[\d\.\s]*)?([A-ZÁÉÍÓÚÑa-z\s]{4,35})",
        texto,
        re.IGNORECASE,
    )

    # 3. ORIGEN
    match_origen = re.search(
        r"Origen[\s:]*([A-ZÁÉÍÓÚÑa-z\s]{3,30})", texto, re.IGNORECASE
    )

    # 4. DESTINO
    match_destino = re.search(
        r"Destino[\s:]*([A-ZÁÉÍÓÚÑa-z\s]{3,30})", texto, re.IGNORECASE
    )

    # 5. DESTINATARIO
    match_destinatario = re.search(
        r"Destinatario[\s:]*([A-Z0-9ÁÉÍÓÚÑa-z\s\.\-&]{3,50})",
        texto,
        re.IGNORECASE,
    )

    # Limpiador inteligente para cortar etiquetas de casillas vecinas
    def limpiar_campo(match, es_placa=False):
        if not match:
            return "NO ENCONTRADO"

        if es_placa:
            return match.group(0).upper().replace(" ", "").replace("-", "")

        valor = match.group(1).split("\n")[0].strip()

        # Palabras de parada para que no se traslape con otras casillas
        palabras_parada = [
            "Coordenadas",
            "Latitud",
            "Longitud",
            "Dirección",
            "Direccion",
            "Teléfono",
            "Telefono",
            "Observaciones",
            "Manifiesto",
            "Pedido",
            "Fecha",
            "Remitente",
            "Cliente",
            "Agencia",
            "C.C",
            "CC",
            "Placa",
            "Vehículo",
            "Vehiculo",
            "CANTIDAD",
            "Marca",
            "Serial",
        ]

        for palabra in palabras_parada:
            pos = valor.find(palabra)
            if pos != -1:
                valor = valor[:pos]

        valor = valor.strip()
        return valor if len(valor) > 1 else "NO ENCONTRADO"

    datos["vehiculo"] = limpiar_campo(match_placa, es_placa=True)
    datos["conductor"] = limpiar_campo(match_conductor)
    datos["origen"] = limpiar_campo(match_origen)
    datos["destino"] = limpiar_campo(match_destino)
    datos["destinatario"] = limpiar_campo(match_destinatario)

    return datos

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)