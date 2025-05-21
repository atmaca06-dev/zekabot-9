from flask import Flask, request
import os
from openai import OpenAI
from twilio.rest import Client

app = Flask(__name__)

# OpenAI ve Twilio ayarları
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
twilio_client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))
twilio_number = os.environ.get("TWILIO_NUMBER")

@app.route("/", methods=["GET"])
def home():
    return "Zekabot V1 aktif"

@app.route("/webhook", methods=["POST"])
def webhook():
    msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    # Komutları kontrol et
    if msg.upper().startswith("KOD:"):
        # Burada kod testi/fix modülü çağırabilirsin
        yanit = "Kod test/düzeltme modülü çalıştı (buraya detay eklenir)."
    elif msg.upper().startswith("DÜZELT:"):
        yanit = "Kod düzeltme modülü çalıştı (buraya detay eklenir)."
    elif msg.upper().startswith("SCRAPE:"):
        yanit = "Web scraping modülü çalıştı (buraya detay eklenir)."
    elif msg.upper().startswith("GİRİŞ:"):
        yanit = "Giriş/form modülü çalıştı (buraya detay eklenir)."
    else:
        # Komut yoksa mesajı GPT-4o'ya sor
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sen kibar, yardımcı bir WhatsApp asistanısın."},
                {"role": "user", "content": msg}
            ],
            max_tokens=250,
        )
        yanit = response.choices[0].message.content.strip()

    # Yanıtı Twilio ile kullanıcıya gönder
    twilio_client.messages.create(
        from_=twilio_number,
        to=sender,
        body=yanit
    )
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

