import os
from flask import Flask, request
from openai import OpenAI
from twilio.rest import Client
from general_scraper import scrape_site
from code_tester import test_code
from code_fixer import fix_code
from login_bot import login_and_submit
from base64_helper import decode_base64_image

app = Flask(__name__)
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
twilio_client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))
twilio_number = os.environ.get("TWILIO_NUMBER")

@app.route("/", methods=["GET"])
def home():
    return "Zekabot V1 çalışıyor"

@app.route("/webhook", methods=["POST"])
def webhook():
    msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")
    reply = "Komut algılanamadı."

    try:
        if msg.startswith("KOD:"):
            reply = test_code(msg[4:])
        elif msg.startswith("DÜZELT:"):
            reply = fix_code(msg[7:], openai_client)
        elif msg.startswith("GİRİŞ:"):
            reply = login_and_submit(msg[6:])
        elif msg.startswith("SCRAPE:"):
            reply = scrape_site(msg[7:])
        else:
            reply = "Lütfen geçerli bir komut girin: KOD, DÜZELT, GİRİŞ, SCRAPE"
    except Exception as e:
        reply = f"Hata oluştu: {str(e)}"

    twilio_client.messages.create(
        body=reply,
        from_=twilio_number,
        to=sender
    )
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

