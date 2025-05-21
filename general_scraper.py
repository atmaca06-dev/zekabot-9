import subprocess

def test_code(code):
    try:
        result = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=10  # 10 saniyeden fazla sürerse iptal
        )
        return result.stdout or result.stderr or "Çıktı yok."
    except subprocess.TimeoutExpired:
        return "Kod çalıştırma süresi doldu."
    except Exception as e:
        return f"Hata: {e}"
