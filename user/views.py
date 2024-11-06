from debugpy.adapter import access_token
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
    permission_classes = [IsAuthenticated]  # Allow any user (authenticated or not) to hit this endpoint

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

# class JwtTestView(APIView):
#     permission_classes = [IsAuthenticated]  # Require authentication
#     authentication_classes = [JWTAuthentication]
#
#     def get(self, request):
#         user = SysUser.objects.get(username='admin', password='test')
#         # Generate tokens
#         refresh = RefreshToken.for_user(user)
#         access_token = str(refresh.access_token)
#
#         res = {
#             'code': 200,
#             'data': access_token,
#             'refresh': str(refresh)
#         }
#         return JsonResponse(res)
