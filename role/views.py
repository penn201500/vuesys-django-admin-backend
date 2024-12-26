from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import SysRole, SysUserRole, SysRoleSerializer
from user.authentication import CookieJWTAuthentication


class RoleListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        try:
            roles = SysRole.objects.all()
            serializer = SysRoleSerializer(roles, many=True)
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


class UserRoleUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        try:
            user = request.user
            role_ids = request.data.get("roles", [])

            if not role_ids:
                return Response(
                    {"code": 400, "message": "At least one role must be selected"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Prevent non-admin from managing admin role
            if not user.roles.filter(code="admin").exists():
                admin_role = SysRole.objects.filter(code="admin").first()
                if admin_role and admin_role.id in role_ids:
                    return Response(
                        {
                            "code": 403,
                            "message": "Cannot assign admin role without admin privileges",
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

            # Update user roles
            SysUserRole.objects.filter(user=user).delete()
            for role_id in role_ids:
                try:
                    role = SysRole.objects.get(id=role_id)
                    SysUserRole.objects.create(user=user, role=role)
                except SysRole.DoesNotExist:
                    continue

            return Response(
                {
                    "code": 200,
                    "message": "Roles updated successfully",
                    "data": {"roles": role_ids},
                }
            )

        except Exception as e:
            return Response(
                {"code": 500, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
