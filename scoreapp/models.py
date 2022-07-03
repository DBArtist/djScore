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

class RoomUser(models.Model):
    """ 房间用户 """
    room = models.ForeignKey(verbose_name="房间",to="Room", to_field="id", on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name="用户",to="UserInfo", to_field="id", on_delete=models.CASCADE)
    position_choices = ((1, "东"), (2, "南"),(3, "西"),(4, "北"),)
    position = models.SmallIntegerField(verbose_name="方位",choices=position_choices)
    create_time = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="最近更新时间",auto_now=True)

class GameRecord(models.Model):
    """ 游戏对局接结果记录 """
    round_id = models.CharField(verbose_name="游戏对局ID",max_length=32)
    room = models.ForeignKey(verbose_name="房间",to="Room", to_field="id", on_delete=models.CASCADE)
    user_east = models.ForeignKey(verbose_name="东方用户",to="UserInfo", to_field="id", on_delete=models.CASCADE,related_name="fk_ue")
    user_south = models.ForeignKey(verbose_name="西方用户",to="UserInfo", to_field="id", on_delete=models.CASCADE,related_name="fk_us")
    user_west = models.ForeignKey(verbose_name="南方用户",to="UserInfo", to_field="id", on_delete=models.CASCADE,related_name="fk_uw")
    user_north = models.ForeignKey(verbose_name="北方用户",to="UserInfo", to_field="id", on_delete=models.CASCADE,related_name="fk_un")
    score_east = models.IntegerField(verbose_name="东方用户输赢积分",default=0)
    score_south = models.IntegerField(verbose_name="男方用户输赢积分",default=0)
    score_west = models.IntegerField(verbose_name="西方用户输赢积分",default=0)
    score_north = models.IntegerField(verbose_name="北方用户输赢积分",default=0)
    result_choices = ((-1, "输"),(1, "赢"),)
    result_east = models.SmallIntegerField(verbose_name="东方用户游戏结果",choices=result_choices,default=-1)
    result_south = models.SmallIntegerField(verbose_name="南方用户游戏结果",choices=result_choices,default=-1)
    result_west = models.SmallIntegerField(verbose_name="西方用户游戏结果",choices=result_choices,default=-1)
    result_north = models.SmallIntegerField(verbose_name="北方用户游戏结果",choices=result_choices,default=-1)
    type_choices = ((1, "任意人添加"),(2, "赢家添加"),)
    record_type = models.SmallIntegerField(verbose_name="记录类型",choices=type_choices,default=1)
    status_choices = ((1, "待确认"),(2, "已确认"),)
    record_status = models.SmallIntegerField(verbose_name="记录状态",choices=status_choices,default=1)
    create_time = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="最近更新时间",auto_now=True)




