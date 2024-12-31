from django.urls import path
from .views import (
    RoleListView,
    RoleDetailView,
    RoleStatusView,
    RoleMenuView,
    MenuTreeView,
)

urlpatterns = [
    path("api/roles/", RoleListView.as_view(), name="role-list"),
    path("api/roles/<int:pk>/", RoleDetailView.as_view(), name="role-detail"),
    path("api/roles/<int:pk>/status/", RoleStatusView.as_view(), name="role-status"),
    path("api/roles/<int:pk>/menus/", RoleMenuView.as_view(), name="role-menus"),
    path("api/roles/menu-tree/", MenuTreeView.as_view(), name="menu-tree"),
]
