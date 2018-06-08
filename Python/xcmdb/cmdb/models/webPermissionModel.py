from django.db import models
from .xpermissionModel import XPermission


class Menu(models.Model):
    xpermission = models.ForeignKey(XPermission)
    name = models.CharField("菜单名称", max_length=100)
    this_url = models.CharField("URL", max_length=255)
    ppid = models.IntegerField("父菜单", default=0)