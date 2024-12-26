from django.urls import path
from .views import RoleListView, UserRoleUpdateView

urlpatterns = [
    path("api/roles/", RoleListView.as_view(), name="role-list"),
    path("api/profile/roles/", UserRoleUpdateView.as_view(), name="user-role-update"),
]
