from django.urls import path
from .views import UserMenuView

urlpatterns = [
    path("user-menu/", UserMenuView.as_view(), name="user-menu"),
]
