"""
Base bot class for Telegram and VK bots.

This module provides a common interface and shared functionality for all bot implementations.
It handles Django initialization, API communication, error handling, and logging.
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from urllib import error, parse, request

from .exceptions import (
    APIException,
    BackendAPIError,
    NetworkError,
    TimeoutError,
)

logger = logging.getLogger(__name__)


class BaseBot(ABC):
    """
    Abstract base class for bot implementations (Telegram, VK, etc).

    This class provides common functionality for:
    - API communication with bot providers
    - Backend API communication
    - Django model access
    - Error handling and logging
    - Configuration management
    """

    # Django setup flag - should be set once per process
    _django_setup_done = False

    def __init__(self, api_token: str, backend_base_url: str, request_timeout: int = 30):
        """
        Initialize the bot.

        Args:
            api_token: Authentication token for the bot provider API
            backend_base_url: Base URL for the backend API
            request_timeout: Timeout in seconds for HTTP requests (default: 30)
        """
        self.api_token = api_token
        self.backend_base_url = backend_base_url
        self.request_timeout = request_timeout

    @classmethod
    def setup_django(cls) -> None:
        """
        Initialize Django ORM - called only once per process.

        This method should be called exactly once at bot startup to avoid
        resource leaks and performance issues. Subsequent calls are no-ops.

        Raises:
            RuntimeError: If Django settings module is not configured
        """
        if cls._django_setup_done:
            return

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

        try:
            import django

            django.setup()
            cls._django_setup_done = True
            logger.info("Django ORM initialized successfully")
        except Exception as exc:
            logger.error("Failed to initialize Django: %s", exc)
            raise RuntimeError(f"Django initialization failed: {exc}") from exc

    @staticmethod
    def make_request(
        url: str,
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to an API endpoint.

        Args:
            url: The full URL to request
            method: HTTP method (GET, POST, etc.)
            data: Request payload (will be URL-encoded or JSON based on headers)
            headers: HTTP headers to include
            timeout: Request timeout in seconds

        Returns:
            Parsed JSON response from the server

        Raises:
            TimeoutError: If the request times out
            NetworkError: If there's a network error
            APIException: If the API returns an error or response can't be parsed
        """
        try:
            req_data = None
            if data is not None:
                if headers and headers.get("Content-Type") == "application/json":
                    req_data = json.dumps(data).encode("utf-8")
                else:
                    req_data = parse.urlencode(data).encode("utf-8")

            req = request.Request(url, data=req_data, method=method)

            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)

            with request.urlopen(req, timeout=timeout) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                logger.debug(f"API request successful: {method} {url}")
                return response_data

        except error.HTTPError as exc:
            logger.error(f"HTTP Error {exc.code}: {exc.reason}")
            raise APIException(f"HTTP {exc.code}: {exc.reason}") from exc
        except error.URLError as exc:
            logger.error(f"Network error: {exc.reason}")
            raise NetworkError(f"Network error: {exc.reason}") from exc
        except TimeoutError as exc:
            logger.error(f"Request timeout after {timeout}s: {url}")
            raise TimeoutError(f"Request timeout: {url}") from exc
        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse JSON response from {url}")
            raise APIException(f"Invalid JSON response from {url}") from exc
        except Exception as exc:
            logger.error(f"Unexpected error during request to {url}: {exc}")
            raise APIException(f"Request failed: {exc}") from exc

    def backend_post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request to the backend API.

        Args:
            path: API endpoint path (e.g., "/api/appointments/confirm/")
            payload: Request payload dictionary

        Returns:
            Parsed JSON response from the backend

        Raises:
            BackendAPIError: If the backend API returns an error
        """
        url = f"{self.backend_base_url}{path}"

        try:
            response = self.make_request(
                url,
                method="POST",
                data=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.request_timeout,
            )

            # Check for backend-specific error responses
            if isinstance(response, dict) and response.get("error"):
                raise BackendAPIError(response.get("error"))

            return response

        except APIException as exc:
            logger.error(f"Backend API error: {exc}")
            raise BackendAPIError(f"Backend API error: {exc}") from exc

    @abstractmethod
    def send_message(self, recipient_id: str | int, text: str) -> bool:
        """
        Send a text message to a user.

        Args:
            recipient_id: User ID or chat ID
            text: Message text

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def handle_callback(self, callback_data: Dict[str, Any]) -> None:
        """
        Handle callback/button action from user.

        Args:
            callback_data: Callback data dictionary with action information
        """
        pass

    @abstractmethod
    def start_polling(self) -> None:
        """Start the bot's main polling loop."""
        pass

    def get_django_model(self, app_name: str, model_name: str) -> type:
        """
        Get a Django model class.

        This method can only be called after setup_django() has been called.

        Args:
            app_name: Django app name (e.g., 'appointments')
            model_name: Model name (e.g., 'Appointment')

        Returns:
            Django model class

        Raises:
            RuntimeError: If Django is not initialized
            ImportError: If the model cannot be found
        """
        if not self._django_setup_done:
            raise RuntimeError("Django not initialized. Call setup_django() first.")

        try:
            from django.apps import apps

            return apps.get_model(app_name, model_name)
        except LookupError as exc:
            logger.error(f"Failed to get Django model {app_name}.{model_name}")
            raise ImportError(f"Model not found: {app_name}.{model_name}") from exc
