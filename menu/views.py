from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from user.authentication import CookieJWTAuthentication
from user.views import CustomPageNumberPagination
from .models import SysMenu, SysRoleMenu
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
    pagination_class = CustomPageNumberPagination  # Add pagination class

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

            # Apply ordering
            ordering = request.query_params.get("ordering", "order_num")
            if ordering:
                queryset = queryset.order_by(ordering)

            # Build tree structure
            menu_tree = self.build_menu_tree(queryset)

            # Apply pagination
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(menu_tree, request)

            return Response(
                {
                    "code": 200,
                    "message": "Success",
                    "data": page,
                    "count": len(menu_tree),
                    "page": int(request.query_params.get("page", 1)),
                    "pageSize": int(
                        request.query_params.get("pageSize", paginator.page_size)
                    ),
                }
            )

        except Exception as e:
            return Response(
                {"code": 500, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    def build_menu_tree(queryset):
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


class MenuDetailView(AdminRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, pk):
        admin_check = self.check_admin(request)
        if admin_check:
            return admin_check

        try:
            menu = SysMenu.objects.get(id=pk, deleted_at__isnull=True)
            return Response({"code": 200, "data": MenuSerializer(menu).data})
        except SysMenu.DoesNotExist:
            return Response(
                {"code": 404, "message": "Menu not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request, pk):
        admin_check = self.check_admin(request)
        if admin_check:
            return admin_check

        try:
            menu = SysMenu.objects.get(id=pk, deleted_at__isnull=True)
            serializer = MenuSerializer(menu, data=request.data, partial=True)

            if serializer.is_valid():
                # Check if this would create a circular reference
                new_parent_id = request.data.get("parent_id")
                if new_parent_id and not self.is_valid_parent(pk, new_parent_id):
                    return Response(
                        {
                            "code": 400,
                            "message": "Invalid parent: would create circular reference",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                serializer.save()
                return Response(
                    {
                        "code": 200,
                        "message": "Menu updated successfully",
                        "data": serializer.data,
                    }
                )

            return Response(
                {"code": 400, "message": "Invalid data", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except SysMenu.DoesNotExist:
            return Response(
                {"code": 404, "message": "Menu not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, pk):
        admin_check = self.check_admin(request)
        if admin_check:
            return admin_check

        try:
            menu = SysMenu.objects.get(id=pk, deleted_at__isnull=True)

            # Check if menu has children
            if SysMenu.objects.filter(parent_id=pk, deleted_at__isnull=True).exists():
                return Response(
                    {"code": 400, "message": "Cannot delete menu with children"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Delete role-menu associations
            SysRoleMenu.objects.filter(menu=menu).delete()

            menu.soft_delete()
            return Response({"code": 200, "message": "Menu deleted successfully"})

        except SysMenu.DoesNotExist:
            return Response(
                {"code": 404, "message": "Menu not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def is_valid_parent(self, menu_id, parent_id):
        """Check if the parent_id would create a circular reference"""
        if menu_id == parent_id:
            return False

        current_id = parent_id
        while current_id is not None:
            try:
                menu = SysMenu.objects.get(id=current_id)
                if menu.parent_id == menu_id:
                    return False
                current_id = menu.parent_id
            except SysMenu.DoesNotExist:
                break

        return True


class MenuCreateView(AdminRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        admin_check = self.check_admin(request)
        if admin_check:
            return admin_check

        serializer = MenuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "code": 200,
                    "message": "Menu created successfully",
                    "data": serializer.data,
                }
            )
        return Response(
            {"code": 400, "message": "Invalid data", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class MenuReorderView(AdminRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        admin_check = self.check_admin(request)
        if admin_check:
            return admin_check

        try:
            items = request.data.get("items", [])
            parent_id = request.data.get("parent_id")

            for item in items:
                menu = SysMenu.objects.get(id=item["id"], deleted_at__isnull=True)
                menu.order_num = item["order_num"]
                menu.parent_id = parent_id
                menu.save()

            return Response({"code": 200, "message": "Menu order updated successfully"})
        except Exception as e:
            return Response(
                {"code": 500, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
