# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from .serializers import LoginSerializer
from user.models import SysUser
from datetime import datetime, timezone


# Create your views here.
class TestView(APIView):
    permission_classes = [AllowAny]  # No authentication required

    def get(self, request):
        users = list(SysUser.objects.all().values())
        res = {
            'code': 200,
            'data': users
        }
        return Response(res)


# @method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow any user to access

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)

            res = {
                'code': 200,
                'data': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
                'message': 'Login successful'
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            res = {
                'code': 401,
                'message': 'Invalid username or password'
            }
            return Response(res, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                res = {
                    'code': 400,
                    'message': 'Refresh token is required'
                }
                return Response(res, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            res = {
                'code': 200,
                'message': 'Logout successful'
            }
            return Response(res, status=status.HTTP_200_OK)
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
