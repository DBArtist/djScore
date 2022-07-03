from django import forms
from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from scoreapp import models
from scoreapp.utils.bootstrap import BootStrapModelForm, BootStrapForm
from scoreapp.utils.pagination import Pagination
import random
from datetime import datetime

class GameRecordModelForm(BootStrapModelForm):
    class Meta:
        model = models.GameRecord
        fields = ["score_east","result_east",
                  "score_south","result_south",
                  "score_west","result_west",
                  "score_north","result_north",]

        labels={
            "score_east" : "东积分",
            "score_south": "南积分",
            "score_west" : "西积分",
            "score_north": "北积分",

            "result_east" : "东输赢",
            "result_south": "南输赢",
            "result_west" : "西输赢",
            "result_north": "北输赢",
        }

class GameRecordWinnerModelForm(BootStrapModelForm):
    class Meta:
        model = models.UserInfo
        fields = ["user_nick"]

        labels={
            "user_nick" : "谁是赢家",
        }


def game_record_list(request,rid):
    """ 游戏记录列表 """
    if request.method == "GET":
        queryset = models.GameRecord.objects.filter(room=rid).order_by('-id')
        page_object = Pagination(request, queryset, page_size=50)

        form = GameRecordModelForm()
        # 获取房间用户列表
        userDicts = models.RoomUser.objects.filter(room_id=rid).values("user_id")

        userList = []
        for u in userDicts:
            userList.append(u["user_id"])

        # 根据用户ID列表获取对应的昵称
        usernickDicts = models.UserInfo.objects.filter(id__in=userList).values("user_nick")

        usernickList=[]
        for un in usernickDicts:
            usernickList.append(un["user_nick"])

        context = {
            "form":form,
            "winnerForm":usernickList,
            "queryset": page_object.page_queryset, # 分完页的数据
            "page_string": page_object.html(),     # 生成页码
        }
        return render(request, 'game_record_list.html', context)


@csrf_exempt
def game_record_add(request):
    """ 添加对局记录（ajax请求）"""
    # 获取ID
    rid = request.GET.get("rid")

    form = GameRecordModelForm(data=request.POST)
    if form.is_valid():
        # 判断是否存在待确认的记录，如果存在，不允许添加
        exists = models.GameRecord.objects.filter(room=rid,record_status=1)
        if exists:
            form.add_error("score_east","该房间还存在未确认的记录")
            return JsonResponse({"status": False, "error": form.errors})

        # 判断当前房间状态是否为游戏中
        exists = models.Room.objects.filter(id=rid,roomstatus=2)
        if not exists:
            form.add_error("score_east","房间状态异常，无法添加记录。")
            return JsonResponse({"status": False, "error": form.errors})

        # 根据房间ID获取四个用户信息
        room_user_list = models.RoomUser.objects.filter(room_id=rid).values()

        ulist=[]

        for row in room_user_list:
            # 获取四个位置的用户
            if row["position"] == 1 :
                east_u = row["user_id"]
            elif row["position"] == 2 :
                south_u = row["user_id"]
            elif row["position"] == 3 :
                west_u = row["user_id"]
            elif row["position"] == 4 :
                north_u = row["user_id"]

            # 把用户插入列表中，用来判断提交用户是否是该房间用户
            ulist.append(row["user_id"])

        # 从session中获取用户ID
        uid = request.session.get('info')["id"]

        if uid not in ulist:
            form.add_error("score_east","您不在此房间里，无法添加")
            return JsonResponse({"status": False, "error": form.errors})

        # 获取数据
        es = form.cleaned_data['score_east']
        er = form.cleaned_data['result_east']
        ss = form.cleaned_data['score_south']
        sr = form.cleaned_data['result_south']
        ws = form.cleaned_data['score_west']
        wr = form.cleaned_data['result_west']
        ns = form.cleaned_data['score_north']
        nr = form.cleaned_data['result_north']

        if  (er == -1 and es < 0) :
            form.add_error("score_east","请填正整数,输局会自动转为负数记录")
            return JsonResponse({"status": False, "error": form.errors})

        if  (sr == -1 and ss < 0) :
            form.add_error("score_south","请填正整数,输局会自动转为负数记录")
            return JsonResponse({"status": False, "error": form.errors})

        if  (wr == -1 and ws < 0) :
            form.add_error("score_west","请填正整数,输局会自动转为负数记录")
            return JsonResponse({"status": False, "error": form.errors})

        if  (nr == -1 and ns < 0) :
            form.add_error("score_north","请填正整数,输局会自动转为负数记录")
            return JsonResponse({"status": False, "error": form.errors})

        e_end = es*er
        s_end = ss*sr
        w_end = ws*wr
        n_end = ns*nr
        sum_end = e_end + s_end + w_end + n_end

        if er==sr and sr==wr and wr==nr:
            form.add_error("result_east","不能所有人输赢结果都一样")
            return JsonResponse({"status": False, "error": form.errors})

        if sum_end != 0:
            form.add_error("score_east","所有人积分之和不等于0")
            return JsonResponse({"status": False, "error": form.errors})

        if e_end == 0 and s_end == 0 and w_end == 0 and n_end == 0 :
            form.add_error("score_east","不能所有人积分都是0")
            return JsonResponse({"status": False, "error": form.errors})

        # 生成对局ID
        form.instance.round_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))

        # 实例化四个方位用户
        form.instance.user_east  = models.UserInfo.objects.get(id=east_u)
        form.instance.user_south = models.UserInfo.objects.get(id=south_u)
        form.instance.user_west  = models.UserInfo.objects.get(id=west_u)
        form.instance.user_north = models.UserInfo.objects.get(id=north_u)
        form.instance.room = models.Room.objects.get(id=rid)

        # 重置积分值
        form.instance.score_east = e_end
        form.instance.score_south = s_end
        form.instance.score_west = w_end
        form.instance.score_north = n_end

        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})

