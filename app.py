import os
import json
from flask import Flask, request
from openai import OpenAI
from twilio.rest import Client
from general_scraper import scrape_site  # Kendi scraper fonksiyonunu koy
# from code_tester import test_code      # Eğer kod test/düzeltme için ayrı modülün varsa ekle
# from code_fixer import fix_code        # Aynı şekilde düzeltme için modül ekleyebilirsin

app = Flask(__name__)

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
twilio_client = Client(os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN"))
twilio_number = os.environ.get("TWILIO_NUMBER")

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    # GPT-4o ile "işlemi" ve "parametreleri" ayıklayalım:
    gpt_prompt = f"""
    Aşağıdaki kullanıcının WhatsApp mesajından ne yapmak istediğini tek satır JSON olarak çıkar:
    - Sadece şu anahtarlar olacak: 'islem', 'site', 'arama', 'kod'
    - Eğer kod testi/düzeltmesi istiyorsa 'islem' anahtarı 'kodtest' veya 'düzelt' olacak, kodu da 'kod' anahtarına yaz
    - Eğer web scraping ise 'islem' anahtarı 'scrape', site adı 'site', aranacak kelime 'arama'
    - Eğer siteye giriş/form işlemi ise 'islem' anahtarı 'giris', site adı 'site', diğer her şeyi 'arama'ya yaz
    - Sohbetse islem 'sohbet' olur, diğerleri boş kalır

    Mesaj: '{incoming_msg}'
    Çıktı örnekleri:
    - Kod testi:         {{"islem": "kodtest", "kod": "print('selam')", "site": "", "arama": ""}}
    - Kod düzelt:        {{"islem": "düzelt", "kod": "prnt('merhaba')", "site": "", "arama": ""}}
    - Sahibinden scraping: {{"islem": "scrape", "site": "sahibinden", "arama": "ankara fiyatları", "kod": ""}}
    - Giriş:             {{"islem": "giris", "site": "hepsiemlak", "arama": "kullanici123 sifre123", "kod": ""}}
    - Sohbet:            {{"islem": "sohbet", "site": "", "arama": "", "kod": ""}}
    Sadece tek satır JSON ver!
    """

    gpt_response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": gpt_prompt}],
        max_tokens=180,
        temperature=0.1
    )
    try:
        parsed = json.loads(gpt_response.choices[0].message.content.strip())
    except Exception as e:
        parsed = {"islem": "sohbet", "site": "", "arama": "", "kod": ""}

    islem = parsed.get("islem", "")
    site = parsed.get("site", "")
    arama = parsed.get("arama", "")
    kod = parsed.get("kod", "")

    # Ana akış
    if islem == "scrape":
        try:
            result = scrape_site(site, arama)
            yanit = f"{site} sitesinde '{arama}' için sonuç: {result}"
        except Exception as e:
            yanit = f"Scraper hatası: {e}"
    elif islem == "kodtest":
        try:
            # result = test_code(kod)
            result = f"Burada kod test fonksiyonu çalışır: {kod}"
            yanit = f"Test sonucu:\n{result}"
        except Exception as e:
            yanit = f"Kod test hatası: {e}"
    elif islem == "düzelt":
        try:
            # result = fix_code(kod, openai_client)
            result = f"Burada kod düzeltme fonksiyonu çalışır: {kod}"
            yanit = f"Düzeltilmiş kod:\n{result}"
        except Exception as e:
            yanit = f"Kod düzeltme hatası: {e}"
    elif islem == "giris":
        try:
            yanit = f"{site} sitesine giriş işlemi için şunlar kullanılacak: {arama}"
        except Exception as e:
            yanit = f"Giriş hatası: {e}"
    else:  # sohbet
        yanit = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": incoming_msg}],
            max_tokens=250,
        ).choices[0].message.content.strip()

    # Yanıtı WhatsApp'a gönder
    twilio_client.messages.create(
        from_=twilio_number,
        to=sender,
        body=yanit
    )
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
