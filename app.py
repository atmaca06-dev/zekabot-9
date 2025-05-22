import os
from flask import Flask, request
from openai import OpenAI
from twilio.rest import Client
import requests
from bs4 import BeautifulSoup

# Flask app
app = Flask(__name__)

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
twilio_client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))
twilio_number = os.environ.get("TWILIO_NUMBER")

# --- Scraping Fonksiyonları ---
def scrape_sahibinden(query):
    # Örn: query="ankara-sincan-satilik"
    url = f"https://www.sahibinden.com/{query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.content, "html.parser")
        ilanlar = soup.find_all("a", class_="classifiedTitle")
        if not ilanlar:
            return "Sahibinden'de ilan bulunamadı."
        sonuc = "[Sahibinden] İlk 5 ilan başlığı:\n"
        for ilan in ilanlar[:5]:
            sonuc += "- " + ilan.text.strip() + "\n"
        return sonuc
    except Exception as e:
        return f"Sahibinden scraping hatası: {e}"

def scrape_hepsiemlak(query):
    # Örn: query="ankara-sincan-satilik"
    url = f"https://www.hepsiemlak.com/{query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.content, "html.parser")
        ilanlar = soup.find_all("a", class_="card-link")
        if not ilanlar:
            return "Hepsiemlak'ta ilan bulunamadı."
        sonuc = "[Hepsiemlak] İlk 5 ilan başlığı:\n"
        for ilan in ilanlar[:5]:
            sonuc += "- " + ilan.text.strip() + "\n"
        return sonuc
    except Exception as e:
        return f"Hepsiemlak scraping hatası: {e}"

def scrape_site(site, query):
    # site: sahibinden.com veya hepsiemlak.com
    if "sahibinden" in site:
        return scrape_sahibinden(query)
    elif "hepsiemlak" in site:
        return scrape_hepsiemlak(query)
    else:
        return "Sadece sahibinden.com veya hepsiemlak.com destekleniyor."

# --- GPT ile Komut Yönlendirme ---
def gpt_command_parser(user_message):
    prompt = f"""
Kullanıcının aşağıdaki mesajını analiz et ve şu formatta JSON döndür:
{{
  "action": "scrape",
  "site": "...",  // sahibinden.com veya hepsiemlak.com
  "query": "..." // site URL'sindeki şehir-ilçe-tip (örn: ankara-sincan-satilik)
}}
Eğer komut anlamıyorsan {{"action": "bilinmiyor"}} döndür.
Kullanıcı mesajı: {user_message}
"""
    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}]
    )
    import json
    try:
        command = json.loads(completion.choices[0].message.content)
    except Exception:
        command = {"action": "bilinmiyor"}
    return command

# --- Webhook ---
@app.route("/webhook", methods=["POST"])
def webhook():
    msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")
    command = gpt_command_parser(msg)
    action = command.get("action", "")

    if action == "scrape":
        site = command.get("site", "")
        query = command.get("query", "")
        cevap = scrape_site(site, query)
    else:
        cevap = "Komut anlaşılamadı veya desteklenmiyor."

    twilio_client.messages.create(
        body=cevap,
        from_=twilio_number,
        to=sender
    )
    return "OK", 200

# Ana sayfa test
@app.route("/", methods=["GET"])
def home():
    return "Zekabot Emlak Otomasyon Sistemi Çalışıyor!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