@csrf_exempt
def game_record_winner_add(request,rid):
    """ 添加对局记录（ajax请求）"""
    form = GameRecordWinnerModelForm(data=request.POST)
    if form.is_valid():
        # 判断当前房间状态是否为游戏中
        exists = models.Room.objects.filter(id=rid,roomstatus=2)
        if not exists:
            form.add_error("score_east","房间状态异常，无法添加记录。")
            return JsonResponse({"status": False, "error": form.errors})

        # 根据房间ID获取四个用户信息
        room_user_list = models.RoomUser.objects.filter(room_id=rid).values()

        ulist=[]

        for row in room_user_list:
            # 获取四个位置的用户
            if row["position"] == 1 :
                east_u = row["user_id"]
            elif row["position"] == 2 :
                south_u = row["user_id"]
            elif row["position"] == 3 :
                west_u = row["user_id"]
            elif row["position"] == 4 :
                north_u = row["user_id"]

            # 把用户插入列表中，用来判断提交用户是否是该房间用户
            ulist.append(row["user_id"])

        # 从session中获取用户ID
        uid = request.session.get('info')["id"]

        if uid not in ulist:
            form.add_error("score_east","您不在此房间里，无法添加")
            return JsonResponse({"status": False, "error": form.errors})

        # 获取数据
        es = form.cleaned_data['score_east']
        er = form.cleaned_data['result_east']
        ss = form.cleaned_data['score_south']
        sr = form.cleaned_data['result_south']
        ws = form.cleaned_data['score_west']
        wr = form.cleaned_data['result_west']
        ns = form.cleaned_data['score_north']
        nr = form.cleaned_data['result_north']

        if  (er == -1 and es < 0) :
            form.add_error("score_east","请填正整数,输局会自动转为负数记录")
            return JsonResponse({"status": False, "error": form.errors})

        if  (sr == -1 and ss < 0) :
            form.add_error("score_south","请填正整数,输局会自动转为负数记录")
            return JsonResponse({"status": False, "error": form.errors})

        if  (wr == -1 and ws < 0) :
            form.add_error("score_west","请填正整数,输局会自动转为负数记录")
            return JsonResponse({"status": False, "error": form.errors})

        if  (nr == -1 and ns < 0) :
            form.add_error("score_north","请填正整数,输局会自动转为负数记录")
            return JsonResponse({"status": False, "error": form.errors})

        e_end = es*er
        s_end = ss*sr
        w_end = ws*wr
        n_end = ns*nr
        sum_end = e_end + s_end + w_end + n_end

        if er==sr and sr==wr and wr==nr:
            form.add_error("result_east","不能所有人输赢结果都一样")
            return JsonResponse({"status": False, "error": form.errors})

        if sum_end != 0:
            form.add_error("score_east","所有人积分之和不等于0")
            return JsonResponse({"status": False, "error": form.errors})

        if e_end == 0 and s_end == 0 and w_end == 0 and n_end == 0 :
            form.add_error("score_east","不能所有人积分都是0")
            return JsonResponse({"status": False, "error": form.errors})

        # 生成对局ID
        form.instance.round_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))

        # 实例化四个方位用户
        form.instance.user_east  = models.UserInfo.objects.get(id=east_u)
        form.instance.user_south = models.UserInfo.objects.get(id=south_u)
        form.instance.user_west  = models.UserInfo.objects.get(id=west_u)
        form.instance.user_north = models.UserInfo.objects.get(id=north_u)
        form.instance.room = models.Room.objects.get(id=rid)

        # 重置积分值
        form.instance.score_east = e_end
        form.instance.score_south = s_end
        form.instance.score_west = w_end
        form.instance.score_north = n_end

        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def game_record_delete(request):
    """ 删除对局记录 """
    # 获取ID
    recordid = request.GET.get("recordid")

    # 根据对局ID查询房间ID
    rid_dic = models.GameRecord.objects.filter(id=recordid).values("room").first()
    rid = rid_dic["room"]

    # 根据session确认是不是本人退出
    user_id = request.session.get('info')["id"]

    # 判断操作删除的用户是不是本房间用户
    exists = models.RoomUser.objects.filter(room=rid,user=user_id).first()
    if not exists:
        return JsonResponse({"status": False, 'error': "删除失败，您不是本房间用户。"})

    # 删除
    models.GameRecord.objects.filter(id=recordid).delete()

    # 重定向房间列表
    return JsonResponse({"status": True})

