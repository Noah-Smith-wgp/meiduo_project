from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django import http

from meiduo_mall.utils.response_code import RETCODE
# Create your views here.


class QQAuthUserView(View):
    """用户扫码登录的回调处理"""
    def get(self, request):
        #Oauth2.0认证
        #接收Authorization code
        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('缺少code')
        pass


class QQAuthURLView(View):
    """
    提供QQ登录页面网址
    https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=xxx&redirect_uri=xxx&state=xxx
    """
    def get(self, request):
        #next表示从哪个页面进入到的登录页面，将来登录成功后，就自动回到那个页面
        next = request.GET.get('next', '/')

        #获取QQ登录页面网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)

        login_url = oauth.get_qq_url()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url':login_url})