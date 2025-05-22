import os
from flask import Flask, request
from openai import OpenAI
from twilio.rest import Client

# Burada varsa ek modüllerini import et
# from scraper.general_scraper import scrape_site
# from executor.code_tester import test_code
# from executor.code_fixer import fix_code
# from web_actions.login_bot import login_and_submit

app = Flask(__name__)

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
twilio_client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))
twilio_number = os.environ.get("TWILIO_NUMBER")

# Ana komut yönlendirici fonksiyon
def gpt_command_parser(user_message):
    prompt = f"""
Sen bir komut analizcisisin. Kullanıcının aşağıdaki mesajını çözümle ve çıktıyı JSON olarak üret.
Mevcut komutlar:
- scrape (veri çekme)
- kod_test (kod test etme)
- kod_fix (kod hatası düzeltme)
- site_login (siteye giriş yapma)

Komut ve parametrelerini şu formatta döndür:
{{"action": "...", "site": "...", "query": "...", "kod": "...", "login_info": {{...}} }}

Kullanıcı mesajı: {user_message}
Eğer komut anlamıyorsan {"action": "bilinmiyor"} döndür.
"""
    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}]
    )
    # JSON kısmı genellikle completion.choices[0].message.content
    import json
    try:
        command = json.loads(completion.choices[0].message.content)
    except Exception:
        command = {"action": "bilinmiyor"}
    return command

if action == "bilinmiyor":
    cevap = "Komut anlaşılamadı veya bilinmiyor."
else:
    # Burada diğer aksiyonlara göre işlemler yapılır
    ...

@app.route("/webhook", methods=["POST"])
def webhook():
    msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")
    command = gpt_command_parser(msg)    # Burada msg artık tanımlı!
    action = command.get("action", "")
    
    if action == "bilinmiyor":
        cevap = "Komut anlaşılamadı veya bilinmiyor."
    else:
        # Diğer işlemler burada
        cevap = "İşlem başarılı!"
    
    # Burada Twilio ile cevap gönderme kodun devamı olacak
    return "OK"



    # Sonuca göre ilgili fonksiyonu çalıştır
    yanit = ""
    if komut["action"] == "scrape":
        # ÖRNEK: scrape_site fonksiyonuna site ve query gönder
        # yanit = scrape_site(komut["site"], komut["query"])
        yanit = f"{komut['site']} sitesinde '{komut['query']}' için sonuç: [örnek sonuç]"
    elif komut["action"] == "kod_test":
        # yanit = test_code(komut["kod"])
        yanit = "[örnek kod test sonucu]"
    elif komut["action"] == "kod_fix":
        # yanit = fix_code(komut["kod"])
        yanit = "[örnek kod düzeltildi]"
    elif komut["action"] == "site_login":
        # yanit = login_and_submit(komut["site"], komut["login_info"])
        yanit = "[örnek site giriş sonucu]"
    else:
        yanit = "Komut anlaşılamadı. Lütfen açıkça belirtin (ör: sahibinden.com Ankara Sincan daireleri çek)."

    twilio_client.messages.create(
        body=yanit,
        from_=twilio_number,
        to=sender
    )
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "Zekabot GPT analizli aktif!"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
