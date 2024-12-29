from django.db import models
from rest_framework import serializers
from django.utils import timezone

from user.models import SysUser


# Create your models here.


class SysRole(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, verbose_name="Role Name")
    code = models.CharField(max_length=100, verbose_name="Role Permission Code")
    status = models.IntegerField(
        default=1, verbose_name="Status"
    )  # 1: active, 0: inactive
    is_system = models.BooleanField(
        default=False, verbose_name="Is System Role"
    )  # For admin role
    deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Deletion Date"
    )  # For soft delete
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created Time",
    )
    update_time = models.DateTimeField(auto_now=True, verbose_name="Updated Time")
    remark = models.CharField(
        max_length=500, null=True, blank=True, verbose_name="Comment"
    )

    class Meta:
        db_table = "sys_role"

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.status = 0
        self.save()

    @property
    def is_active(self):
        return self.status == 1 and not self.deleted_at


class SysUserRole(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(SysRole, on_delete=models.PROTECT)
    user = models.ForeignKey(SysUser, on_delete=models.PROTECT)

    class Meta:
        db_table = "sys_user_role"
