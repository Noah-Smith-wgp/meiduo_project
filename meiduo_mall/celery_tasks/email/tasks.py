from django.core.mail import send_mail
from django.conf import settings

from celery_tasks.main import celery_app


# name：任务别名
# bind：将任务对象作为第一个参数传入到任务中
@celery_app.task(name='send_verify_email', bind=True)
def send_verify_email(self, to_email, verify_url):
    """
    发送验证邮箱邮件
    :param to_email: 收件人邮箱
    :param verify_url: 验证链接
    :return: None
    """
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    try:
        send_mail(subject, "", settings.EMAIL_FROM, [to_email], html_message=html_message)
    except Exception as e:
        # exc：捕获的异常
        # countdown：自动重试的时间间隔
        # max_retries：自动重试次数的上限
        # 捕获到异常，每隔两秒重试一次，最多重试三次
        raise self.retry(exc=e, countdown=2, max_retries=3)
