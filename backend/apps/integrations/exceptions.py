"""
Custom exceptions for bot integrations.

This module defines specific exceptions used across Telegram and VK bot implementations.
Proper exception handling allows for better error logging and user feedback.
"""


class BotException(Exception):
    """Base exception for all bot-related errors."""

    pass


class APIException(BotException):
    """Exception for API communication errors."""

    pass


class TelegramAPIError(APIException):
    """Exception raised when Telegram API returns an error."""

    pass


class VKAPIError(APIException):
    """Exception raised when VK API returns an error."""

    pass


class BackendAPIError(APIException):
    """Exception raised when backend API returns an error."""

    pass


class AppointmentException(BotException):
    """Exception for appointment-related errors."""

    pass


class AppointmentNotFound(AppointmentException):
    """Exception raised when an appointment is not found."""

    pass


class InvalidTokenError(BotException):
    """Exception raised when a token is invalid or expired."""

    pass


class ValidationError(BotException):
    """Exception raised when input validation fails."""

    pass


class CallbackDataError(ValidationError):
    """Exception raised when callback data cannot be parsed."""

    pass


class NetworkError(APIException):
    """Exception for network-related errors."""

    pass


class TimeoutError(NetworkError):
    """Exception raised when API request times out."""

    pass
