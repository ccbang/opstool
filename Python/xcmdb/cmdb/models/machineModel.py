from django.db import models
from .xroleModel import Roles
from django.contrib.postgres.fields import ArrayField, JSONField


class Machines(models.Model):
    role = models.ForeignKey(Roles)
    mac_address = models.CharField("MAC地址", max_length=255)
    machine_ip = JSONField('IP信息', default=dict)
