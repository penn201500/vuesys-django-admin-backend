from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from user.models import SysUser


# Create your views here.
class TestView(APIView):
    permission_classes = [AllowAny]  # Require authentication

    def get(self, request):
        users = list(SysUser.objects.all().values())
        res = {
            'code': 200,
            'data': users
        }
        return Response(res)


class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow any user (authenticated or not) to hit this endpoint

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
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
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


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
        return Response({'code': 200, 'data': data})
