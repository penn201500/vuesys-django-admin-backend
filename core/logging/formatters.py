import json
import logging
from django.utils import timezone


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON structured logs with all necessary context
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_fields = {
            "name",
            "levelname",
            "pathname",
            "lineno",
            "msg",
            "args",
            "exc_info",
            "exc_text",
        }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with structured data"""
        # Basic log data
        message_dict = {
            "timestamp": timezone.localtime().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            # Source location
            "source": {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            },
        }

        # Add exception info if present
        if record.exc_info:
            message_dict["error"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Add request info if available
        if hasattr(record, "request"):
            message_dict["request"] = {
                "method": getattr(record, "method", None),
                "path": getattr(record, "path", None),
                "user_id": getattr(record, "user_id", None),
                "ip": getattr(record, "ip_address", None),
            }

        # Add any extra fields
        extras = {}
        for key, value in record.__dict__.items():
            if key not in self.default_fields and not key.startswith("_"):
                try:
                    # Try default JSON serialization
                    json.dumps(value)
                    extras[key] = value
                except (TypeError, ValueError):
                    # Fallback to string representation
                    extras[key] = str(value)

        if extras:
            message_dict["extra"] = extras

        return json.dumps(message_dict)
