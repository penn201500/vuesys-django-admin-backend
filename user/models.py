from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class SysUser(AbstractUser):
    avatar = models.CharField(max_length=255, null=True, verbose_name="Avatar")
    email = models.CharField(max_length=100, null=True, verbose_name="Email")
    phone = models.CharField(max_length=11, null=True, verbose_name="Phone")
    status = models.IntegerField(null=True, verbose_name="Status")
    create_time = models.DateTimeField(null=True, verbose_name="Create Time")
    update_time = models.DateTimeField(null=True, verbose_name="Update Time")
    comment = models.CharField(max_length=500, null=True, verbose_name="Comment")

    class Meta:
        db_table = "sys_user"
