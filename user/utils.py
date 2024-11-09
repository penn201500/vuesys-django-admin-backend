# user/utils.py
from django.conf import settings


def set_token_cookie(response, token_type, token_value):
    """
    Sets the specified token in the response cookies.

    Args:
        response (Response): The DRF Response object.
        token_type (str): 'access' or 'refresh'.
        token (str): The token string.
    """
    is_access = token_type == 'access'
    settings_prefix = 'AUTH' if is_access else 'REFRESH'

    response.set_cookie(
        key=settings.SIMPLE_JWT[f'{settings_prefix}_COOKIE'],
        value=token_value,
        httponly=settings.SIMPLE_JWT[f'{settings_prefix}_COOKIE_HTTP_ONLY'],
        secure=settings.SIMPLE_JWT[f'{settings_prefix}_COOKIE_SECURE'],
        samesite=settings.SIMPLE_JWT[f'{settings_prefix}_COOKIE_SAMESITE'],
        max_age=settings.SIMPLE_JWT[f'{"ACCESS" if is_access else "REFRESH"}_TOKEN_LIFETIME'].total_seconds(),
        path=settings.SIMPLE_JWT[f'{settings_prefix}_COOKIE_PATH'],
    )
    return response