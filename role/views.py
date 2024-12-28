from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import SysRole
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
