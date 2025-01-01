from rest_framework import permissions


class AuditAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if user has either admin or common role
        return request.user.roles.filter(code__in=["admin", "common"]).exists()
