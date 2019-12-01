from django import http
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, reverse
from django.db import DatabaseError
import re, json, logging
from django_redis import get_redis_connection
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from users.models import User, Address
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from celery_tasks.email.tasks import send_verify_email
from users.utils import generate_verify_email_url, check_verify_email_token
from users import constants
from goods.models import SKU
# Create your views here.

logger = logging.getLogger('django')


class UserBrowseHistory(LoginRequiredJSONMixin, View):
    """用户浏览记录"""
    def post(self, request):
        """保存用户浏览记录"""
        #接收参数：sku_id
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        #校验参数
        try:
            SKU.objects.get(id = sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseBadRequest('参数sku_id错误')

        #创建连接到redis的对象
        redis_conn = get_redis_connection('history')
        pl = redis_conn.pipeline()

        user_id = request.user.id
        #先去重
        # redis_conn.lrem('key', 0, '要添加的元素')
        pl.lrem('history_%s' % user_id, 0, sku_id)
        #再添加
        # redis_conn.lpush('key', '要添加的元素')
        pl.lpush('history_%s' % user_id, sku_id)
        #最后截取：截取最前面五个元素[0,1,2,3,4]
        # redis_conn.ltrim('key', '开始的角标', '结束的角标')
        pl.ltrim('history_%s' % user_id, 0, 4)
        pl.execute()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

    def get(self, request):
        """查询用户浏览记录"""
        # 创建连接到redis的对象
        user_id = request.user.id
        redis_conn = get_redis_connection('history')

        sku_ids = redis_conn.lrange('history_%s' % user_id, 0, -1)

        skus = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id = sku_id)
            sku_dict = {
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            }
            skus.append(sku_dict)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'skus': skus})


class AddressCreateView(LoginRequiredJSONMixin, View):
    """新增地址"""
    def post(self, request):
        """实现新增地址逻辑"""
        # 判断是否超过地址上限：最多20个
        # count = Address.objects.filter(user=request.user, is_deleted=False).count()
        count = request.user.addresses.filter(is_deleted=False).count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        #接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        #校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        #保存地址数据
        try:
            address = Address.objects.create(
                user = request.user,
                title = receiver,
                receiver = receiver,
                # province = province, # 将省份模型对象赋值给province (province = Area.objects.get(id=province_id))
                province_id=province_id,  # 省份ID赋值给外键
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )

            #设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except DatabaseError:
            return http.JsonResponse({'code':RETCODE.DBERR, 'errmsg':'新增地址失败'})

        # 封装新增的地址数据：为了新增地址成功后在页面直接刷新新的地址
        address_dict = {
            'id': address.id,
            'title': address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        #响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg':'新增地址成功', 'address': address_dict})


class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""
    def get(self, request):
        """提供收货地址页面"""
        # 获取用户地址列表
        # addresses = Address.objects.filter(user=request.user, is_deleted=False)
        addresses = request.user.addresses.filter(is_deleted = False)

        address_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_list.append(address_dict)

        context = {
            'default_address_id': request.user.default_address_id,
            'addresses': address_list
        }

        return render(request, 'user_center_site.html', context)


class VerifyEmailView(View):
    """验证邮箱"""
    def get(self, request):
        """实现邮箱验证逻辑"""
        # 接收参数
        token = request.GET.get('token')

        #校验参数：判断token是否为空和过期，提取user
        if not token:
            return http.HttpResponseForbidden('缺少token')

        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseForbidden('无效的token')

        #修改email_active的值为True
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('验证邮箱失败')

        #返回邮箱验证结果
        return redirect(reverse('users:info'))


class EmailView(LoginRequiredJSONMixin, View):
    '''添加邮箱'''
    def put(self, request):
        """实现添加邮箱逻辑"""
        #接收参数
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        email = json_dict.get('email')

        #校验参数
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')

        #赋值email字段
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.EMAILERR, 'errmsg': '添加邮箱失败'})

        #异步发送验证邮件
        verify_url = generate_verify_email_url(request.user)
        send_verify_email.delay(email, verify_url)

        #响应添加邮箱结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""
    def get(self, request):
        """提供个人信息页面"""
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }
        return render(request, 'user_center_info.html', context)


class LogoutView(View):
    """退出登录"""
    def get(self, request):
        """实现退出登录逻辑"""
        #清理session数据
        logout(request)
        #重定向到首页
        response = redirect(reverse('contents:index'))
        # 清理cookie中的username
        response.delete_cookie('username')
        # 响应结果
        return response


class LoginView(View):
    """用户名登录"""
    def get(self, request):
        """
        提供用户登录页面
        :param request: 请求对象
        :return: 登录界面
        """
        return render(request, 'login.html')

    def post(self, request):
        """
        实现登录逻辑
        :param request: 请求对象
        :return: 登录结果
        """
        #接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        #校验参数
        #判断参数是否齐全
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必传参数')

        #判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')

        #判断密码是否是8-20个字符
        if not re.match(r'^[0-9a-zA-Z]{8,20}$', password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')

        #认证用户登录
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmag': '账号或密码错误'})

        #实现状态保持
        login(request, user)

        #设置状态保持周期
        if not remembered:
            #没有记住用户：浏览器会话结束就过期
            request.session.set_expiry(0)
        else:
            #记住用户：None表示两周后过期
            request.session.set_expiry(None)

        #获取next参数
        next = request.GET.get('next')
        #判断登录地址中是否有next参数
        if not next:
            #创建响应对象
            response = redirect(reverse('contents:index'))
        else:
            response = redirect(next)

        # 将用户名写入到cookie
        # response.set_cookie('key', 'value', '过期时间')
        response.set_cookie('username', user.username, expires=3600 * 24 * 14)

        #响应结果
        return response


class UsernameCountView(View):
    """判断用户名是否重复注册"""
    def get(self, request, username):
        """
        查询指定用户记录个数
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        #查询指定用户记录个数：filter()返回的是查询集QuerySet([User])
        count = User.objects.filter(username=username).count()
        #响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class MobileCountView(View):
    """判断手机号是否重复注册"""
    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        #查询手机号注册个数
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class RegisterView(View):
    """用户注册"""
    def get(self, request):
        """
        提供注册页面
        :param request: 请求对象
        :return: 注册页面
        """
        return render(request, 'register.html')

    def post(self, request):
        """
        实现用户注册逻辑
        :param request: 请求对象
        :return: 注册结果
        """
        # 接收参数:不同的发送参数的方式，决定了不同的取参数的方式
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        sms_code_client = request.POST.get('sms_code')

        # 校验参数：首先判断必传参数是否缺少，然后以取反的方式以此校验参数
        #all()如果发现列表中有任意一个元素为空就返回false， 反之返回true
        if not all([username, password, password2, mobile, sms_code_client, allow]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')

        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg':'无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'register.html', {'sms_code_errmsg':'输入短信验证码有误'})

        #保存用户注册数据
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        #状态保持：如果成功就表示用户登入到美多商城
        login(request, user)

        #创建响应对象
        response = redirect(reverse('contents:index'))

        #将用户名写入到cookie
        # response.set_cookie('key', 'value', '过期时间')
        response.set_cookie('username', user.username, expires=3600*24*14)

        #响应注册结果：重定向到首页
        return response