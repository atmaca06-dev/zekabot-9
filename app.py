from flask import Flask, request
import os
import openai
from twilio.rest import Client

app = Flask(__name__)

# OpenAI istemcisi
client_oai = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Twilio istemcisi
twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_number = os.environ.get("TWILIO_NUMBER")
client_twilio = Client(twilio_sid, twilio_token)

@app.route("/", methods=["GET"])
def index():
    return "Zekabot GPT-4o görsel destekli aktif ✅"

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")
    num_media = int(request.values.get("NumMedia", 0))

    messages = []

    if incoming_msg:
        messages.append({"type": "text", "text": incoming_msg})

    if num_media > 0:
        media_url = request.values.get("MediaUrl0")
        if media_url:
            messages.append({
                "type": "image_url",
                "image_url": {"url": media_url}
            })

    if not messages:
        return "Boş mesaj", 400

    try:
        response = client_oai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": messages}
            ],
            max_tokens=500
        )
        reply = response.choices[0].message.content.strip()
    except Exception as e:
        reply = f"GPT-4o hatası: {str(e)}"

    try:
        client_twilio.messages.create(
            body=reply,
            from_=twilio_number,
            to=from_number
        )
    except Exception as e:
        return f"Twilio hatası: {str(e)}", 500

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
