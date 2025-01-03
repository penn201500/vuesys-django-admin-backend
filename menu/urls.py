from django.urls import path
from .views import (
    MenuListView,
    MenuDetailView,
    MenuCreateView,
    MenuReorderView,
    UserMenuView,
)

urlpatterns = [
    path("menus/", MenuListView.as_view(), name="menu-list"),
    path("menus/<int:pk>/", MenuDetailView.as_view(), name="menu-detail"),
    path("menus/create/", MenuCreateView.as_view(), name="menu-create"),
    path("menus/reorder/", MenuReorderView.as_view(), name="menu-reorder"),
    path("user-menus/", UserMenuView.as_view(), name="user-menus"),  # For current user
    path(
        "users/<int:user_id>/menus/",
        UserMenuView.as_view(),
        name="user-specific-menus",
    ),  # For specific user
]
