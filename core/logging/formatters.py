import json
import logging
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after gathering all the log record args
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_fields = ["name", "levelname", "pathname", "lineno"]

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as JSON
        """
        message_dict = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "user_id"):
            message_dict["user_id"] = record.user_id
        if hasattr(record, "ip_address"):
            message_dict["ip_address"] = record.ip_address
        if hasattr(record, "method"):
            message_dict["method"] = record.method
        if hasattr(record, "path"):
            message_dict["path"] = record.path
        if hasattr(record, "status_code"):
            message_dict["status_code"] = record.status_code

        # Add exception info if present
        if record.exc_info:
            message_dict["exception"] = self.formatException(record.exc_info)

        # Add any extra attributes from the record
        for key, value in record.__dict__.items():
            if key not in self.default_fields and not key.startswith("_"):
                try:
                    json.dumps(value)  # Check if value is JSON serializable
                    message_dict[key] = value
                except (TypeError, ValueError):
                    message_dict[key] = str(value)

        return json.dumps(message_dict)
