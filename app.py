import os
from flask import Flask, request
from openai import OpenAI
from twilio.rest import Client
import traceback

app = Flask(__name__)

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
twilio_client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))
twilio_number = os.environ.get("TWILIO_NUMBER")

# KOD TEST / DÜZELTME / VERİ ÇEKME / FORM DOLDURMA FONKSİYONLARI

def test_code(kod):
    import io, sys
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    try:
        exec(kod)
        result = mystdout.getvalue()
        if not result:
            result = "Kod çalıştı, çıktı üretmedi."
    except Exception:
        result = "Kodda hata var:\n" + traceback.format_exc()
    finally:
        sys.stdout = old_stdout
    return result

def fix_code(kod):
    prompt = f"Bu kodda hata var, düzelt: \n{kod}\n"
    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}]
    )
    return completion.choices[0].message.content

def scrape_site(site, query):
    # Buraya gerçek scraping kodu entegre edilir
    return f"{site} sitesinde '{query}' için sonuç: (Buraya scraping ile gelen veriler gelir)"

def site_login(site, login_info):
    # Buraya otomatik siteye giriş ve form doldurma kodları gelir
    return f"{site} sitesine giriş yapıldı: {login_info}"

# --- GPT YÖNLENDİRİCİ ---
def gpt_command_parser(user_message):
    prompt = f"""
Sen profesyonel bir komut analizcisisin. Kullanıcının aşağıdaki mesajını detaylı analiz et.
Aşağıdaki *her türlü görevi* tanıyacak şekilde çıktı üret:
- scrape: bir siteden veri çek
- kod_test: kodu test et
- kod_fix: hatalı kodu düzelt
- site_login: siteye giriş/form doldurma
- sohbet: selamlaşma veya bilgi amaçlı mesajlar (merhaba, nasılsın, bilgi ver vs.)
Her mesajı şu formatta analiz et:
{{
    "action": "...",      // Görev tipi
    "site": "...",        // Site adı
    "query": "...",       // Arama/metin
    "kod": "...",         // Kod varsa
    "login_info": {{...}},// Giriş veya form bilgileri (varsa)
    "message": "..."      // Sadece sohbetse, cevap metni
}}
Eğer hiç anlamıyorsan: {{"action":"bilinmiyor"}}
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

# --- WEBHOOK ---

@app.route("/webhook", methods=["POST"])
def webhook():
    msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")
    command = gpt_command_parser(msg)
    action = command.get("action", "")

    if action == "bilinmiyor":
        cevap = "Komut anlaşılamadı veya bilinmiyor."
    elif action == "sohbet":
        cevap = command.get("message", "Merhaba! Ben Zekabot.")
    elif action == "kod_test":
        kod = command.get("kod", "")
        cevap = test_code(kod)
    elif action == "kod_fix":
        kod = command.get("kod", "")
        cevap = fix_code(kod)
    elif action == "scrape":
        site = command.get("site", "")
        query = command.get("query", "")
        cevap = scrape_site(site, query)
    elif action == "site_login":
        site = command.get("site", "")
        login_info = command.get("login_info", {})
        cevap = site_login(site, login_info)
    else:
        cevap = "Tanımsız komut."

    twilio_client.messages.create(
        body=cevap,
        from_=twilio_number,
        to=sender
    )

    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "Zekabot Otomasyon Aktif", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
