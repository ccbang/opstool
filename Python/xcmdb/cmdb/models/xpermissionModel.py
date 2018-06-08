from django.db import models
from .xroleModel import  Roles


class XPermission(models.Model):
    role = models.ForeignKey(Roles)
    permission_type = models.CharField("权限类型", max_length=100)


class PermissionAction(models.Model):
    xpermission = models.ForeignKey(XPermission)
    action_name = models.CharField("操作名称", max_length=100)
    action_type = models.CharField("操作编码", max_length=100)
    cut_url = models.CharField("拦截URL前缀", max_length=255)
    ppid = models.IntegerField("父操作ID", default=0)

