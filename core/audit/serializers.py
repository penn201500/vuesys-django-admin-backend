from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    # Convert GenericIPAddressField to CharField to avoid validation issues
    ip_address = serializers.CharField(allow_null=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "username",
            "user_email",
            "action",
            "module",
            "resource_type",
            "resource_id",
            "detail",
            "ip_address",
            "timestamp",
            "status",
            "message",
        ]
        read_only_fields = fields


class AuditLogFilterSerializer(serializers.Serializer):
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    user = serializers.CharField(required=False)
    action = serializers.ChoiceField(choices=AuditLog.ACTION_CHOICES, required=False)
    module = serializers.ChoiceField(choices=AuditLog.MODULE_CHOICES, required=False)
    search = serializers.CharField(required=False)
