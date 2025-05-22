import os
from flask import Flask, request
from openai import OpenAI
from twilio.rest import Client
import traceback

app = Flask(__name__)

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
twilio_client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))
twilio_number = os.environ.get("TWILIO_NUMBER")

# --- KOD TEST ve DÜZELTME FONKSİYONLARI ---
def test_code(kod):
    import io, sys
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    try:
        exec(kod)
        result = mystdout.getvalue()
        if not result:
            result = "Kod çalıştı, çıktı üretmedi."
    except Exception as e:
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

# --- ÖRNEK SCRAPE (Burada örnek olarak, sadece site ve query'yi ekrana yazıyor, gerçek scraping için requests+BeautifulSoup ile doldurabilirsin) ---
def scrape_site(site, query):
    return f"{site} sitesinde '{query}' için sonuç: (Buraya scraping ile gelen veriler gelir)"

# --- GPT KOMUT AYRIŞTIRICI ---
def gpt_command_parser(user_message):
    prompt = f"""
Sen bir komut analizcisisin. Kullanıcının aşağıdaki mesajını çözümle ve çıktıyı JSON olarak üret.
Mevcut komutlar:
- scrape (veri çekme)
- kod_test (kod test etme)
- kod_fix (kod hatası düzeltme)
Komut ve parametrelerini şu formatta döndür:
{{"action": "...", "site": "...", "query": "...", "kod": "..."}}
Kullanıcı mesajı: {user_message}
Eğer komut anlamıyorsan {{"action": "bilinmiyor"}} döndür.
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

    # Cevap stringini üret
    if action == "bilinmiyor":
        cevap = "Komut anlaşılamadı veya bilinmiyor."
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
    else:
        cevap = "Tanımsız komut."
    # Twilio üzerinden cevap gönder
    twilio_client.messages.create(
        body=cevap,
        from_=twilio_number,
        to=sender
    )
    return "OK", 200

# Ana sayfa test
@app.route("/", methods=["GET"])
def home():
    return "Zekabot GPT Otomasyon Sistemi Aktif", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
