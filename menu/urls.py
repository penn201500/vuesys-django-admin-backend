from django.urls import path
from .views import MenuListView, MenuDetailView, MenuCreateView

urlpatterns = [
    path("api/menus/", MenuListView.as_view(), name="menu-list"),
    path("api/menus/<int:pk>/", MenuDetailView.as_view(), name="menu-detail"),
    path("api/menus/create/", MenuCreateView.as_view(), name="menu-create"),
]
