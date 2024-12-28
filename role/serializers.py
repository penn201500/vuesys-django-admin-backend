from rest_framework import serializers
from .models import SysRole


class SysRoleSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = SysRole
        fields = [
            "id",
            "name",
            "code",
            "status",
            "is_system",
            "create_time",
            "update_time",
            "remark",
            "is_active",
        ]
        read_only_fields = ["is_system", "create_time", "update_time"]

    def validate_code(self, value):
        """
        Validate that the role code is unique and not a system role code
        """
        if value in ["admin", "common"]:
            raise serializers.ValidationError("Cannot use reserved system role codes")

        # Check for uniqueness, excluding soft-deleted roles
        if SysRole.objects.filter(code=value, deleted_at__isnull=True).exists():
            if self.instance and self.instance.code == value:
                return value
            raise serializers.ValidationError("Role with this code already exists")
        return value
