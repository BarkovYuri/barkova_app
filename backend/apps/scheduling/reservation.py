"""Soft-reservation слотов через Redis.

Когда пользователь выбирает слот в booking-форме, мы кладём в кэш
ключ `slot_lock:<id>` со случайным токеном и TTL 5 минут. Это даёт
человеку время заполнить форму, не боясь что слот «уведут».

Защита не строгая: финальный гарант уникальности — DB-constraint
`unique_active_appointment_per_slot`. Reservation — это только UX-слой,
который превращает «гонку на финише» в «приехал второй — увидел сразу».

Race-окно при release минимально (get → delete без CAS), но даже если
кто-то «случайно» отпустит чужой лок — ничего страшного: финальная
защита всё равно в БД.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass

from django.core.cache import cache

RESERVATION_TTL_SECONDS = 300  # 5 минут
TOKEN_BYTES = 32  # 64 hex chars

_KEY_PREFIX = "slot_lock"


def _key(slot_id: int) -> str:
    return f"{_KEY_PREFIX}:{slot_id}"


@dataclass(frozen=True)
class Reservation:
    slot_id: int
    token: str
    ttl_seconds: int = RESERVATION_TTL_SECONDS


def reserve_slot(slot_id: int) -> Reservation | None:
    """Атомарная попытка зарезервировать слот.

    Возвращает Reservation если ключа ещё не было, иначе None
    (слот уже зарезервирован кем-то другим).
    """
    token = secrets.token_hex(TOKEN_BYTES)
    # cache.add — это SETNX в backend-агностичной обёртке Django:
    # успех только если ключа не существует.
    if cache.add(_key(slot_id), token, timeout=RESERVATION_TTL_SECONDS):
        return Reservation(slot_id=slot_id, token=token)
    return None


def is_slot_reserved(slot_id: int) -> bool:
    return cache.get(_key(slot_id)) is not None


def is_owned_by(slot_id: int, token: str) -> bool:
    if not token:
        return False
    stored = cache.get(_key(slot_id))
    return bool(stored and stored == token)


def release_slot(slot_id: int, token: str) -> bool:
    """Освобождает слот, только если токен совпадает.

    Между get и delete есть микро-race: если в этот момент TTL истёк
    и кто-то новый успел зарезервировать тот же слот, мы можем стереть
    его лок. Это ОК — UX-уровень защиты, финальный гарант в БД.
    """
    if is_owned_by(slot_id, token):
        cache.delete(_key(slot_id))
        return True
    return False


def get_reserved_slot_ids(slot_ids: list[int]) -> set[int]:
    """Массовая проверка для списка слотов одной даты."""
    if not slot_ids:
        return set()
    keys = [_key(sid) for sid in slot_ids]
    found = cache.get_many(keys)
    return {sid for sid in slot_ids if _key(sid) in found}
