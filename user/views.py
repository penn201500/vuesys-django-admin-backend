# views.py

from datetime import datetime, timezone, timedelta

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView as SimpleJWTTokenRefreshView

from user.utils import set_token_cookie
from .authentication import CookieJWTAuthentication
from .serializers import CustomTokenObtainPairSerializer
from django_ratelimit.decorators import ratelimit

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view to handle JWT authentication and return custom response structure.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    @ratelimit(key='ip', rate=settings.RATE_LIMIT_LOGIN)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        remember_me = request.data.get('rememberMe', False)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.user

            # Adjust token lifetimes based on rememberMe value
            if remember_me:
                # Set longer lifetimes for 'remember me'
                access_token_lifetime = timedelta(minutes=30)  # Adjust as needed
                refresh_token_lifetime = timedelta(days=1)  # Adjust as needed
            else:
                # Use default lifetimes
                access_token_lifetime = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
                refresh_token_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']

            tokens = self.get_tokens_for_user(user, access_token_lifetime, refresh_token_lifetime)

            response = Response({
                'code': 200,
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                }
            }, status=status.HTTP_200_OK)

            # Set access token cookie
            set_token_cookie(response, 'access', tokens['access'])
            # Set refresh token cookie
            set_token_cookie(response, 'refresh', tokens['refresh'])

            return response

        except serializers.ValidationError:
            # Customize the error response
            return Response(
                {
                    'code': 401,
                    'message': 'Invalid username or password'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

    def get_tokens_for_user(self, user, access_lifetime, refresh_lifetime):
        """
        Generates token pair for the authenticated user.
        """
        refresh = RefreshToken.for_user(user)
        refresh.set_exp(lifetime=refresh_lifetime)
        access = refresh.access_token
        access.set_exp(lifetime=access_lifetime)
        return {
            'refresh': str(refresh),
            'access': str(access),
        }


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @ratelimit(key='ip', rate=settings.RATE_LIMIT_LOGIN)  # Assuming same rate limit as login
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_COOKIE'])
        if not refresh_token:
            res = {
                'code': 400,
                'message': 'Refresh token is required'
            }
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()

                res = {'code': 200, 'message': 'Logout successful'}
                response = Response(
                    res,
                    status=status.HTTP_200_OK
                )
            except TokenError as e:
                res = {
                    'code': 400,
                    'message': f'Invalid token, error is {e}'
                }
                response = Response(res, status=status.HTTP_400_BAD_REQUEST)

            # Remove the tokens by deleting the cookies
            response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'], path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'])
            response.delete_cookie(settings.SIMPLE_JWT['REFRESH_COOKIE'], path=settings.SIMPLE_JWT['REFRESH_COOKIE_PATH'])

            return response


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        user = request.user
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
        return Response({'code': 200, 'data': data})


class TokenValidityView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    @ratelimit(key='ip', rate=settings.RATE_LIMIT_LOGIN)
    def get(self, request):
        access_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE'])
        if access_token:
            try:
                exp_ts = access_token['exp']
                issued_at_ts = access_token['iat']

                exp_datetime = datetime.fromtimestamp(exp_ts, timezone.utc)
                iat_datetime = datetime.fromtimestamp(issued_at_ts, timezone.utc)
                now = datetime.now(timezone.utc)

                time_left = (exp_datetime - now).total_seconds()
                token_lifetime = (exp_datetime - iat_datetime).total_seconds()

                return Response({'code': 200, 'valid': True, 'data': {'time_left': time_left, 'token_lifetime': token_lifetime}})
            except (IndexError, TokenError, InvalidToken):
                return Response({'code': 400, 'valid': False, 'message': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'code': 400,
                'valid': False,
                'message': 'Authorization header missing'
            }, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(SimpleJWTTokenRefreshView):
    permission_classes = [AllowAny]

    @ratelimit(key='ip', rate=settings.RATE_LIMIT_REFRESH)
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_COOKIE'])
        if not refresh_token:
            res = {
                'code': 400,
                'message': 'No refresh token provided'
            }
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

        data = {'refresh': refresh_token}
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response({
                'code': 401,
                'message': f'Invalid or expired refresh token: {str(e)}'
            }, status=status.HTTP_401_UNAUTHORIZED)

        access = serializer.validated_data.get('access')
        new_refresh = serializer.validated_data.get('refresh')
        res = {
            'code': 200,
            'message': 'Token refreshed successfully'
        }
        response = Response(res, status=status.HTTP_200_OK)
        # Set new access token cookie
        if access:
            set_token_cookie(response, 'access', access)
        # Set new refresh token cookie if rotation is enabled and a new refresh token is issued
        if new_refresh:
            set_token_cookie(response, 'refresh', new_refresh)

        return response


class GetCSRFTokenView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    @ratelimit(key='ip', rate=settings.RATE_LIMIT_CSRF)
    def get(self, request):
        return Response({'detail': 'CSRF cookie set'}, status=status.HTTP_200_OK)