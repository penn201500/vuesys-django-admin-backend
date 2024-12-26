from django.urls import path
from user.views import (
    TokenValidityView,
    UserInfoView,
    LogoutView,
    CustomTokenObtainPairView,
    GetCSRFTokenView,
    CustomTokenRefreshView,
    SignupView,
    ProfileUpdateView,
    PasswordUpdateView,
    AvatarUpdateView,
    UserAvatarView,
    UserListView,
    UserRoleUpdateView,
)

urlpatterns = [
    path("api/login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/user-info/", UserInfoView.as_view(), name="user_info"),
    path("api/token/validity/", TokenValidityView.as_view(), name="token_validity"),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("api/csrf/", GetCSRFTokenView.as_view(), name="csrf"),
    path("api/signup/", SignupView.as_view(), name="signup"),
    path("api/profile/update/", ProfileUpdateView.as_view(), name="profile-update"),
    path("api/profile/password/", PasswordUpdateView.as_view(), name="password-update"),
    path("api/profile/avatar/", AvatarUpdateView.as_view(), name="avatar-update"),
    path("api/profile/get-avatar/", UserAvatarView.as_view(), name="get-avatar"),
    path("api/users/", UserListView.as_view(), name="user-list"),
    path("api/profile/roles/", UserRoleUpdateView.as_view(), name="user-role-update"),
]
