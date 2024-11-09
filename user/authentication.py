# user/authentication.py

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that retrieves the token from a cookie.
    """

    def get_raw_token(self, request):
        """
        Override the method to retrieve the token from the specified cookie.
        """
        # print("Attempting to retrieve accessToken from cookies")
        token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        # print(f"Retrieved accessToken from cookies: {token}")
        return token

    def authenticate(self, request):
        access_token = self.get_raw_token(request)

        # print(f"Authenticating with access token: {access_token}")
        if not access_token:
            return None
        try:
            validated_token = self.get_validated_token(access_token)
            return self.get_user(validated_token), validated_token
        except TokenError as e:
            # print(f"Token error: {e}")
            return None
