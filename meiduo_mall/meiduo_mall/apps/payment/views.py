from django.shortcuts import render
from django.views import View
from django import http
from alipay import AliPay
from django.conf import settings
import os

from meiduo_mall.utils.views import LoginRequiredJSONMixin
from orders.models import OrderInfo
from meiduo_mall.utils.response_code import RETCODE
# Create your views here.


class PaymentView(LoginRequiredJSONMixin, View):
    """订单支付功能"""

    def get(self,request, order_id):
        # 对接支付宝支付逻辑
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')

        # app_private_key_string = open("/path/to/your/private/key.pem").read()
        # alipay_public_key_string = open("/path/to/alipay/public/key.pem").read()

        #初始化对接支付宝的SDK实例
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_string=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/app_private_key.pem')).read(),
            alipay_public_key_string=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/alipay_public_key.pem')).read(),
            sign_type='RSA2',
            debug=settings.ALIPAY_DEBUG
        )

        #生成登录支付宝连接
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 美多商城维护的订单编号
            total_amount=str(order.total_amount),  # 支付金额
            subject="美多商城%s" % order_id,  # 订单的标题
            return_url=settings.ALIPAY_RETURN_URL  # 同步回调的地址（用来等待支付结果的）
        )

        alipay_url = settings.ALIPAY_URL + '?' + order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})
