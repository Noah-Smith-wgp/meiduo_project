from django.contrib.auth.backends import ModelBackend
import re
from users.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings

from . import constants


def check_verify_email_token(token):
    """
    验证token并提取user
    :param token: 用户信息签名后的结果
    :return: user, None
    """
    s = Serializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    try:
        data = s.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user


def generate_verify_email_url(user):
    """
    生成邮箱验证链接
    :param user: 当前登录用户
    :return: verify_url
    """
    s = Serializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    data = {'user_id': user.id, 'email': user.email}
    token = s.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
    return verify_url


def get_user_by_account(account):
    """
    根据account查询用户
    :param account: 用户名或者手机号
    :return: user
    """
    try:
        if re.match('^1[3-9]\d{9}$', account):
            # 手机号登录
            user = User.objects.get(mobile=account)
        else:
            # 用户名登录
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """自定义用户认证后端"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写认证方法，实现多账号登录
        :param request: 请求对象
        :param username: 账号（用户名或者手机号）
        :param password: 密码
        :param kwargs: 其他参数
        :return: user
        """
        if request:  #在前台用户登录验证时添加request参数，如果有传入request则为前台登录，否则为后台登录
            #根据传入的username获取user对象。username可以是手机号也可以是账号
            user = get_user_by_account(username)
            #校验user是否存在并校验密码是否正确
            if user and user.check_password(password):
                return user
            else:
                return None
        else:  #没有得到request参数，则为后台登录
            try:
                user = User.objects.get(username=username, is_staff=True)
            except User.DoesNotExist:
                return None
            if user.check_password(password):
                return user