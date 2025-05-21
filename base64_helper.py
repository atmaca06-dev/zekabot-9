import base64

def decode_base64_image(data):
    try:
        img_bytes = base64.b64decode(data)
        return img_bytes
    except Exception as e:
        return f"Base64 çözme hatası: {e}"
