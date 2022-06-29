from django.db import models

class UserInfo(models.Model):
    """ 用户信息表 """
    user_account = models.CharField(verbose_name="用户账号",max_length=16)
    user_password = models.CharField(verbose_name="账号密码",max_length=64,default='')
    user_nick    = models.CharField(verbose_name="用户昵称",max_length=32)
    mobile = models.CharField(verbose_name="手机号",max_length=16)
    gender_choices = ((1,"男"),(0,"女"),)
    gender = models.SmallIntegerField(verbose_name="性别",choices=gender_choices)
    create_time = models.DateField(verbose_name="创建时间",auto_created=True)
    update_time = models.DateTimeField(verbose_name="最近更新时间",auto_now=True)




















