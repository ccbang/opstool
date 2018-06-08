from django.db import models



class UserGroup(models.Model):
    group_name = models.CharField('组名称', max_length=100)
    pp_id = models.IntegerField('父组ID', default=0)


class Users(models.Model):
    user_name = models.CharField('用户名称', max_length=200)


class Roles(models.Model):
    user = models.ForeignKey(Users)
    user_group = models.ForeignKey(UserGroup)
    role_ame = models.CharField('角色名', max_length=100)


