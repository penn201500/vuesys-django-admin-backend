import logging
from functools import wraps


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


def log_operation(logger_name: str, operation: str):
    """
    Decorator to log operations with additional context

    Usage:
    @log_operation('user_operations', 'create_user')
    def create_user(request, *args, **kwargs):
        ...
    """

    def decorator(func):
        logger = get_logger(logger_name)

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Get request object (assuming first arg is request in view)
                request = args[0] if args else None
                user_id = (
                    request.user.id if request and hasattr(request, "user") else None
                )

                # Log operation start
                extra = {
                    "operation": operation,
                    "user_id": user_id,
                }
                logger.info(f"Starting operation: {operation}", extra=extra)

                # Execute function
                result = func(*args, **kwargs)

                # Log successful completion
                logger.info(f"Operation completed: {operation}", extra=extra)
                return result

            except Exception as e:
                # Log error
                logger.error(
                    f"Operation failed: {operation}",
                    extra={"operation": operation, "error": str(e)},
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator
