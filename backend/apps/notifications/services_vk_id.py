import logging

import requests

logger = logging.getLogger(__name__)


def verify_vk_id_token(access_token: str, claimed_user_id: str) -> dict:
    """
    Верифицирует VK ID access_token обращением к users.get и сравнением
    user_id с заявленным фронтом. Это правильный способ при VK ID
    OAuth 2.1 + PKCE: code обменивает только сам VKID SDK в браузере
    (только он знает code_verifier), а backend проверяет уже выданный
    токен server-to-server.
    """
    try:
        response = requests.get(
            "https://api.vk.com/method/users.get",
            params={
                "access_token": access_token,
                "v": "5.131",
            },
            timeout=10,
        )
        data = response.json()
    except Exception:
        logger.exception("VK users.get request failed")
        return {"verified": False}

    if "error" in data:
        logger.warning("VK users.get returned error: %s", data["error"])
        return {"verified": False}

    users = data.get("response") or []
    if not users:
        logger.warning("VK users.get returned empty response: %s", data)
        return {"verified": False}

    actual_user_id = str(users[0].get("id") or "")
    if not actual_user_id:
        return {"verified": False}
    if actual_user_id != str(claimed_user_id):
        logger.warning(
            "VK user_id mismatch: claimed=%s actual=%s",
            claimed_user_id,
            actual_user_id,
        )
        return {"verified": False}

    return {"verified": True, "user_id": actual_user_id}
