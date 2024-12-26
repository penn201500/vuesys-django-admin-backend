from django.urls import path
from .views import RoleListView

urlpatterns = [
    path("api/roles/", RoleListView.as_view(), name="role-list"),
]
