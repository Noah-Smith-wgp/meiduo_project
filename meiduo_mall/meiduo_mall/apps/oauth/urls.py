from django.conf.urls import url, include

from . import views

urlpatterns = [
    #获取QQ扫码登录链接
    url(r'^qq/login/$', views.QQAuthURLView.as_view(), name='qq/login'),
    #QQ登录回调处理
    url(r'^oauth_callback/$', views.QQAuthUserView.as_view(), name='oauth_callback'),
    #WB登录授权连接
    url(r'^wb/login/$', views.WBAuthURLView.as_view(), name='wb/login'),
    #WB登录回调处理
    url(r'^oauth_callback/$', views.WBAuthUserView.as_view(), name='oauth_callback2'),
]