from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
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

            serializer = SysRoleSerializer(queryset, many=True)
            return Response(
                {
                    "code": 200,
                    "message": "Roles retrieved successfully",
                    "data": serializer.data,
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
