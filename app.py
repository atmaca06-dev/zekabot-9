from flask import Flask, request
import os
import openai
from twilio.rest import Client

app = Flask(__name__)

# OpenAI ayarları
client_oai = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Twilio ayarları
twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_number = os.environ.get("TWILIO_NUMBER")
client_twilio = Client(twilio_sid, twilio_token)

@app.route("/", methods=["GET"])
def index():
    return "Zekabot GPT-4o güncellendi ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")

    if not incoming_msg:
        return "Boş mesaj", 400

    # GPT-4o çağrısı
    try:
        completion = client_oai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": incoming_msg}],
            max_tokens=500,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content.strip()
    except Exception as e:
        reply = f"Hata: {str(e)}"

    # Yanıtı geri gönder
    try:
        client_twilio.messages.create(
            body=reply,
            from_=twilio_number,
            to=from_number
        )
    except Exception as e:
        return f"Twilio gönderim hatası: {str(e)}", 500

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
