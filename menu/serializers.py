from rest_framework import serializers
from menu.models import SysMenu


class MenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()

    class Meta:
        model = SysMenu
        fields = [
            "id",
            "name",
            "icon",
            "parent_id",
            "order_num",
            "path",
            "component",
            "perms",
            "status",
            "create_time",
            "update_time",
            "remark",
            "children",
            "has_children",
        ]

    def get_children(self, obj):
        if hasattr(obj, "children"):
            return MenuSerializer(obj.children, many=True).data
        return []

    def get_has_children(self, obj):
        return hasattr(obj, "children") and bool(obj.children)
