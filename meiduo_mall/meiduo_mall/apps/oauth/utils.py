from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from itsdangerous import BadData
from urllib.parse import urlencode, parse_qs
import json
import requests


from oauth import constants


class OAuthWB(object):
    """WB认证辅助工具类"""
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state = state  # 用于保存登录成功后的跳转页面路径

    def get_wb_url(self):
        # WB登录url参数组建
        data_dict = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state
        }
        wb_url = 'https://api.weibo.com/oauth2/authorize?' + urlencode(data_dict)
        return wb_url

    def get_wbaccess_token(self, code):
        #构建参数数据
        data_dict = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }
        access_url = 'https://api.weibo.com/oauth2/access_token'

        response = requests.post(access_url,data_dict)
        result = json.loads(response.decode())
        # wb_access_token = result['access_token']
        # uid = result['uid']
        return result


    def get_token_info(self, access_token):
        info_url = 'https://api.weibo.com/oauth2/get_token_info'
        response = requests.post(info_url, access_token)
        result = json.loads(response.decode())
        uid = result['uid']
        return uid

    def revokeoauth2(self, access_token):
        url = 'https://api.weibo.com/oauth2/revokeoauth2?' + access_token
        status = requests.get(url)
        return status


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