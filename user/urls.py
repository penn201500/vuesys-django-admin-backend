from django.urls import path

from user.views import TestView

urlpatterns = [
    path('test/', TestView.as_view(), name='test')
]