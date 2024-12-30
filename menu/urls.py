from django.urls import path
from .views import MenuListView, MenuDetailView

urlpatterns = [
    path("api/menus/", MenuListView.as_view(), name="menu-list"),
    path("api/menus/<int:pk>/", MenuDetailView.as_view(), name="menu-detail"),
]