def game_record_detail(request):
    """ 根据记录ID获取详情信息 """
    recordid = request.GET.get("recordid")
    row_dict = models.GameRecord.objects.filter(id=recordid).values("score_east","result_east","score_south","result_south","score_west","result_west","score_north","result_north").first()

    if not row_dict:
        return JsonResponse({"status": False, 'error': "数据不存在。"})

    # 从数据库获取到一个对象
    result = {
        "status": True,
        "data": row_dict
    }
    return JsonResponse(result)

@csrf_exempt
def game_record_edit(request):
    """ 编辑对局记录 """
    rid = request.GET.get("rid")
    recordid = request.GET.get("recordid")
    row_object = models.GameRecord.objects.filter(id=recordid).first()
    if not row_object:
        return JsonResponse({"status": False, 'tips': "数据不存在，请刷新重试。"})

    form = GameRecordModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        # 判断当前房间状态是否为游戏中
        exists = models.Room.objects.filter(id=rid,roomstatus=2)
        if not exists:
            form.add_error("score_east","房间状态异常，无法添加记录。")
            return JsonResponse({"status": False, "error": form.errors})

        # 根据房间ID获取四个用户信息
        room_user_list = models.RoomUser.objects.filter(room_id=rid).values()

        ulist=[]

        for row in room_user_list:
            # 获取四个位置的用户
            if row["position"] == 1 :
                east_u = row["user_id"]
            elif row["position"] == 2 :
                south_u = row["user_id"]
            elif row["position"] == 3 :
                west_u = row["user_id"]
            elif row["position"] == 4 :
                north_u = row["user_id"]

            # 把用户插入列表中，用来判断提交用户是否是该房间用户
            ulist.append(row["user_id"])

        # 从session中获取用户ID
        uid = request.session.get('info')["id"]

        if uid not in ulist:
            form.add_error("score_east","您不在此房间里，无法添加")
            return JsonResponse({"status": False, "error": form.errors})

        # 获取数据
        es = form.cleaned_data['score_east']
        er = form.cleaned_data['result_east']
        ss = form.cleaned_data['score_south']
        sr = form.cleaned_data['result_south']
        ws = form.cleaned_data['score_west']
        wr = form.cleaned_data['result_west']
        ns = form.cleaned_data['score_north']
        nr = form.cleaned_data['result_north']

        if  (er == -1 and es < 0) :
            form.add_error("score_east","请填正整数,输局会自动转为负数记录")
            return JsonResponse({"status": False, "error": form.errors})

        if  (sr == -1 and ss < 0) :
            form.add_error("score_south","请填正整数,输局会自动转为负数记录")
            return JsonResponse({"status": False, "error": form.errors})

        if  (wr == -1 and ws < 0) :
            form.add_error("score_west","请填正整数,输局会自动转为负数记录")
            return JsonResponse({"status": False, "error": form.errors})

        if  (nr == -1 and ns < 0) :
            form.add_error("score_north","请填正整数,输局会自动转为负数记录")
            return JsonResponse({"status": False, "error": form.errors})

        e_end = es*er
        s_end = ss*sr
        w_end = ws*wr
        n_end = ns*nr
        sum_end = e_end + s_end + w_end + n_end

        if er==sr and sr==wr and wr==nr:
            form.add_error("result_east","不能所有人输赢结果都一样")
            return JsonResponse({"status": False, "error": form.errors})

        if sum_end != 0:
            form.add_error("score_east","所有人积分之和不等于0")
            return JsonResponse({"status": False, "error": form.errors})

        if e_end == 0 and s_end == 0 and w_end == 0 and n_end == 0 :
            form.add_error("score_east","不能所有人积分都是0")
            return JsonResponse({"status": False, "error": form.errors})

        # 生成对局ID
        form.instance.round_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))

        # 实例化四个方位用户
        form.instance.user_east  = models.UserInfo.objects.get(id=east_u)
        form.instance.user_south = models.UserInfo.objects.get(id=south_u)
        form.instance.user_west  = models.UserInfo.objects.get(id=west_u)
        form.instance.user_north = models.UserInfo.objects.get(id=north_u)
        form.instance.room = models.Room.objects.get(id=rid)

        # 重置积分值
        form.instance.score_east = e_end
        form.instance.score_south = s_end
        form.instance.score_west = w_end
        form.instance.score_north = n_end

        form.save()
        return JsonResponse({"status": True})

    return JsonResponse({"status": False, 'error': form.errors})

def game_record_confirm(request):
    """ 确认记录，更新记录状态为已确认 """
    # 获取房间ID和记录ID
    rid = request.GET.get("rid")
    recordid = request.GET.get("recordid")

    # 根据session获取本人ID
    user_id = request.session.get('info')["id"]

    # 判断操作确认的用户是不是本房间用户
    exists = models.RoomUser.objects.filter(room=rid,user=user_id).first()
    if not exists:
        return JsonResponse({"status": False, 'error': "确认失败，您不是本房间用户。"})

    # 判断当前该记录状态是否是待确认状态
    exists = models.GameRecord.objects.filter(id=recordid,record_status=1).first()
    if not exists:
        return JsonResponse({"status": False, 'error': "确认失败，该记录已经被确认过了。"})

    # 更新确认状态
    models.GameRecord.objects.filter(id=recordid).update(record_status=2)

    # 重定向房间列表
    return JsonResponse({"status": True})
