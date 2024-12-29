from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from user.authentication import CookieJWTAuthentication
from .models import SysMenu
from .serializers import MenuSerializer


class AdminRequiredMixin:
    def check_admin(self, request):
        if not request.user.roles.filter(code="admin").exists():
            return Response(
                {"code": 403, "message": "Admin privileges required"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None


class MenuListView(AdminRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        admin_check = self.check_admin(request)
        if admin_check:
            return admin_check

        try:
            search = request.query_params.get("search", "").strip()
            queryset = SysMenu.objects.filter(deleted_at__isnull=True)

            # Apply search if provided
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search)
                    | Q(path__icontains=search)
                    | Q(component__icontains=search)
                    | Q(perms__icontains=search)
                    | Q(remark__icontains=search)
                )

            # Build tree structure
            menu_tree = self.build_menu_tree(queryset)

            return Response({"code": 200, "message": "Success", "data": menu_tree})
        except Exception as e:
            return Response(
                {"code": 500, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def build_menu_tree(self, queryset):
        menu_dict = {}
        for menu in queryset:
            menu_dict[menu.id] = menu
            menu.children = []

        root_menus = []
        for menu in queryset:
            if menu.parent_id and menu.parent_id in menu_dict:
                menu_dict[menu.parent_id].children.append(menu)
            else:
                root_menus.append(menu)

        return MenuSerializer(root_menus, many=True).data
