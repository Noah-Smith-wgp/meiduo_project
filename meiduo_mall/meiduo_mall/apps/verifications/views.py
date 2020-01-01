import random, logging
from django import http
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from verifications.libs.captcha.captcha import captcha
from verifications import constants
from meiduo_mall.utils.response_code import RETCODE
# from verifications.libs.yuntongxun.ccp_sms import CCP
from celery_tasks.sms.tasks import ccp_send_sms_code
# Create your views here.


logger = logging.getLogger('django')


# url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        """
        :param request: 请求对象
        :param uuid: 唯一标识图形验证码所属于的用户
        :return: image/jpg
        """
        # 生成图形验证码（图片、文字）
        text, image = captcha.generate_captcha()

        # 保存图形验证码（文字）
        redis_conn = get_redis_connection('verify_code')
        # redis_conn.set() 没有过期时间
        # redis_conn.setex('key', '过期时间', 'values')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 响应结果（图片）
        # return http.HttpResponse(响应体, content_type='数据类型')
        return http.HttpResponse(image, content_type='image/jpeg')


# url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):
        """
        :param reqeust: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        # 创建连接到redis的对象
        redis_conn = get_redis_connection('verify_code')
        # 提取发送短信的标记 60秒避免频繁请求短信验证码
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        # 判断发送短信的标记是否存在（如果存在：频繁发送短信。反之，频率正常）
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})

        # 接收参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 校验参数
        if not all([image_code_client, uuid]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 提取图形验证码
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            # 图形验证码过期或者不存在
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码失效'})
        # 删除图形验证码，避免恶意测试图形验证码
        redis_conn.delete('img_%s' % uuid)

        # 对比图形验证码
        # 提示：在python3中，从redis中提取的所有数据都是bytes类型的
        # 提示：image_code_server是bytes类型的，而image_code_client是字符串，类型不同无法比较
        # 需要先将bytes类型的image_code_server转成字符串再对比
        image_code_server = image_code_server.decode()  # bytes转字符串
        if image_code_client.lower() != image_code_server.lower():  # 转小写后比较
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码有误'})

        # 生成短信验证码：生成6位数验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # 保存短信验证码
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 重新写入send_flag
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 创建redis管道
        pl = redis_conn.pipeline()
        # 将Redis请求添加到管道
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 执行请求
        pl.execute()

        # 发送短信验证码
        # CCP().send_template_sms(手机号, [验证码, 过期时间：单位分], 模板ID)
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)

        # Celery异步发送短信验证码
        ccp_send_sms_code.delay(mobile, sms_code)

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})
