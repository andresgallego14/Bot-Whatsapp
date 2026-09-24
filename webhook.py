import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Tus credenciales configuradas
VERIFY_TOKEN = "satrack_bot_token_2026"
PHONE_NUMBER_ID = "1276025325598759"
WHATSAPP_TOKEN = "EAATgAPck5N4BSUg2HaUxFAQwnx9ro4j8FSgpFPmxgDTfwZCOZAHHgmRPq0LyZANIBuZCIpTm9JZBkV8Kv2rUrksFRg2sy8ZC0Xyg53DClU4nyNiVQ4UCSMpcCaKWTqrk8tFj6Tr3QVMJpSVnxYH52IsSHlRZBx0ZCrDZCGw5V9hgjiIX5Yes9mWJWWQp0LZAfrFUIedMr1LzTBrokTJZAvLcszAOODOZA6ZAtV0zxBI17KcvQjYXn4juXazKBtNFpxsukC5LKhe6gVgNOkNvxnZBgmn6nv"

@app.route('/', methods=['GET'])
def home():
    return "Servidor activo y escuchando en /webhook", 200

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Validación del Webhook por parte de Meta
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Token de verificación inválido", 403

    elif request.method == 'POST':
        # Recepción de mensajes entrantes
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
                
                # CASO 1: El usuario envió un mensaje de texto
                if msg_type == 'text':
                    msg_body = message['text']['body']
                    print(f"Texto de {from_number}: {msg_body}")
                    enviar_respuesta(from_number, f"¡Hola! Recibí tu texto: '{msg_body}'.")

                # CASO 2: El usuario envió un documento (PDF, etc.)
                elif msg_type == 'document':
                    doc = message['document']
                    media_id = doc['id']
                    file_name = doc.get('filename', 'archivo.pdf')
                    mime_type = doc['mime_type']
                    
                    print(f"Documento recibido de {from_number}: {file_name} (Tipo: {mime_type})")

                    if 'pdf' in mime_type:
                        # Descargar y procesar el PDF
                        descargar_y_procesar_pdf(media_id, file_name, from_number)
                    else:
                        enviar_respuesta(from_number, "Recibí el archivo, pero por ahora solo proceso documentos PDF.")

        except Exception as e:
            print("Error procesando el mensaje:", e)

        return jsonify({"status": "success"}), 200

def descargar_y_procesar_pdf(media_id, file_name, from_number):
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    
    # 1. Obtener la URL de descarga del archivo desde la API de Meta
    url_meta = f"https://graph.facebook.com/v20.0/{media_id}"
    response = requests.get(url_meta, headers=headers)
    
    if response.status_code == 200:
        file_url = response.json().get("url")
        
        # 2. Descargar el archivo binario del PDF
        file_response = requests.get(file_url, headers=headers)
        if file_response.status_code == 200:
            local_path = f"/tmp/{file_name}"
            with open(local_path, "wb") as f:
                f.write(file_response.content)
            
            print(f"PDF descargado exitosamente en: {local_path}")
            enviar_respuesta(from_number, f"He recibido y descargado tu PDF '{file_name}' correctamente. Próximamente extraeré la placa y validaré el sistema.")
            
            # TODO: Aquí agregaremos la lógica para leer el PDF con pypdf y buscar la placa
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)