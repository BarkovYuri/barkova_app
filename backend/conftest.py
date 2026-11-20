"""Общие настройки pytest: тесты не зависят от Redis, Celery-воркера и сети."""

import itertools

import pytest


@pytest.fixture(autouse=True)
def _isolated_infra(settings):
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "tests",
        }
    }
    # Реальный токен из локального .env не должен приводить к запросам в VK.
    settings.VK_GROUP_TOKEN = ""
    settings.VK_GROUP_ID = "123"
    settings.VK_DOCTOR_USER_IDS = []
    settings.DOCTOR_ALERT_EMAILS = []

    from django.core.cache import cache

    cache.clear()

    # Celery читает конфигурацию из Django-настроек с префиксом CELERY_,
    # причём ключ с префиксом важнее значений в celery_app.conf. Поэтому
    # синхронное выполнение задач включаем именно через settings.
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    yield
    cache.clear()


class FakeVK:
    """Подмена apps.notifications.transports.vk.call: записывает вызовы и
    отвечает как VK API."""

    def __init__(self):
        self.calls: list[tuple[str, dict]] = []
        self.allowed = True
        self.fail_send_to: set[str] = set()
        self._ids = itertools.count(1000)

    def __call__(self, method, payload):
        self.calls.append((method, payload))
        if method == "messages.send":
            if str(payload.get("peer_id")) in self.fail_send_to:
                return False, {}, '{"error_code": 10, "error_msg": "Internal server error"}'
            return True, {"response": next(self._ids)}, ""
        if method == "messages.isMessagesFromGroupAllowed":
            return True, {"response": {"is_allowed": int(self.allowed)}}, ""
        if method == "users.get":
            ids = str(payload.get("user_ids", "")).split(",")
            return (
                True,
                {"response": [{"id": int(i), "first_name": "Иван", "last_name": "Петров"} for i in ids if i]},
                "",
            )
        if method == "messages.getConversations":
            return True, {"response": {"count": 0, "items": []}}, ""
        return True, {"response": 1}, ""

    def sent(self, peer_id=None):
        return [
            p for m, p in self.calls if m == "messages.send" and (peer_id is None or str(p["peer_id"]) == str(peer_id))
        ]

    def methods(self):
        return [m for m, _ in self.calls]


@pytest.fixture
def fake_vk(settings, monkeypatch):
    settings.VK_GROUP_TOKEN = "test-token"
    fake = FakeVK()
    monkeypatch.setattr("apps.notifications.transports.vk.call", fake)
    return fake
