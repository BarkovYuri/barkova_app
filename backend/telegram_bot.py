import json
import os
import time
from urllib import error, parse, request

import socket

_original_getaddrinfo = socket.getaddrinfo

def _ipv4_first_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host == "api.telegram.org":
        return _original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
    return _original_getaddrinfo(host, port, family, type, proto, flags)

socket.getaddrinfo = _ipv4_first_getaddrinfo

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BACKEND_BASE = os.getenv("BACKEND_BASE_URL", "http://backend:8000")


def telegram_api(method: str, payload: dict | None = None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = None

    if payload is not None:
        data = parse.urlencode(payload).encode("utf-8")

    req = request.Request(url, data=data, method="POST" if payload is not None else "GET")

    with request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def backend_post(path: str, payload: dict):
    url = f"{BACKEND_BASE}{path}"
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def send_message(chat_id, text):
    return telegram_api(
        "sendMessage",
        {
            "chat_id": str(chat_id),
            "text": text,
        },
    )


def answer_callback_query(callback_query_id, text):
    return telegram_api(
        "answerCallbackQuery",
        {
            "callback_query_id": callback_query_id,
            "text": text,
        },
    )


def edit_message_text(chat_id, message_id, text):
    return telegram_api(
        "editMessageText",
        {
            "chat_id": str(chat_id),
            "message_id": str(message_id),
            "text": text,
        },
    )


def handle_start(chat_id: int, text: str):
    parts = text.split(" ", 1)

    if len(parts) == 1:
        send_message(chat_id, "Здравствуйте! Telegram-уведомления подключены.")
        return

    payload = parts[1].strip()

    if payload.startswith("connect_"):
        token = payload.replace("connect_", "", 1)

        try:
            backend_post(
                "/api/appointments/telegram/prelink/link/",
                {
                    "token": token,
                    "chat_id": str(chat_id),
                },
            )
            send_message(chat_id, 
                "Здравствуйте!\n"
                "Вы перешли сюда для подтверждения записи к врачу-инфекционисту.\n\n"
                "ℹ️ Ваш аккаунт Telegram успешно привязан к системе записи.\n\n"
                "**Что будет дальше:**\n"
                "1. Мы пришлем вам уведомление для подтверждения визита.\n"
                "2. За 2 часа до приема бот напомнит вам о нем и уточнит, сможете ли вы присутствовать.\n"
                "3. Если вам потребуется отменить прием, вы сможете сделать это прямо в этом чате, нажав кнопку «Отменить запись» или просто написав сообщение в этот чат.\n\n"
                "🔔 Пожалуйста, сейчас перейдите обратно на сайт для продолжения записи."
            )


        except Exception as exc:
            send_message(chat_id, f"Не удалось подключить Telegram: {exc}")
        return

    send_message(chat_id, "Команда распознана, но сценарий не найден.")


def handle_callback(callback_query: dict):
    callback_query_id = callback_query["id"]
    data = callback_query.get("data", "")
    message = callback_query.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")

    try:
        action, appointment_id, token = data.split(":", 2)
    except ValueError:
        answer_callback_query(callback_query_id, "Некорректная команда.")
        return

    if action not in {"confirm", "cancel", "keep"}:
        answer_callback_query(callback_query_id, "Неизвестное действие.")
        return
    
    if action == "keep":
        answer_callback_query(callback_query_id, "Запись оставлена без изменений.")
        edit_message_text(chat_id, message_id, "✅ Запись оставлена без изменений")
        return

    try:
        result = backend_post(
            "/api/appointments/telegram/action/",
            {
                "appointment_id": appointment_id,
                "token": token,
                "action": action,
                "chat_id": str(chat_id),
            },
        )

        if action == "confirm":
            answer_callback_query(callback_query_id, "Запись подтверждена.")
            edit_message_text(chat_id, message_id, "✅ Запись подтверждена")
        else:
            answer_callback_query(callback_query_id, "Запись отменена.")
            edit_message_text(chat_id, message_id, "❌ Запись отменена")

    except Exception as exc:
        answer_callback_query(callback_query_id, f"Ошибка: {exc}")

def find_active_appointment_for_chat(chat_id: int):
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()

    from apps.appointments.models import Appointment

    return (
        Appointment.objects.select_related("slot")
        .filter(telegram_chat_id=str(chat_id), status__in=["new", "confirmed"])
        .order_by("-created_at")
        .first()
    )


def send_cancel_confirmation(chat_id: int, appointment):
    return telegram_api(
        "sendMessage",
        {
            "chat_id": str(chat_id),
            "text": (
                "Вы хотите отменить запись?\n"
                f"Дата: {appointment.slot.date}\n"
                f"Время: {appointment.slot.start_time.strftime('%H:%M')}–{appointment.slot.end_time.strftime('%H:%M')}"
            ),
            "reply_markup": json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Подтвердить отмену",
                                "callback_data": f"cancel:{appointment.id}:{appointment.telegram_link_token}",
                            },
                            {
                                "text": "Оставить запись",
                                "callback_data": f"keep:{appointment.id}:{appointment.telegram_link_token}",
                            },
                        ]
                    ]
                },
                ensure_ascii=False,
            ),
        },
    )


def main():
    offset = None

    while True:
        try:
            payload = {"timeout": 25}
            if offset is not None:
                payload["offset"] = offset

            data = telegram_api("getUpdates", payload)

            for item in data.get("result", []):
                offset = item["update_id"] + 1

                if "callback_query" in item:
                    handle_callback(item["callback_query"])
                    continue

                message = item.get("message")
                if not message:
                    continue

                chat = message.get("chat", {})
                chat_id = chat.get("id")
                text = message.get("text", "")

                if text.startswith("/start"):
                    handle_start(chat_id, text)

                elif text.strip():
                    appointment = find_active_appointment_for_chat(chat_id)
                    if appointment:
                        send_cancel_confirmation(chat_id, appointment)
                    else:
                        send_message(chat_id, "У вас нет активной записи для отмены.")

        except error.HTTPError as exc:
            print("HTTPError:", exc.code)
            time.sleep(3)
        except Exception as exc:
            print("Error:", exc)
            time.sleep(3)


if __name__ == "__main__":
    main()
