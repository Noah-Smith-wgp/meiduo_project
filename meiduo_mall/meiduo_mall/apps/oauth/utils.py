from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from itsdangerous import BadData

from oauth import constants


def generate_access_token_openid(openid):
    """
    序列化openid
    :param openid: openid明文
    :return: openid密文
    """
    #创建序列化器
    s = Serializer(settings.SECRET_KEY, expires_in=constants.ACCESS_TOKEN_EXPIRES)
    #准备要序列化的数据
    data = {'openid': openid}
    #序列化数据
    access_token_openid = s.dumps(data)
    #返回序列化后的数据
    return access_token_openid.decode()


def check_access_token_openid(access_token_openid):
    """
    反序列化openid
    :param access_token_openid: openid密文
    :return: openid明文
    """
    #创建序列化对象：序列化和反序列化的对象的参数必须是一模一样
    s = Serializer(settings.SECRET_KEY, expires_in=constants.ACCESS_TOKEN_EXPIRES)
    #反序列化openid密文
    try:
        data = s.loads(access_token_openid)
    except BadData:  #openid密文过期
        return None
    else:
        #返回openid明文
        return data.get('openid')