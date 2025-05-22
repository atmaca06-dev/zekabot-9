import requests

def site_login(site, login_info):
    # login_info {"username": "...", "password": "..."} gibi gelir
    # Bu sadece örnek! Gerçek bir site için endpoint ve parametreler değişir!
    try:
        if "hepsiemlak" in site:
            url = "https://www.hepsiemlak.com/kullanici/giris"
            payload = {
                "UserName": login_info.get("username", ""),
                "Password": login_info.get("password", "")
            }
            session = requests.Session()
            response = session.post(url, data=payload)
            if response.ok:
                return "Giriş başarılı!"
            else:
                return f"Giriş başarısız: {response.status_code}"
        else:
            return "Bu siteye otomatik giriş/destek yok."
    except Exception as e:
        return f"Giriş sırasında hata: {e}"
