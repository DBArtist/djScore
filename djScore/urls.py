"""djScore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from scoreapp.views import user,room,room_user,game_record


urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('index/', views.index),
    re_path(r'^$', user.user_login),

    # 用户管理
    path('user/list/', user.user_list),
    # path('user/add/', user.user_add),
    path('user/model/form/add/', user.user_model_form_add),
    path('user/<int:nid>/edit/', user.user_edit),
    path('user/<int:nid>/delete/', user.user_delete),

    # 用户登录
    path('login/', user.user_login),
    path('logout/', user.user_logout),
    path('register/', user.user_register),
    path('image/code/', user.image_code),

    # 房间管理
    path('room/list/', room.room_list),
    path('room/add/', room.room_add),

    # 房间用户管理
    path('room/<int:rid>/info/', room_user.room_user_list),
    path('room/<int:rid>/lock/', room_user.room_user_lock),
    path('room/<int:rid>/user/add/', room_user.room_user_add),
    path('room/user/<int:ruid>/delete/', room_user.room_user_delete),

    # 游戏记录管理
    path('room/<int:rid>/gamerecord/list/', game_record.game_record_list),
    path('room/<int:rid>/gamerecord/add/', game_record.game_record_add),
    path('room/<int:rid>/gamerecord/add/', game_record.game_record_winner_add),

    path('room/gamerecord/add/', game_record.game_record_add),
    path('room/gamerecord/detail/', game_record.game_record_detail),
    path('room/gamerecord/edit/', game_record.game_record_edit),
    path('room/gamerecord/confirm/', game_record.game_record_confirm),
    path('room/gamerecord/delete/', game_record.game_record_delete),

]

