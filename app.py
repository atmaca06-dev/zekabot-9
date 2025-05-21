from flask import Flask, request
import os
import requests
from base64 import b64encode
from twilio.rest import Client
from openai import OpenAI  # ✅ Yeni istemci

app = Flask(__name__)

# OpenAI istemcisi
client_oai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Twilio istemcisi
twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_number = os.environ.get("TWILIO_NUMBER")
client_twilio = Client(twilio_sid, twilio_token)

@app.route("/", methods=["GET"])
def index():
    return "Zekabot GPT-4o (görsel destekli) aktif ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")
    num_media = int(request.values.get("NumMedia", 0))

    messages = []

    if incoming_msg:
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": incoming_msg}]
        })

    # Görsel varsa ekle
    if num_media > 0:
        media_url = request.values.get("MediaUrl0")
        img_response = requests.get(media_url, auth=(twilio_sid, twilio_token))
        if img_response.status_code == 200:
            base64_img = b64encode(img_response.content).decode("utf-8")
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_img}"
                }
            })

    # GPT-4o çağrısı
    try:
        response = client_oai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"Hata: {str(e)}"

    client_twilio.messages.create(
        body=reply,
        from_=twilio_number,
        to=from_number
    )

    return "OK", 200
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
