from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from user.authentication import CookieJWTAuthentication
from role.models import SysUserRole
from .models import SysMenu, SysRoleMenu


class UserMenuView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        # Get all roles associated with the logged-in user
        user_roles = SysUserRole.objects.filter(user_id=request.user.id).values_list(
            "role_id", flat=True
        )
        # Get all menu IDs associated with these roles
        menu_ids = (
            SysRoleMenu.objects.filter(role_id__in=user_roles)
            .values_list("menu_id", flat=True)
            .distinct()
        )
        # Fetch the menus and order them by `order_num`
        menus = SysMenu.objects.filter(id__in=menu_ids).order_by("order_num")
        # Build a hierarchical menu structure
        menu_data = self.build_menu_hierarchy(menus)
        return Response({"code": 200, "data": menu_data}, status=200)

    def build_menu_hierarchy(self, menus):
        # Convert queryset to a list of dicts for easier processing
        menu_list = list(
            menus.values(
                "id",
                "name",
                "icon",
                "parent_id",
                "order_num",
                "path",
                "component",
                "menu_type",
                "perms",
                "create_time",
                "update_time",
                "remark",
            )
        )

        # Create a dictionary of menus keyed by parent_id
        menu_dict = {}
        for m in menu_list:
            parent_id = m["parent_id"] if m["parent_id"] else 0
            menu_dict.setdefault(parent_id, []).append(m)

        # Recursively build the tree
        def build_tree(parent_id=0):
            children = []
            for menu in menu_dict.get(parent_id, []):
                menu["children"] = build_tree(menu["id"])
                children.append(menu)
            return children

        return build_tree()
