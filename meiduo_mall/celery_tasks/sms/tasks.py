#封装任务：任务就是函数
from celery_tasks.sms.yuntongxun.ccp_sms import CCP
from celery_tasks.sms import constants
from celery_tasks.main import celery_app


@celery_app.task(name='ccp_send_sms_code')
def ccp_send_sms_code(mobile, sms_code):
    """
    发送短信异步任务
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return: 成功0 或 失败-1
    """
    ret = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)
    return ret