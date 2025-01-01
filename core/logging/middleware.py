import logging
import time
from typing import Callable
from django.http import HttpRequest, HttpResponse


class RequestLoggingMiddleware:
    """
    Middleware to log all HTTP requests and responses
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.logger = logging.getLogger("django.request")

        # Define paths that should not be logged (e.g., static files, health checks)
        self.IGNORED_PATHS = [
            "/static/",
            "/media/",
            "/health/",
            "/favicon.ico",
        ]

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Skip logging for ignored paths
        if any(request.path.startswith(path) for path in self.IGNORED_PATHS):
            return self.get_response(request)

        # Start timing the request
        start_time = time.time()

        # Collect request information
        request_data = {
            "method": request.method,
            "path": request.path,
            "user_id": (
                request.user.id
                if hasattr(request, "user") and request.user.is_authenticated
                else None
            ),
            "ip_address": self.get_client_ip(request),
        }

        # Process the request
        response = self.get_response(request)

        # Calculate request duration
        duration = time.time() - start_time

        # Add response information
        request_data.update(
            {
                "status_code": response.status_code,
                "duration": round(duration * 1000, 2),  # Convert to milliseconds
            }
        )

        # Log the request with appropriate level based on status code
        if response.status_code >= 500:
            self.logger.error("Request failed", extra=request_data)
        elif response.status_code >= 400:
            self.logger.warning("Request failed", extra=request_data)
        else:
            self.logger.info("Request processed", extra=request_data)

        return response

    @staticmethod
    def get_client_ip(request: HttpRequest) -> str:
        """Get the client's IP address from the request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR", "")

    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """Log unhandled exceptions"""
        self.logger.error(
            "Unhandled exception",
            extra={
                "method": request.method,
                "path": request.path,
                "user_id": (
                    request.user.id
                    if hasattr(request, "user") and request.user.is_authenticated
                    else None
                ),
                "ip_address": self.get_client_ip(request),
                "exception": str(exception),
            },
            exc_info=True,
        )
