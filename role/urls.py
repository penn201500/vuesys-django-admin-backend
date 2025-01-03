from django.urls import path
from .views import (
    RoleListView,
    RoleDetailView,
    RoleStatusView,
    RoleMenuView,
    MenuTreeView,
)

urlpatterns = [
    path("roles/", RoleListView.as_view(), name="role-list"),
    path("roles/<int:pk>/", RoleDetailView.as_view(), name="role-detail"),
    path("roles/<int:pk>/status/", RoleStatusView.as_view(), name="role-status"),
    path("roles/<int:pk>/menus/", RoleMenuView.as_view(), name="role-menus"),
    path("roles/menu-tree/", MenuTreeView.as_view(), name="menu-tree"),
]
