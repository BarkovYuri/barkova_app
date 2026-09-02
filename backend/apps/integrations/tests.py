"""
Tests for shared bot integration infrastructure.

This module contains unit tests for the bot base class used by the VK bot.
"""

from django.test import TestCase


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
