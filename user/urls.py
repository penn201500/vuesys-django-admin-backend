from django.urls import path
from user.views import LoginView, TokenValidityView, UserInfoView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView

urlpatterns = [
    path('api/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/user-info/', UserInfoView.as_view(), name='user_info'),
    path('api/token/validity/', TokenValidityView.as_view(), name='token_validity'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]