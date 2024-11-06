from django.urls import path
from user.views import TestView, LoginView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
    # path('jwt_test/', JwtTestView.as_view(), name='jwt_test'),
    path('api/login/', LoginView.as_view(), name='login'),
]
