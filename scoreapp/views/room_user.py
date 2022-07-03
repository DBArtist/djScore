from django import forms
from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from scoreapp import models
from scoreapp.utils.bootstrap import BootStrapModelForm, BootStrapForm


class RoomUserModelForm(BootStrapModelForm):
    class Meta:
        model = models.RoomUser
        fields = ["position"]
        labels={
            "position":"入座方位"
        }


def room_user_list(request, rid):
    """ 房间用户列表 """
    if request.method == "GET":
        # 根据rid获取数据
        queryset = models.RoomUser.objects.filter(room=rid).order_by('position')
        form = RoomUserModelForm()
        # 重定向部门列表
        return render(request, 'room_user_list.html', {"form":form,"queryset": queryset,"rid":rid})

    return HttpResponse("AOU")

    # 不分页了
    # page_object = Pagination(request, queryset, page_size=50)
    # form = RoomModelForm()
    # context = {
    #     "form":form,
    #     "queryset": page_object.page_queryset, # 分完页的数据
    #     "page_string": page_object.html(),     # 生成页码
    # }
    # return render(request, 'room_list.html', context)

@csrf_exempt
def room_user_add(request,rid):
    """加入房间（ajax请求）"""
    form = RoomUserModelForm(data=request.POST)
    print (f"begin room_user_add ")
    if form.is_valid():
        print(f'room_user_add={form.cleaned_data}')
        # 从session中获取用户ID
        owner = request.session.get('info')["id"]

        # 实例化房间和用户
        form.instance.user = models.UserInfo.objects.get(id=owner)
        form.instance.room = models.Room.objects.get(id=rid)

        # 判断该方位是否已经有人了
        exists = models.RoomUser.objects.filter(room=rid,position=form.cleaned_data["position"]).first()
        if exists:
            form.add_error("position", "该位置已经有人入座了")
            return JsonResponse({"status": False, "error": form.errors})

        # 判断该用户是否已经入座过了
        exists2 = models.RoomUser.objects.filter(user=owner,room=rid).first()
        if exists2:
            form.add_error("position", "您已经入座了")
            return JsonResponse({"status": False, "error": form.errors})
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def room_user_delete(request,ruid):
    """ 退出房间 """
    # # 获取ID
    # ruid = request.GET.get(ruid)

    # 根据session确认是不是本人退出
    user_id = request.session.get('info')["id"]

    exists = models.RoomUser.objects.filter(id=ruid,user=user_id).first()
    if not exists:
        return HttpResponse("只能退出自己的账号,请返回上一页再次操作")

    # 删除
    models.RoomUser.objects.filter(id=ruid).delete()

    # 重定向房间列表
    return redirect("/room/list/")


def room_user_lock(request,rid):
    """ 锁定房间 """
    if request.method == "GET":
        # 判断当前房间状态是否为1
        exists = models.Room.objects.filter(id=rid,roomstatus=1).first()
        if not exists:
            return HttpResponse("房间已经锁定过了")

        # 判断当前用户是否有四个人
        cnt = models.RoomUser.objects.filter(room_id=rid).count()
        if cnt != 4:
            return HttpResponse("房间人数不足四人,无法锁定")

        # 从session中获取用户ID
        uid = request.session.get('info')["id"]

        # 判断锁定的人是否在房间的四个人当中
        exists = models.RoomUser.objects.filter(room_id=rid,user_id=uid).first()
        if not exists:
            return HttpResponse("你不在房间里,无法锁定该房间。")

        # 根据更新房间状态
        models.Room.objects.filter(id=rid).update(roomstatus=2)

        # 重定向部门列表
        return redirect("/room/list/")

    return HttpResponse("NO POST")
