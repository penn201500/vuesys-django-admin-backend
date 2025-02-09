from rest_framework import serializers
from .models import SysRole

RESERVED_ROLE_CODE = ["admin", "common"]  # Only admin and common is reserved


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
        extra_kwargs = {
            "remark": {"required": False, "allow_null": True}  # Make remark optional
        }

    def validate_code(self, value):
        """
        Validate that the role code is unique and not one of the reserved code
        """
        # Convert to lowercase for comparison
        value = value.lower()

        if value in RESERVED_ROLE_CODE:
            raise serializers.ValidationError("Cannot use reserved system role code")

        # Check for uniqueness, excluding soft-deleted roles
        if SysRole.objects.filter(code=value, deleted_at__isnull=True).exists():
            if self.instance and self.instance.code.lower() == value:
                return value
            raise serializers.ValidationError("Role with this code already exists")
        return value

    def validate(self, attrs):
        """
        Additional validation to prevent modifying admin role
        """
        # If this is an update operation
        if self.instance and self.instance.code == RESERVED_ROLE_CODE:
            raise serializers.ValidationError("Cannot modify admin role")
        return attrs
