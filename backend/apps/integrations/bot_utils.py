"""
Utility functions for bot implementations.

This module provides common utility functions used across multiple bot implementations,
including Django model access, appointment handling, and validation.
"""

import json
import logging
from typing import Any, Dict, Optional

from .exceptions import (
    AppointmentNotFound,
    CallbackDataError,
    ValidationError,
)

logger = logging.getLogger(__name__)


def get_appointment_by_user(user_id: str | int, platform: str) -> Optional[Any]:
    """
    Get an active appointment for a user by platform.

    Args:
        user_id: User ID from the platform (Telegram chat_id or VK user_id)
        platform: Bot platform ('telegram' or 'vk')

    Returns:
        Appointment object or None if not found

    Raises:
        AppointmentNotFound: If no active appointment exists
    """
    from apps.appointments.models import Appointment

    field_name = {
        "telegram": "telegram_chat_id",
        "vk": "vk_user_id",
    }.get(platform)

    if not field_name:
        raise ValidationError(f"Unknown platform: {platform}")

    try:
        appointment = (
            Appointment.objects.select_related("slot")
            .filter(**{field_name: str(user_id), "status__in": ["new", "confirmed"]})
            .order_by("-created_at")
            .first()
        )

        if not appointment:
            logger.debug(f"No active appointment found for {platform} user {user_id}")
            return None

        logger.debug(f"Found appointment {appointment.id} for {platform} user {user_id}")
        return appointment

    except Exception as exc:
        logger.error(f"Failed to get appointment for {platform} user {user_id}: {exc}")
        raise AppointmentNotFound(f"Failed to retrieve appointment: {exc}") from exc


def parse_callback_data(raw_data: str | Dict[str, Any], separator: str = ":") -> Dict[str, Any]:
    """
    Parse callback data from bot buttons.

    Supports both string format (colon-separated) and JSON format.

    Args:
        raw_data: Raw callback data (string or dict)
        separator: Separator character for string format (default: ":")

    Returns:
        Parsed callback data as dictionary

    Raises:
        CallbackDataError: If callback data cannot be parsed
    """
    if isinstance(raw_data, dict):
        return raw_data

    if not raw_data:
        raise CallbackDataError("Callback data is empty")

    # Try JSON parsing first
    if isinstance(raw_data, str) and raw_data.startswith("{"):
        try:
            return json.loads(raw_data)
        except json.JSONDecodeError as exc:
            raise CallbackDataError(f"Invalid JSON callback data: {exc}") from exc

    # Try colon-separated format
    if isinstance(raw_data, str) and separator in raw_data:
        try:
            parts = raw_data.split(separator, 2)  # Max 3 parts
            if len(parts) < 2:
                raise CallbackDataError(
                    f"Invalid callback format: expected at least 2 parts, got {len(parts)}"
                )

            return {
                "action": parts[0],
                "appointment_id": parts[1],
                "token": parts[2] if len(parts) > 2 else None,
            }
        except Exception as exc:
            raise CallbackDataError(f"Failed to parse callback data: {exc}") from exc

    raise CallbackDataError(
        f"Unknown callback data format: {raw_data}. "
        f"Expected JSON or {separator}-separated string."
    )


def validate_appointment_token(appointment: Any, token: str, platform: str) -> bool:
    """
    Validate that the token matches the appointment.

    Args:
        appointment: Appointment object
        token: Token from callback data
        platform: Bot platform ('telegram' or 'vk')

    Returns:
        True if token is valid

    Raises:
        ValidationError: If token is invalid or missing
    """
    field_name = {
        "telegram": "telegram_link_token",
        "vk": "vk_link_token",
    }.get(platform)

    if not field_name:
        raise ValidationError(f"Unknown platform: {platform}")

    if not hasattr(appointment, field_name):
        raise ValidationError(f"Appointment has no field '{field_name}'")

    stored_token = getattr(appointment, field_name)

    if str(token) != str(stored_token):
        logger.warning(f"Token mismatch for appointment {appointment.id}")
        raise ValidationError("Token validation failed")

    return True


def format_appointment_info(appointment: Any) -> str:
    """
    Format appointment information for display.

    Args:
        appointment: Appointment object with related slot

    Returns:
        Formatted appointment info string
    """
    slot = appointment.slot
    date_str = slot.date.strftime("%d.%m.%Y")
    time_str = f"{slot.start_time.strftime('%H:%M')}–{slot.end_time.strftime('%H:%M')}"

    return f"📅 {date_str}\n🕐 {time_str}"


def should_send_greeting(user_id: str | int, platform: str, cache_timeout: int = 86400) -> bool:
    """
    Check if greeting should be sent to user (rate limiting).

    Uses Django cache to prevent sending duplicates within timeout period.

    Args:
        user_id: User ID from the platform
        platform: Bot platform ('telegram' or 'vk')
        cache_timeout: Seconds before allowing greeting again (default: 24 hours)

    Returns:
        True if greeting should be sent, False if already sent recently
    """
    from django.core.cache import cache

    cache_key = f"bot_greeting_{platform}_{user_id}"

    if cache.get(cache_key):
        logger.debug(f"Greeting already sent to {platform} user {user_id}, skipping")
        return False

    cache.set(cache_key, "1", timeout=cache_timeout)
    return True


def validate_user_id(user_id: str | int, min_value: int = 1) -> str:
    """
    Validate and normalize user ID.

    Args:
        user_id: User ID from bot platform
        min_value: Minimum valid user ID value

    Returns:
        Normalized user ID as string

    Raises:
        ValidationError: If user ID is invalid
    """
    try:
        user_id_int = int(user_id)
        if user_id_int < min_value:
            raise ValueError(f"User ID must be >= {min_value}")
        return str(user_id_int)
    except (ValueError, TypeError) as exc:
        raise ValidationError(f"Invalid user ID: {user_id}") from exc


def validate_token(token: str, min_length: int = 10) -> str:
    """
    Validate and normalize token.

    Args:
        token: Token to validate
        min_length: Minimum token length

    Returns:
        Normalized token as string

    Raises:
        ValidationError: If token is invalid
    """
    if not token or not isinstance(token, str):
        raise ValidationError("Token must be a non-empty string")

    token = token.strip()

    if len(token) < min_length:
        raise ValidationError(f"Token too short (minimum {min_length} characters)")

    return token
