# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from user.models import SysUser
from datetime import datetime, timezone
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator


# Create your views here.
# Replace the LoginView with the following code
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view to handle JWT authentication and return custom response structure.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.user
            tokens = self.get_tokens_for_user(user)

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
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=tokens['access'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
            )

            # Set refresh token cookie
            response.set_cookie(
                key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
                value=tokens['refresh'],
                httponly=settings.SIMPLE_JWT['REFRESH_COOKIE_HTTP_ONLY'],
                secure=settings.SIMPLE_JWT['REFRESH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['REFRESH_COOKIE_SAMESITE'],
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                path=settings.SIMPLE_JWT['REFRESH_COOKIE_PATH'],
            )

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

    def get_tokens_for_user(self, user):
        """
        Generates token pair for the authenticated user.
        """
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_COOKIE'])
        if not refresh_token:
            res = {
                'code': 400,
                'message': 'Refresh token is required'
            }
            return Response(res, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            res = {'code': 200, 'message': 'Logout successful'},
            response = Response(
                res,
                status=status.HTTP_200_OK
            )

            # Remove the tokens by deleting the cookies
            response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'], path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'])
            response.delete_cookie(settings.SIMPLE_JWT['REFRESH_COOKIE'], path=settings.SIMPLE_JWT['REFRESH_COOKIE_PATH'])

            return response

        except TokenError:
            res = {
                'code': 400,
                'message': 'Invalid token'
            }
            return Response(res, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

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
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if auth_header:
            try:
                token_str = auth_header.split(' ')[1]
                token = AccessToken(token_str)
                exp_ts = token['exp']
                exp_datetime = datetime.fromtimestamp(exp_ts, timezone.utc)
                now = datetime.now(timezone.utc)
                time_left = exp_datetime - now
                return Response({'code': 200, 'valid': True, 'data': {'time_left': time_left.total_seconds()}})
            except (IndexError, TokenError, InvalidToken):
                return Response({'code': 400, 'valid': False, 'message': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'code': 400, 'valid': False, 'message': 'Authorization header missing'}, status=status.HTTP_400_BAD_REQUEST)


class GetCSRFTokenView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({'detail': 'CSRF cookie set'}, status=status.HTTP_200_OK)
