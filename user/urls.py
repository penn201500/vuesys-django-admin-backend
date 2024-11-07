from django.urls import path
from user.views import TestView, LoginView, TokenValidityView, UserInfoView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/user-info/', UserInfoView.as_view(), name='user_info'),
    path('api/token/validity/', TokenValidityView.as_view(), name='token_validity'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]