from django.shortcuts import render, redirect
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django import http
import logging, re
from django.contrib.auth import login
from django_redis import get_redis_connection
from django.db import DatabaseError

from meiduo_mall.utils.response_code import RETCODE
from oauth.models import OAuthQQUser
from oauth.utils import generate_access_token_openid, check_access_token_openid, OAuthWB
from users.models import User
from carts.utils import merge_cart_cookie_to_redis

# Create your views here.

logger = logging.getLogger('django')


class WBAuthUserView(View):
    def post(self, request):
        code = request.POST.get('code')
        oauth_wb = OAuthWB(client_id=settings.WB_CLIENT_ID, client_secret=settings.WB_CLIENT_SECRET,
                           redirect_uri=settings.WB_REDIRECT_URI, state=next)
        wb_access_token = oauth_wb.get_wbaccess_token(code)
        print(wb_access_token)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'result':wb_access_token})


class WBAuthURLView(View):
    def get(self, request):
        next = request.GET.get('next', '/')

        oauth_wb = OAuthWB(client_id=settings.WB_CLIENT_ID, client_secret=settings.WB_CLIENT_SECRET,
                        redirect_uri=settings.WB_REDIRECT_URI, state=next)

        login_url = oauth_wb.get_wb_url()
        print(login_url)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url':login_url})


class QQAuthUserView(View):
    """用户扫码登录的回调处理"""
    def get(self, request):
        #Oauth2.0认证
        # #接收Authorization code
        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('缺少code')

        #创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        try:
            #通过Autherization Code获取Access Token
            access_token = oauth.get_access_token(code)
            #通过Access Token获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('OAuth2.0认证失败')

        try:
            qq_user_model = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            #如果openid没有绑定美多商城用户
            access_token_openid = generate_access_token_openid(openid)
            context = {'openid': access_token_openid}
            return render(request, 'oauth_callback.html', context)
        else:
            #如果openid已绑定美多商城用户
            # #实现状态保持
            qq_user = qq_user_model.user
            login(request, qq_user)

            #重定向
            next = request.GET.get('state')
            response = redirect(next)

            #登录时用户名写入到cookie，有效期两周
            response.set_cookie('username', qq_user.username, max_age=3600*24*14)

            # 登录成功后，合并购物车
            response = merge_cart_cookie_to_redis(request=request, user=qq_user, response=response)

            #响应结果
            return response

    def post(self, request):
        """美多商城用户绑定到openid"""
        #接收参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        access_token_openid = request.POST.get('openid')

        #校验参数
        #判断参数是否齐全
        if not all([mobile, password, sms_code_client, access_token_openid]):
            return http.HttpResponseForbidden('缺少必传参数')

        #判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        #判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        #判断短信验证码是否一致
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg':'无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg':'输入短信验证码有误'})

        #判断openid是否有效。错误提示放在sms_code_openid位置
        openid = check_access_token_openid(access_token_openid)
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': '无效的openid'})

        #判断用户是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 用户不存在,新建用户
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        else:
            #如果用户存在，检查用户密码
            if not user.check_password(password):
                return render(request, 'oaauth_callback.html', {'account_errmsg':'账号或密码有误'})
        #将用户绑定openid
        try:
            OAuthQQUser.objects.create(openid = openid, user=user)
        except DatabaseError:
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登陆失败'})

        #实现状态保持
        login(request, user)

        #响应绑定结果
        next = request.GET.get('state')
        response = redirect(next)

        #登录时用户名写入到cookie，有效期两周
        response.set_cookie('username', user.username, max_age=3600*24*14)

        # 登录成功后，合并购物车
        response = merge_cart_cookie_to_redis(request=request, user=user, response=response)

        return response


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