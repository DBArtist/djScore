from django import forms
from django.shortcuts import render, HttpResponse, redirect
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from scoreapp import models
from scoreapp.utils.form import UserModelForm
from scoreapp.utils.pagination import Pagination
from scoreapp.utils.bootstrap import BootStrapModelForm, BootStrapForm
from scoreapp.utils.encrypt import md5
from scoreapp.utils.code import check_code
from io import BytesIO

class RoomModelForm(BootStrapModelForm):
    class Meta:
        model = models.Room
        fields = ["roomname","roomstatus","owner"]

def room_list(request):
    """ 房间列表 """
    queryset = models.Room.objects.all().order_by('-id')
    page_object = Pagination(request, queryset, page_size=50)
    form = RoomModelForm()

    context = {
        "form":form,
        "queryset": page_object.page_queryset, # 分完页的数据
        "page_string": page_object.html(),     # 生成页码
    }
    return render(request, 'room_list.html', context)



def room_add(request):
    """创建房间（ajax请求）"""
    if request.method == "GET":
        return render(request, 'room_add.html')

    form=RoomModelForm(data=request.POST)
    print(f'0xxxxxxxxx{form}')
    if form.is_valid():
        # roomname = request.POST.get("roomname")
        # 从session中获取用户ID，作为房间的拥有者即房主
        form.instance.owner = request.session.get('info')["id"]

        # # 获取都session中的用户ID，然后查询UserInfo实例化
        # userobj = models.UserInfo.objects.get(id=session_user_id)

        # 判断该用户是否有未关闭的房间。如果有的话不允许新创建
        exists = models.Room.objects.filter(roomstatus__in=[2,3]).first()
        print ('1xxxxxxxxx')
        if exists:
            print ('2xxxxxxxxx')
            form.add_error("roomname","已经创建过房间，直接进入房间或关闭旧房间再新创建一个")
            return redirect("/room/list/")
        form.save()
        return render(request, 'room_list.html', {'form': form})
    return render(request, 'room_list.html', {'form': form})
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



