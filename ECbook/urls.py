"""
URL configuration for ECbook project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from bookapp import views

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("", views.index),
    # 管理图书
    path("admin/account/", views.account),
    # 编辑图书
    path("admin/edit/<int:book_id>/", views.edit),
    # 删除图书
    path("admin/account/<int:book_id>/", views.dele),
    # 首页
    path("admin/message/", views.message),
    # 携带参数提供给页面获取数据
    path("admin/comment/<int:bookNums>/<int:ebookid>/", views.comment),
    # 无参数时的页面
    path("admin/comment/", views.comments),
    # 新增图书
    path("admin/add/", views.add),
    # 上架的图书
    path("admin/up/", views.up),
    # 将已经获取的书本id携带进每个不同的评论
    path("admin/comment/god/<int:booknum>/<int:bookid>/<str:value>/", views.good),
    path("admin/comment/avg/<int:booknum>/<int:bookid>/<str:value>/", views.avg),
    path("admin/comment/bad/<int:booknum>/<int:bookid>/<str:value>/", views.bad),
    # 情感分析
    path("admin/comment/analyze/", views.analyze),
]
