from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from user.models import SysUser


# Create your views here.
class TestView(View):
    def get(self, request):
        users = list(SysUser.objects.all().values())
        res = {
            'code': 200,
            'data': users
        }
        return JsonResponse(res)