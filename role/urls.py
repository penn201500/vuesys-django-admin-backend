from django.urls import path
from .views import RoleListView, RoleDetailView

urlpatterns = [
    path("api/roles/", RoleListView.as_view(), name="role-list"),
    path("api/roles/<int:pk>/", RoleDetailView.as_view(), name="role-detail"),
]
