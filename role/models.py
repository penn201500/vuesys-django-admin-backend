from django.db import models
from rest_framework import serializers

from user.models import SysUser


# Create your models here.


class SysRole(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, null=True, verbose_name="Role Name")
    code = models.CharField(
        max_length=100, null=True, verbose_name="Role Permission Code"
    )
    create_time = models.DateField(
        null=True,
        verbose_name="Created Time",
    )
    update_time = models.DateField(null=True, verbose_name="Updated Time")
    remark = models.CharField(max_length=500, null=True, verbose_name="Comment Time")

    class Meta:
        db_table = "sys_role"


class SysRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysRole
        fields = "__all__"


class SysUserRole(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(SysRole, on_delete=models.PROTECT)
    user = models.ForeignKey(SysUser, on_delete=models.PROTECT)

    class Meta:
        db_table = "sys_user_role"


class SysUserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysUserRole
        fields = "__amll__"
