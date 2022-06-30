from django.db import models

class UserInfo(models.Model):
    """ 用户信息表 """
    user_account = models.CharField(verbose_name="用户账号",max_length=16)
    user_password = models.CharField(verbose_name="账号密码",max_length=64,default='')
    user_nick = models.CharField(verbose_name="用户昵称",max_length=32)
    mobile = models.CharField(verbose_name="手机号",max_length=16)
    gender_choices = ((1,"男"),(0,"女"),)
    gender = models.SmallIntegerField(verbose_name="性别",choices=gender_choices)
    birthday = models.DateField(verbose_name="生日",default="2000-01-01")
    create_time = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="最近更新时间",auto_now=True)




class Room(models.Model):
    """ 房间表 """
    roomname = models.CharField(verbose_name="房间名称",max_length=16)
    roomstatus_choices = ((1, "空闲中"), (2, "游戏中"),(3, "结算中"),(4, "已关闭"),)
    roomstatus = models.SmallIntegerField(verbose_name="房间状态",choices=roomstatus_choices)
    owner = models.ForeignKey(verbose_name="房主",to="UserInfo", to_field="id", on_delete=models.CASCADE)
    create_time = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="最近更新时间",auto_now=True)














