from flask import Flask, request, jsonify

app = Flask(__name__)

# Token de verificación que usaremos para validar con Meta
VERIFY_TOKEN = "satrack_bot_token_2026"

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    # Meta hace una petición GET para validar la URL
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if token == VERIFY_TOKEN:
        return challenge, 200
    return "Token de verificación inválido", 403

@app.route("/webhook", methods=["POST"])
def recibir_mensaje():
    # Meta envía los mensajes entrantes vía POST
    datos = request.get_json()
    print("\n--- NUEVO MENSAJE RECIBIDO DE WHATSAPP ---")
    print(datos)
    print("------------------------------------------\n")
    return jsonify({"status": "exito"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)