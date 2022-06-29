from django.shortcuts import render,HttpResponse,redirect
from scoreapp import models
from scoreapp.utils.form import UserModelForm,PrettyModelForm,PrettyEditModelForm

def user_list(request):
    """ 用户列表 """
    queryset =
    return render(request,'user_list.html')


def user_add(request):
    return render(request,'user_add.html')


class UserModelForm()

def user_model_form_add(request):
    """添加用户（ModelForm版本)"""
    if request.method == "GET":
        form = UserModelForm()
        return render(request, 'user_model_form_add.html', {"form": form})

    # POST提交数据，数据校验
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        # 如果数据合法，保存到数据库
        # print (form.cleaned_data)
        form.save()
        return redirect('/user/list')

    # 校验失败 print (form.errors)
    return render(request, 'user_model_form_add.html', {"form": form})
