from flask import Flask, request
import openai
import os
from twilio.rest import Client

app = Flask(__name__)

# OpenAI ayarları
openai.api_key = os.environ.get("OPENAI_API_KEY")
model = "gpt-4o"

# Twilio ayarları
twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_number = os.environ.get("TWILIO_NUMBER")
client = Client(twilio_sid, twilio_token)

@app.route("/", methods=["GET"])
def index():
    return "Zekabot Webhook Aktif ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")

    if not incoming_msg:
        return "Boş mesaj", 400

    # GPT'den yanıt al
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": incoming_msg}],
            temperature=0.7,
            max_tokens=500
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"Hata: {str(e)}"

    # Cevabı WhatsApp üzerinden geri gönder
    client.messages.create(
        body=reply,
        from_=twilio_number,
        to=from_number
    )

   if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

