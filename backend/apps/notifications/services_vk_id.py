import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def verify_vk_id_token(access_token: str, claimed_user_id: str) -> dict:
    """
    Верифицирует VK ID access_token обращением к OIDC user_info endpoint'у
    и сравнением user_id с заявленным фронтом.

    Важно: VK ID 2.x выдаёт OAuth 2.1 / OIDC токены, которые НЕ работают
    с классическим api.vk.com/method/users.get. Для них есть специальный
    user_info endpoint id.vk.com/oauth2/user_info.
    """
    try:
        response = requests.post(
            "https://id.vk.com/oauth2/user_info",
            data={
                "client_id": settings.VK_APP_ID,
                "access_token": access_token,
            },
            timeout=10,
        )
        data = response.json()
    except Exception:
        logger.exception("VK ID user_info request failed")
        return {"verified": False}

    if "error" in data:
        logger.warning("VK ID user_info returned error: %s", data)
        return {"verified": False}

    user = data.get("user") or {}
    actual_user_id = str(user.get("user_id") or user.get("id") or "")
    if not actual_user_id:
        logger.warning("VK ID user_info response missing user_id: %s", data)
        return {"verified": False}
    if actual_user_id != str(claimed_user_id):
        logger.warning(
            "VK ID user_id mismatch: claimed=%s actual=%s",
            claimed_user_id,
            actual_user_id,
        )
        return {"verified": False}

    return {"verified": True, "user_id": actual_user_id}
