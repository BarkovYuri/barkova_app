import requests
from django.conf import settings


def exchange_vk_id_code(code: str, device_id: str) -> dict:
    """
    Обменивает VK ID code на данные пользователя
    """

    url = "https://id.vk.ru/oauth2/auth"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.VK_APP_ID,
        "client_secret": settings.VK_APP_SECRET,
        "device_id": device_id,
        "redirect_uri": settings.VK_ID_REDIRECT_URL,
    }

    response = requests.post(url, data=data, timeout=10)

    try:
        result = response.json()
    except Exception:
        return {"error": "invalid_json"}

    return result