from django.shortcuts import render
from django.views import View
from django import http
from alipay import AliPay
from django.conf import settings
import os

from meiduo_mall.utils.views import LoginRequiredJSONMixin, LoginRequiredMixin
from orders.models import OrderInfo, OrderGoods
from meiduo_mall.utils.response_code import RETCODE
from payment.models import Payment
# Create your views here.


class OrderCommentView(LoginRequiredMixin, View):
    """订单商品评价"""

    def get(self, request):
        """展示商品评价页面"""
        #接收参数
        order_id = request.GET.get('order_id')
        #校验参数
        try:
            OrderInfo.objects.get(order_id = order_id, user = request.user)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseNotFound('订单不存在')

        #查询订单中未被评价的商品信息

        try:
            uncomment_goods = OrderGoods.objects.filter(order_id=order_id, is_commented=False)
        except Exception:
            return http.HttpResponseServerError('订单商品信息出错')

        #构造待评价商品数据
        uncomment_goods_list = []
        for goods in uncomment_goods:
            uncomment_goods_list.append({
                'order_id': goods.order.order_id,
                'sku_id': goods.sku_id,
                'name': goods.sku.name,
                'price': str(goods.price),
                'default_image_url': goods.sku.default_image.url,
                'comment': goods.comment,
                'score': goods.score,
                'is_anonymous': str(goods.is_anonymous),
            })

            #渲染模板
            context = {
                'uncomment_goods_list': uncomment_goods_list
            }
            return render(request, 'goods_judge.html', context)


class PaymentStatusView(View):
    """保存订单支付结果"""

    def get(self, request):
        # 获取前端传入的请求参数
        query_dict = request.GET
        data = query_dict.dict()
        signature = data.pop('sign')

        # 初始化对接支付宝的SDK实例
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_string=open(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/app_private_key.pem')).read(),
            alipay_public_key_string=open(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/alipay_public_key.pem')).read(),
            sign_type='RSA2',
            debug=settings.ALIPAY_DEBUG
        )

        result = alipay.verify(data, signature)
        if result:
            order_id = data.get('out_trade_no')
            trade_id = data.get('trade_no')

            Payment.objects.create(
                order_id = order_id,
                trade_id = trade_id
            )
            OrderInfo.objects.filter(order_id = order_id, status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status = OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])

            context = {'trade_id': trade_id}
            return render(request, 'pay_success.html', context)
        else:
            return http.HttpResponseBadRequest('非法请求')


class PaymentView(LoginRequiredJSONMixin, View):
    """订单支付功能"""

    def get(self,request, order_id):
        # 对接支付宝支付逻辑
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')

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
