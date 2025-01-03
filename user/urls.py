from django.urls import path
from user.views import (
    TokenValidityView,
    UserInfoView,
    LogoutView,
    CustomTokenObtainPairView,
    GetCSRFTokenView,
    CustomTokenRefreshView,
    SignupView,
    PasswordUpdateView,
    AvatarUpdateView,
    UserAvatarView,
    UserListView,
    UserRoleUpdateView,
    UserProfileDetailView,
    UserProfileUpdateView,
)

urlpatterns = [
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/validity/", TokenValidityView.as_view(), name="token_validity"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("csrf/", GetCSRFTokenView.as_view(), name="csrf"),
    path("signup/", SignupView.as_view(), name="signup"),
    # path("profile/update/", UserProfileUpdateView.as_view(), name="profile-update"),
    # path("profile/roles/", UserRoleUpdateView.as_view(), name="user-role-update"),
    # Add new admin routes for managing other users
    # roles
    # fetch roles url in roles/urls.py
    path(
        "users/<int:user_id>/roles/",
        UserRoleUpdateView.as_view(),
        name="user-role-update",
    ),
    # avatar
    path("profile/get-avatar/", UserAvatarView.as_view(), name="get-avatar"),
    path("profile/avatar/", AvatarUpdateView.as_view(), name="avatar-update"),
    path(
        "users/<int:user_id>/avatar/",
        AvatarUpdateView.as_view(),
        name="user-avatar-update",
    ),
    # password
    path("profile/password/", PasswordUpdateView.as_view(), name="password-update"),
    path(
        "users/<int:user_id>/password/",
        PasswordUpdateView.as_view(),
        name="user-password-update",
    ),
    # user
    path("users/", UserListView.as_view(), name="user-list"),
    path("user-info/", UserInfoView.as_view(), name="user_info"),
    path(
        "users/<int:user_id>/",
        UserProfileDetailView.as_view(),
        name="user-profile-detail",
    ),
    path(
        "users/<int:user_id>/update/",
        UserProfileUpdateView.as_view(),
        name="user-profile-update",
    ),
]
