"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # haystack
    url(r'^search/', include('haystack.urls')),

    #users
    url(r'^', include('users.urls', namespace='users')),  #users
    #content
    url(r'^', include('contents.urls', namespace='contents')),  #首页
    #verifications
    url(r'^', include('verifications.urls', namespace='verifications')),  #验证模块
    #oauth
    url(r'^', include('oauth.urls', namespace='oauth')),  #第三方认证模块
    #areas
    url(r'^', include('areas.urls')),  #省市区
    #goods
    url(r'^', include('goods.urls', namespace='goods')), #商品模块
    #carts
    url(r'^', include('carts.urls', namespace='carts')),  #购物车
    #orders
    url(r'^', include('orders.urls', namespace='orders')),  #订单
    #payment
    url(r'^', include('payment.urls', namespace='payment')),  #支付宝支付
    #admin
    url(r'^meiduo_admin/', include('meiduo_admin.urls', namespace='admin')),  #后台管理
]
