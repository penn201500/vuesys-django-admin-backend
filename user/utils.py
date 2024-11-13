# user/utils.py
from functools import wraps

from django.conf import settings
from django_ratelimit.decorators import ratelimit


def rate_limit_user(rate, method="POST"):
    """
    Decorator for rate limiting based on authenticated user.
    """

    def decorator(view_func):
        @ratelimit(key="user", rate=rate, block=False, method=method)
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def rate_limit_ip(rate, method="POST"):
    """
    Decorator for rate limiting based on IP address.
    """

    def decorator(view_func):
        @ratelimit(key="ip", rate=rate, block=False, method=method)
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def set_token_cookie(response, token_type, token_value, max_age=None):
    """
    Sets the specified token in the response cookies.

    Args:
        response (Response): The DRF Response object.
        token_type (str): 'access' or 'refresh'.
        token (str): The token string.
        max_age (int, optional): Max age in seconds for the cookie. Defaults to None.
    """
    is_access = token_type == "access"
    settings_prefix = "AUTH" if is_access else "REFRESH"

    cookie_kwargs = {
        "key": settings.SIMPLE_JWT[f"{settings_prefix}_COOKIE"],
        "value": token_value,
        "httponly": settings.SIMPLE_JWT[f"{settings_prefix}_COOKIE_HTTP_ONLY"],
        "secure": settings.SIMPLE_JWT[f"{settings_prefix}_COOKIE_SECURE"],
        "samesite": settings.SIMPLE_JWT[f"{settings_prefix}_COOKIE_SAMESITE"],
        "path": settings.SIMPLE_JWT[f"{settings_prefix}_COOKIE_PATH"],
    }

    if max_age is not None:
        cookie_kwargs["max_age"] = max_age

    response.set_cookie(**cookie_kwargs)
    return response
