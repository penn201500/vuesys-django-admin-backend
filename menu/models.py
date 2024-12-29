from django.db import models
from django.utils import timezone


from role.models import SysRole


# Create your models here.


class SysMenu(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name="Menu Name")
    icon = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Menu Icon"
    )
    parent_id = models.IntegerField(
        null=True, blank=True, verbose_name="Parent Menu ID"
    )
    order_num = models.IntegerField(default=0, verbose_name="Order")
    path = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Router Path"
    )
    component = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Component Path"
    )
    perms = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Permission String"
    )
    status = models.IntegerField(default=1, verbose_name="Status(0:disabled,1:enabled)")
    deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Deletion Time"
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Created Time")
    update_time = models.DateTimeField(auto_now=True, verbose_name="Updated Time")
    remark = models.CharField(
        max_length=500, null=True, blank=True, verbose_name="Comment"
    )

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.status = 0
        self.save()

    class Meta:
        db_table = "sys_menu"
        ordering = ["order_num"]


class SysRoleMenu(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(SysRole, on_delete=models.CASCADE)
    menu = models.ForeignKey(SysMenu, on_delete=models.CASCADE)

    class Meta:
        db_table = "sys_role_menu"
        unique_together = ["role", "menu"]
