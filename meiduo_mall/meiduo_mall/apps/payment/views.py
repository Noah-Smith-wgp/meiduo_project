from django.shortcuts import render
from django.views import View
from django import http
from alipay import AliPay
from django.conf import settings
import os, json

from meiduo_mall.utils.views import LoginRequiredJSONMixin, LoginRequiredMixin
from orders.models import OrderInfo, OrderGoods
from meiduo_mall.utils.response_code import RETCODE
from payment.models import Payment
from goods.models import SKU
# Create your views here.


class OrderCommentView(LoginRequiredMixin, View):
    """订单商品评价"""

    def get(self, request):
        """展示商品评价页面"""
        # 接收参数
        order_id = request.GET.get('order_id')
        # 校验参数
        try:
            OrderInfo.objects.get(order_id=order_id, user=request.user)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseNotFound('订单不存在')

        # 查询订单中未被评价的商品信息

        try:
            uncomment_goods = OrderGoods.objects.filter(order_id=order_id, is_commented=False)
        except Exception:
            return http.HttpResponseServerError('订单商品信息出错')

        # 构造待评价商品数据
        uncomment_goods_list = []
        for goods in uncomment_goods:
            uncomment_goods_list.append({
                'order_id': goods.order.order_id,
                'sku_id': goods.sku.id,
                'name': goods.sku.name,
                'price': str(goods.price),
                'default_image_url': goods.sku.default_image.url,
                'comment': goods.comment,
                'score': goods.score,
                'is_anonymous': str(goods.is_anonymous),
            })

        # 渲染模板
        context = {
            'uncomment_goods_list': uncomment_goods_list
        }
        return render(request, 'goods_judge.html', context)

    def post(self, request):
        """评价订单商品"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        order_id = json_dict.get('order_id')
        sku_id = json_dict.get('sku_id')
        score = json_dict.get('score')
        comment = json_dict.get('comment')
        is_anonymous = json_dict.get('is_anonymous')
        # 校验参数
        if not all([order_id, sku_id, score, comment]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            OrderInfo.objects.filter(order_id=order_id, user=request.user,
                                     status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('参数order_id错误')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        if is_anonymous:
            if not isinstance(is_anonymous, bool):
                return http.HttpResponseForbidden('参数is_anonymous错误')

        # 保存订单商品评价数据
        OrderGoods.objects.filter(order_id=order_id, sku_id=sku_id, is_commented=False).update(
            comment=comment,
            score=score,
            is_anonymous=is_anonymous,
            is_commented=True
        )

        # 累计评论数据
        sku.comments += 1
        sku.save()
        sku.spu.comments += 1
        sku.spu.save()

        # 如果所有订单商品都已评价，则修改订单状态为已完成
        if OrderGoods.objects.filter(order_id=order_id, is_commented=False).count() == 0:
            OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM['FINISHED'])

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '评价成功'})


class PaymentStatusView(View):
    """保存订单支付结果"""

    def get(self, request):
        """处理支付宝支付的回调逻辑"""
        # 获取前端传入的请求参数
        # 接收所有的查询字符串参数:GET返回的是QueryDict类型的对象
        query_dict = request.GET
        # 将查询字符串参数转成字典
        data = query_dict.dict()
        # 在移除并提取查询字符串参数中的sign
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

        # 使用SDK实例调用verify方法来验证sign
        result = alipay.verify(data, signature)
        # 如果验证通过，说明这个回调是支付宝在支付成功后的回调请求
        if result:
            # 将美多商城维护的订单和支付宝维护的订单做关联
            order_id = data.get('out_trade_no')  # 获取美多商城维护的订单编号
            trade_id = data.get('trade_no')  # 获取支付宝维护的订单编号

            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            # 修改订单的状态（由待支付修改为待评价）
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])

            context = {'trade_id': trade_id}
            # 跳转到支付成功页面
            return render(request, 'pay_success.html', context)
        else:
            return http.HttpResponseBadRequest('非法请求')


class PaymentView(LoginRequiredJSONMixin, View):
    """订单支付功能"""

    def get(self, request, order_id):
        # 对接支付宝支付逻辑
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')

        # 使用python-alipay-sdk对接支付宝的支付接口、功能
        # 初始化对接支付宝的SDK实例
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,  # 应用ID
            app_notify_url=None,  # 默认回调url
            app_private_key_string=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/app_private_key.pem')).read(),
            alipay_public_key_string=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/alipay_public_key.pem')).read(),
            sign_type='RSA2',  # 签名的标准
            debug=settings.ALIPAY_DEBUG  # 表示当前是调试环境
        )

        # 生成登录支付宝连接
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 美多商城维护的订单编号
            total_amount=str(order.total_amount),  # 支付金额
            subject="美多商城%s" % order_id,  # 订单的标题
            return_url=settings.ALIPAY_RETURN_URL  # 同步回调的地址（用来等待支付结果的）
        )

        # 拼接电脑网站支付收银台登录页面的地址，正式环境，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # 拼接电脑网站支付收银台登录页面的地址，开发环境，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + '?' + order_string

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})
