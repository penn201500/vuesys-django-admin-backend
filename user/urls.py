from django.urls import path
from user.views import TokenValidityView, UserInfoView, LogoutView, CustomTokenObtainPairView, GetCSRFTokenView, TokenRefreshView

urlpatterns = [
    path('api/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/user-info/', UserInfoView.as_view(), name='user_info'),
    path('api/token/validity/', TokenValidityView.as_view(), name='token_validity'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/csrf/', GetCSRFTokenView.as_view(), name='csrf'),
]
