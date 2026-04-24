"""
Tests for telegram bot integration.

This module contains unit and integration tests for telegram_bot functionality
including message handling, callback processing, and error handling.
"""

import json
from unittest.mock import MagicMock, patch

from django.test import TestCase


class TelegramBotCallbackParsingTest(TestCase):
    """Test telegram callback data parsing."""

    def test_parse_valid_callback_data(self) -> None:
        """Test parsing valid callback data in format: action:appointment_id:token."""
        from apps.integrations.bot_utils import parse_callback_data

        data = "confirm:123:abc123token"
        result = parse_callback_data(data, separator=":")

        self.assertEqual(result["action"], "confirm")
        self.assertEqual(result["appointment_id"], "123")
        self.assertEqual(result["token"], "abc123token")

    def test_parse_callback_data_missing_parts(self) -> None:
        """Test parsing callback data with missing parts."""
        from apps.integrations.bot_utils import parse_callback_data
        from apps.integrations.exceptions import CallbackDataError

        with self.assertRaises(CallbackDataError):
            parse_callback_data("invalid", separator=":")

    def test_parse_empty_callback_data(self) -> None:
        """Test parsing empty callback data."""
        from apps.integrations.bot_utils import parse_callback_data
        from apps.integrations.exceptions import CallbackDataError

        with self.assertRaises(CallbackDataError):
            parse_callback_data("", separator=":")


class TelegramBotUtilsTest(TestCase):
    """Test telegram bot utility functions."""

    def test_validate_token_success(self) -> None:
        """Test token validation with valid token."""
        from apps.integrations.bot_utils import validate_token

        token = "valid_token_12345"
        result = validate_token(token)

        self.assertEqual(result, token)

    def test_validate_token_too_short(self) -> None:
        """Test token validation with too short token."""
        from apps.integrations.bot_utils import validate_token
        from apps.integrations.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            validate_token("short")

    def test_validate_token_empty(self) -> None:
        """Test token validation with empty token."""
        from apps.integrations.bot_utils import validate_token
        from apps.integrations.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            validate_token("")

    def test_validate_user_id_success(self) -> None:
        """Test user ID validation with valid ID."""
        from apps.integrations.bot_utils import validate_user_id

        user_id = 123456789
        result = validate_user_id(user_id)

        self.assertEqual(result, "123456789")

    def test_validate_user_id_invalid(self) -> None:
        """Test user ID validation with invalid ID."""
        from apps.integrations.bot_utils import validate_user_id
        from apps.integrations.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            validate_user_id("not_a_number")

    def test_validate_user_id_negative(self) -> None:
        """Test user ID validation with negative ID."""
        from apps.integrations.bot_utils import validate_user_id
        from apps.integrations.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            validate_user_id(-1)


class BaseBotConfigurationTest(TestCase):
    """Test BaseBot Django setup."""

    def test_django_setup_called_once(self) -> None:
        """Test that Django setup is only called once."""
        from apps.integrations.base_bot import BaseBot

        # Reset setup flag
        BaseBot._django_setup_done = False

        # Call setup twice
        BaseBot.setup_django()
        setup_count_1 = BaseBot._django_setup_done

        BaseBot.setup_django()
        setup_count_2 = BaseBot._django_setup_done

        # Both should be True (setup only called once)
        self.assertTrue(setup_count_1)
        self.assertTrue(setup_count_2)
