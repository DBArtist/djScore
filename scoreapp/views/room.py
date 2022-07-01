from django import forms
from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from scoreapp import models
from scoreapp.utils.form import UserModelForm
from scoreapp.utils.pagination import Pagination
from scoreapp.utils.bootstrap import BootStrapModelForm, BootStrapForm
from scoreapp.utils.encrypt import md5
from scoreapp.utils.code import check_code
from io import BytesIO


## https://www.cnblogs.com/yangyangming/p/11157755.html ModelForm文章

class RoomModelForm(BootStrapModelForm):
    class Meta:
        model = models.Room
        fields = ["roomname"]
        # labels={
        #     "owner":"创建者"
        # }


class RoomUserModelForm(BootStrapModelForm):
    class Meta:
        model = models.RoomUser
        fields = ["position"]
        labels={
            "position":"入座方位"
        }

def room_list(request):
    """ 房间列表 """
    queryset = models.Room.objects.all().order_by('-id')
    page_object = Pagination(request, queryset, page_size=50)
    form = RoomModelForm()
    context = {
        "form": form,
        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html(),  # 生成页码
    }
    return render(request, 'room_list.html', context)


@csrf_exempt
def room_add(request):
    """创建房间（ajax请求）"""
    form = RoomModelForm(data=request.POST)

    if form.is_valid():
        print(f'room_add={form.cleaned_data}')
        # 从session中获取用户ID，作为房间的拥有者即房主
        owner = request.session.get('info')["id"]

        # 查询UserInfo实例化owner
        form.instance.owner = models.UserInfo.objects.get(id=owner)

        # 默认新创建的房间状态为1（空闲中)
        form.instance.roomstatus = 1

        # 判断该用户是否有未关闭的房间。如果有的话不允许新创建
        exists = models.Room.objects.filter(roomstatus__in=[1, 2, 3], owner=owner).first()
        print(exists)
        if exists:
            form.add_error("roomname", "您已经有房间啦！")
            # return redirect("/room/list/")
            return JsonResponse({"status": False, "error": form.errors})
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})
    # return render(request, 'room_list.html', {'form': form})
    # models.Room.objects.create(roomname=roomname,owner=userobj,roomstatus=1)
    # return redirect("/room/list/")


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
    print ("begin room_user_add")
    if form.is_valid():
        print(f'room_user_add={form.cleaned_data}')
        # 从session中获取用户ID
        owner = request.session.get('info')["id"]

        # 查询UserInfo实例化owner
        form.instance.owner = models.UserInfo.objects.get(id=owner)

        # 判断该方位是否已经有人了
        exists = models.RoomUser.objects.filter(position=form.position,room=rid).first()
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
    # return render(request, 'room_list.html', {'form': form})
    # models.Room.objects.create(roomname=roomname,owner=userobj,roomstatus=1)
    # return redirect("/room/list/")



def room_delete(request):
    """删除部门"""
    # 获取ID
    nid = request.GET.get('nid')
    # 删除
    models.Room.objects.filter(id=nid).delete()
    # 重定向部门列表
    return redirect("/room/list/")


def room_edit(request, nid):
    """修改房间"""
    if request.method == "GET":
        # 根据nid获取数据
        row_object = models.Room.objects.filter(id=nid).first()
        # 重定向部门列表
        return render(request, 'room_edit.html', {"row_object": row_object})

    title = request.POST.get("title")
    models.Room.objects.filter(id=nid).update(title=title)
    return redirect("/room/list/")
