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
