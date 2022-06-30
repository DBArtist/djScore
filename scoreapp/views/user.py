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


def user_list(request):
    """ 用户列表 """
    queryset = models.UserInfo.objects.all()

    page_object = Pagination(request, queryset, page_size=2)
    context = {
        "queryset": page_object.page_queryset,
        "page_string": page_object.html(),
    }
    return render(request, 'user_list.html', context)


def user_add(request):
    """ 添加用户（原始方式） """

    if request.method == "GET":
        context = {
            'gender_choices': models.UserInfo.gender_choices,
        }
        return render(request, 'user_add.html', context)

    # 获取用户提交的数据
    user_account = request.POST.get('user_account')
    user_password = request.POST.get('user_password')
    user_nick = request.POST.get('user_nick')
    mobile = request.POST.get('mobile')
    birthday = request.POST.get('birthday')
    gender = request.POST.get('gd')

    # 添加到数据库中
    models.UserInfo.objects.create(user_account=user_account, user_password=user_password, user_nick=user_nick,
                                   mobile=mobile, birthday=birthday, gender=gender)

    # 返回到用户列表页面
    return redirect("/user/list/")


def user_model_form_add(request):
    """ 添加用户（ModelForm版本）"""
    if request.method == "GET":
        form = UserModelForm()
        return render(request, 'user_model_form_add.html', {"form": form})

    # 用户POST提交数据，数据校验。
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        # 如果数据合法，保存到数据库
        # {'name': '123', 'password': '123', 'age': 11, 'account': Decimal('0'), 'create_time': datetime.datetime(2011, 11, 11, 0, 0, tzinfo=<UTC>), 'gender': 1, 'depart': <Department: IT运维部门>}
        # print(form.cleaned_data)
        # models.UserInfo.objects.create(..)
        form.save()
        return redirect('/user/list/')

    # 校验失败（在页面上显示错误信息）
    return render(request, 'user_model_form_add.html', {"form": form})


def user_edit(request, nid):
    """ 编辑用户 """
    row_object = models.UserInfo.objects.filter(id=nid).first()

    if request.method == "GET":
        # 根据ID去数据库获取要编辑的那一行数据（对象）
        form = UserModelForm(instance=row_object)
        return render(request, 'user_edit.html', {'form': form})

    form = UserModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        # 默认保存的是用户输入的所有数据，如果想要再用户输入以外增加一点值
        # form.instance.字段名 = 值
        form.save()
        return redirect('/user/list/')
    return render(request, 'user_edit.html', {"form": form})


def user_delete(request, nid):
    models.UserInfo.objects.filter(id=nid).delete()
    return redirect('/user/list/')


class UserModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = models.UserInfo
        fields = ["user_account", "user_password", "confirm_password", "user_nick", "mobile"]
        widgets = {
            "user_password": forms.PasswordInput(render_value=True)
        }

    def clean_user_password(self):
        pwd = self.cleaned_data.get("user_password")
        return md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("user_password")
        confirm = md5(self.cleaned_data.get("confirm_password"))
        if confirm != pwd:
            raise ValidationError("密码不一致")
        # 返回什么，此字段以后保存到数据库就是什么。
        return confirm


class UserResetModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = models.UserInfo
        fields = ['user_password', 'confirm_password']
        widgets = {
            "user_password": forms.PasswordInput(render_value=True)
        }

    def clean_user_password(self):
        pwd = self.cleaned_data.get("user_password")
        md5_pwd = md5(pwd)

        # 去数据库校验当前密码和新输入的密码是否一致
        exists = models.UserInfo.objects.filter(id=self.instance.pk, user_password=md5_pwd).exists()
        if exists:
            raise ValidationError("不能与以前的密码相同")
        return md5_pwd

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("user_password")
        confirm = md5(self.cleaned_data.get("confirm_password"))
        if confirm != pwd:
            raise ValidationError("密码不一致")
        # 返回什么，此字段以后保存到数据库就是什么。
        return confirm


class LoginForm(BootStrapForm):
    user_account = forms.CharField(
        label="用户名",
        widget=forms.TextInput,
        required=True
    )
    user_password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(render_value=True),
        required=True
    )

    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput,
        required=True
    )

    def clean_user_password(self):
        pwd = self.cleaned_data.get("user_password")
        return md5(pwd)


def user_login(request):
    """ 登录 """
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'user_login.html', {'form': form})

    form = LoginForm(data=request.POST)
    if form.is_valid():
        # 验证成功，获取到的用户名和密码
        # {'username': 'wupeiqi', 'password': '123',"code":123}
        # {'username': 'wupeiqi', 'password': '5e5c3bad7eb35cba3638e145c830c35f',"code":xxx}

        # 验证码的校验
        user_input_code = form.cleaned_data.pop('code')
        code = request.session.get('image_code', "")
        if code.upper() != user_input_code.upper():
            form.add_error("code", "验证码错误")
            return render(request, 'user_login.html', {'form': form})


        # 去数据库校验用户名和密码是否正确，获取用户对象、None
        # admin_object = models.Admin.objects.filter(username=xxx, password=xxx).first()
        user_object = models.UserInfo.objects.filter(**form.cleaned_data).first()
        print (form.cleaned_data)
        print (request.POST.get("user_password"))
        if not user_object:
            form.add_error("user_password", "用户名或密码错误")
            # form.add_error("username", "用户名或密码错误")
            return render(request, 'user_login.html', {'form': form})

        # 用户名和密码正确
        # 网站生成随机字符串; 写到用户浏览器的cookie中；在写入到session中；
        request.session["info"] = {'id': user_object.id, 'name': user_object.user_account}
        # session可以保存7天
        request.session.set_expiry(60 * 60 * 24 * 7)

        return redirect("/user/list/")

    return render(request, 'user_login.html', {'form': form})


def image_code(request):
    """ 生成图片验证码 """

    # 调用pillow函数，生成图片
    img, code_string = check_code()

    # 写入到自己的session中（以便于后续获取验证码再进行校验）
    request.session['image_code'] = code_string
    # 给Session设置60s超时
    request.session.set_expiry(60)

    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def user_logout(request):
    """ 注销 """
    request.session.clear()

    return redirect('/login/')


def user_register(request):
    """ 注册 """
    return HttpResponse("XXX")