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
    path("api/login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/token/validity/", TokenValidityView.as_view(), name="token_validity"),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("api/csrf/", GetCSRFTokenView.as_view(), name="csrf"),
    path("api/signup/", SignupView.as_view(), name="signup"),
    # path("api/profile/update/", UserProfileUpdateView.as_view(), name="profile-update"),
    # path("api/profile/avatar/", AvatarUpdateView.as_view(), name="avatar-update"),
    # path("api/profile/roles/", UserRoleUpdateView.as_view(), name="user-role-update"),
    # Add new admin routes for managing other users
    # roles
    # fetch roles url in roles/urls.py
    path(
        "api/users/<int:user_id>/roles/",
        UserRoleUpdateView.as_view(),
        name="user-role-update",
    ),
    # avatar
    path("api/profile/get-avatar/", UserAvatarView.as_view(), name="get-avatar"),
    path(
        "api/users/<int:user_id>/avatar/",
        AvatarUpdateView.as_view(),
        name="user-avatar-update",
    ),
    # password
    path("api/profile/password/", PasswordUpdateView.as_view(), name="password-update"),
    path(
        "api/users/<int:user_id>/password/",
        PasswordUpdateView.as_view(),
        name="user-password-update",
    ),
    # user
    path("api/users/", UserListView.as_view(), name="user-list"),
    path("api/user-info/", UserInfoView.as_view(), name="user_info"),
    path(
        "api/users/<int:user_id>/",
        UserProfileDetailView.as_view(),
        name="user-profile-detail",
    ),
    path(
        "api/users/<int:user_id>/update/",
        UserProfileUpdateView.as_view(),
        name="user-profile-update",
    ),
]
