from django.db import models
from rest_framework import serializers

from role.models import SysRole


# Create your models here.


class SysMenu(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, verbose_name="Menu Name")
    title = models.CharField(
        max_length=100, null=True, verbose_name="Display Title"
    )  # Added
    icon = models.CharField(max_length=100, null=True, verbose_name="Menu Icon")
    parent_id = models.IntegerField(null=True, verbose_name="Parent Menu ID")
    order_num = models.IntegerField(null=True, verbose_name="Order")
    path = models.CharField(max_length=200, null=True, verbose_name="Router")
    component = models.CharField(max_length=255, null=True, verbose_name="Path")
    menu_type = models.CharField(
        max_length=1, null=True, verbose_name="Menu Type（Catalog Menu Button）"
    )
    perms = models.CharField(max_length=100, null=True, verbose_name="Permission")
    keep_alive = models.BooleanField(
        default=False, verbose_name="Keep Tab State"
    )  # Added
    create_time = models.DateField(
        null=True,
        verbose_name="Created Time",
    )
    update_time = models.DateField(null=True, verbose_name="Updated Time")
    remark = models.CharField(max_length=500, null=True, verbose_name="Comment")

    def __lt__(self, other):
        return self.order_num < other.order_num

    class Meta:
        db_table = "sys_menu"


class SysMenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        if hasattr(obj, "children"):
            serializerMenuList: list[SysMenuSerializer2] = list()
            for sysMenu in obj.children:
                serializerMenuList.append(SysMenuSerializer2(sysMenu).data)
            return serializerMenuList

    class Meta:
        model = SysMenu
        fields = "__all__"


class SysRoleMenu(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(SysRole, on_delete=models.PROTECT)
    menu = models.ForeignKey(SysMenu, on_delete=models.PROTECT)

    class Meta:
        db_table = "sys_role_menu"


class SysRoleMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysRoleMenu
        fields = "__all__"
