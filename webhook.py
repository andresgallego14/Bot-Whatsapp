import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Credenciales integradas
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
                msg_body = message['text']['body']
                
                print(f"De: {from_number} | Mensaje: {msg_body}")

                # Responder automáticamente al usuario
                enviar_respuesta(from_number, f"¡Hola! Recibí tu mensaje: '{msg_body}'. El bot está funcionando correctamente.")

        except Exception as e:
            print("Error procesando el mensaje:", e)

        return jsonify({"status": "success"}), 200

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