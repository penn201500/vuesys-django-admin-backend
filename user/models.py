from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# Create your models here.
class SysUser(AbstractUser):
    avatar = models.CharField(max_length=255, null=True, verbose_name="Avatar")
    email = models.CharField(max_length=100, null=True, verbose_name="Email")
    phone = models.CharField(max_length=11, null=True, verbose_name="Phone")
    status = models.IntegerField(null=True, verbose_name="Status")
    create_time = models.DateTimeField(null=True, verbose_name="Create Time")
    update_time = models.DateTimeField(null=True, verbose_name="Update Time")
    comment = models.CharField(max_length=500, null=True, verbose_name="Comment")
    deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Deletion Date"
    )  # For soft delete

    class Meta:
        db_table = "sys_user"

    @property
    def roles(self):
        from role.models import SysRole

        return SysRole.objects.filter(sysuserrole__user=self)

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.status = 0
        self.save()

    @property
    def is_active(self):
        return self.status == 1 and not self.deleted_at
