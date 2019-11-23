from django.conf.urls import url, include

from . import views

urlpatterns = [
    #获取QQ扫码登录链接
    url(r'^qq/login/$', views.QQAuthURLView.as_view(), name='qq/login'),
    #QQ登录回调处理
    url(r'^oauth_callback/$', views.QQAuthUserView.as_view(), name='oauth_callback'),
]