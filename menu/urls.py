from django.urls import path
from .views import (
    MenuListView,
    MenuDetailView,
    MenuCreateView,
    MenuReorderView,
    UserMenuView,
)

urlpatterns = [
    path("api/menus/", MenuListView.as_view(), name="menu-list"),
    path("api/menus/<int:pk>/", MenuDetailView.as_view(), name="menu-detail"),
    path("api/menus/create/", MenuCreateView.as_view(), name="menu-create"),
    path("api/menus/reorder/", MenuReorderView.as_view(), name="menu-reorder"),
    path(
        "api/user-menus/", UserMenuView.as_view(), name="user-menus"
    ),  # For current user
    path(
        "api/users/<int:user_id>/menus/",
        UserMenuView.as_view(),
        name="user-specific-menus",
    ),  # For specific user
]
