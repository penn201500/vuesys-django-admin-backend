from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from menu.models import SysMenu, SysRoleMenu
from user.views import CustomPageNumberPagination
from .models import SysRole, SysUserRole
from .serializers import SysRoleSerializer
from user.authentication import CookieJWTAuthentication


class AdminRequiredMixin:
    """Mixin to check if user has admin role"""

    def check_admin(self, request):
        if not request.user.roles.filter(code="admin").exists():
            return Response(
                {"code": 403, "message": "Admin privileges required"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None


class RoleListView(AdminRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    pagination_class = CustomPageNumberPagination

    def get(self, request):
        # Check admin permission
        admin_check = self.check_admin(request)
        if admin_check:
            return admin_check

        try:
            # Get query parameters
            search_query = request.query_params.get("search", "").strip()

            # Base queryset - exclude soft deleted roles
            queryset = SysRole.objects.filter(deleted_at__isnull=True)

            # Apply search if provided
            if search_query:
                queryset = queryset.filter(
                    Q(name__icontains=search_query)
                    | Q(code__icontains=search_query)
                    | Q(remark__icontains=search_query)
                )

            # Apply ordering
            ordering = request.query_params.get("ordering", "-create_time")
            if ordering:
                queryset = queryset.order_by(ordering)

            # Apply pagination
            paginator = self.pagination_class()
            paginated_users = paginator.paginate_queryset(queryset, request)

            serializer = SysRoleSerializer(queryset, many=True)
            return Response(
                {
                    "code": 200,
                    "message": "Roles retrieved successfully",
                    "data": serializer.data,
                    "count": queryset.count(),
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

    def post(self, request):
        # Check admin permission
        admin_check = self.check_admin(request)
        if admin_check:
            return admin_check

        serializer = SysRoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "code": 200,
                    "message": "Role created successfully",
                    "data": serializer.data,
                }
            )
        return Response(
            {"code": 400, "message": "Invalid data", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class RoleDetailView(AdminRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    @staticmethod
    def get_object(pk):
        try:
            return SysRole.objects.get(pk=pk, deleted_at__isnull=True)
        except SysRole.DoesNotExist:
            return None

    def get(self, request, pk):
        """Get role details"""
        admin_check = self.check_admin(request)
        if admin_check:
            return admin_check

        role = self.get_object(pk)
        if not role:
            return Response(
                {"code": 404, "message": "Role not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SysRoleSerializer(role)
        return Response({"code": 200, "data": serializer.data})

    def put(self, request, pk):
        """Update role"""
        admin_check = self.check_admin(request)
        if admin_check:
            return admin_check

        role = self.get_object(pk)
        if not role:
            return Response(
                {"code": 404, "message": "Role not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if role.is_system:
            return Response(
                {"code": 400, "message": "System roles cannot be modified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SysRoleSerializer(role, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "code": 200,
                    "message": "Role updated successfully",
                    "data": serializer.data,
                }
            )
        return Response(
            {"code": 400, "message": "Invalid data", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        """Soft delete role"""
        admin_check = self.check_admin(request)
        if admin_check:
            return admin_check

        role = self.get_object(pk)
        if not role:
            return Response(
                {"code": 404, "message": "Role not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if role.is_system:
            return Response(
                {"code": 400, "message": "System roles cannot be deleted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if role is in use
        user_count = SysUserRole.objects.filter(role=role).count()
        if user_count > 0:
            return Response(
                {
                    "code": 400,
                    "message": f"Role is assigned to {user_count} users and cannot be deleted",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Perform soft delete
        role.soft_delete()
        return Response({"code": 200, "message": "Role deleted successfully"})


class RoleStatusView(AdminRequiredMixin, APIView):
    """Toggle role active status"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request, pk):
        admin_check = self.check_admin(request)
        if admin_check:
            return admin_check

        role = SysRole.objects.filter(pk=pk, deleted_at__isnull=True).first()
        if not role:
            return Response(
                {"code": 404, "message": "Role not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if role.is_system:
            return Response(
                {"code": 400, "message": "System roles status cannot be modified"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Toggle status
        role.status = 0 if role.status == 1 else 1
        role.save()

        serializer = SysRoleSerializer(role)
        return Response(
            {
                "code": 200,
                "message": "Role status updated successfully",
                "data": serializer.data,
            }
        )


class RoleMenuView(AdminRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request, pk):
        """Get role's menu items"""
        role = SysRole.objects.filter(pk=pk, deleted_at__isnull=True).first()
        if not role:
            return Response(
                {"code": 404, "message": "Role not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        menu_ids = SysRoleMenu.objects.filter(role=role).values_list(
            "menu_id", flat=True
        )
        return Response(
            {"code": 200, "data": {"role_id": role.id, "menu_ids": list(menu_ids)}}
        )

    def put(self, request, pk):
        """Update role's menu items"""
        role = SysRole.objects.filter(pk=pk, deleted_at__isnull=True).first()
        if not role:
            return Response(
                {"code": 404, "message": "Role not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        menu_ids = request.data.get("menu_ids", [])
        # Clear existing and create new
        SysRoleMenu.objects.filter(role=role).delete()
        SysRoleMenu.objects.bulk_create(
            [SysRoleMenu(role=role, menu_id=menu_id) for menu_id in menu_ids]
        )

        return Response({"code": 200, "message": "Menu items updated successfully"})


class MenuTreeView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def build_tree(self, menus):
        menu_map = {menu.id: menu for menu in menus}
        tree = []

        for menu in menus:
            if menu.parent_id is None or menu.parent_id == 0:
                # Root level menu
                tree.append(self._format_menu_item(menu, menu_map))
        return tree

    def _format_menu_item(self, menu, menu_map):
        children = []
        for potential_child in menu_map.values():
            if potential_child.parent_id == menu.id:
                children.append(self._format_menu_item(potential_child, menu_map))

        menu_dict = {
            "id": menu.id,
            "name": menu.name,
        }
        if children:
            menu_dict["children"] = children
        return menu_dict

    def get(self, request):
        try:
            menus = SysMenu.objects.filter(status=1, deleted_at__isnull=True).order_by(
                "order_num"
            )
            tree = self.build_tree(menus)
            return Response(
                {
                    "code": 200,
                    "message": "Menu tree retrieved successfully",
                    "data": tree,
                }
            )
        except Exception as e:
            return Response({"code": 500, "message": str(e)}, status=500)
