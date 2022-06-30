from django import forms
from django.shortcuts import render, HttpResponse, redirect
from django.core.exceptions import ValidationError
from scoreapp import models
from scoreapp.utils.form import UserModelForm
from scoreapp.utils.pagination import Pagination
from scoreapp.utils.bootstrap import BootStrapModelForm, BootStrapForm
from scoreapp.utils.encrypt import md5
from scoreapp.utils.code import check_code
from io import BytesIO


def room_list(request):
    """ 用户列表 """
    queryset = models.Room.objects.all()

    page_object = Pagination(request, queryset, page_size=200)
    context = {
        "queryset": page_object.page_queryset,
        "page_string": page_object.html(),
    }
    return render(request, 'room_list.html', context)

def room_add(request):
    """添加房间"""
    if request.method == "GET":
        return render(request, 'room_add.html')

    roomname = request.POST.get("roomname")
    session_user_id = request.session.get('info')["id"]

    # 从session中获取用户ID，作为房间的拥有者即房主
    # 获取都session中的用户ID，然后查询UserInfo实例化
    userobj = models.UserInfo.objects.get(id=session_user_id)
    models.Room.objects.create(roomname=roomname,owner=userobj,roomstatus=1)
    return redirect("/room/list/")


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



