from decimal import Decimal

from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django_redis import get_redis_connection
import json
from django import http
from django.utils import timezone
from django.db import transaction

from meiduo_mall.utils.views import LoginRequiredJSONMixin
from goods.models import SKU
from users.models import Address
from orders.models import OrderInfo, OrderGoods
from meiduo_mall.utils.response_code import RETCODE
from orders import constants
# Create your views here.


class UserOrderInfoView(LoginRequiredMixin, View):
    """我的订单"""
    def get(self, request, page_num):
        """提供我的订单页面"""
        user = request.user
        # 查询订单
        orders = user.orderinfo_set.all().order_by('-create_time')

        # 遍历所有订单
        for order in orders:
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status-1][1]
            order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method-1][1]
            order.sku_list = []
            # 查询订单商品
            order_goods = order.skus.all()
            for order_good in order_goods:
                sku = order_good.sku
                sku.count = order_good.count
                sku.amount = sku.price * sku.count
                order.sku_list.append(sku)

        page_num = int(page_num)
        try:
            paginator = Paginator(orders, constants.ORDERS_LIST_LIMIT)
            page_orders = paginator.page(page_num)
            total_page = paginator.num_pages
        except EmptyPage:
            return http.HttpResponseNotFound('订单不存在')

        context = {
            "page_orders": page_orders,
            'total_page': total_page,
            'page_num': page_num,
        }
        return render(request, 'user_center_order.html', context)


class OrderSuccessView(LoginRequiredMixin, View):
    """提交订单成功"""

    def get(self, request):
        """提供提交订单成功页面"""
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }
        return render(request, 'order_success.html', context)


class OrderCommitView(LoginRequiredJSONMixin, View):
    """订单提交"""

    def post(self, request):
        """保存订单信息和订单商品信息"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')

        # 校验参数
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden('参数address_id错误')

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')

        user = request.user
        # 生成订单编号：年月日时分秒 + 用户ID == '20191202115910 + 000000010'
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

        # 使用with语句显式的开启一个事务
        with transaction.atomic():
            # 创建保存点：需要在操作mysql之前创建保存点
            save_id = transaction.savepoint()

            try:
                # 保存订单基本信息 OrderInfo（一）
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal(0.00),
                    freight=Decimal(10.00),
                    pay_method=pay_method,
                    # 如果支付方式是<CASH 货到付款>,那么订单的状态就是<待发货>。如果支付方式是<ALIPAY 支付宝支付>,那么订单的状态就是<待支付>
                    # status = 2 if pay_method == 1 else 1
                    status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'CASH'] else OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                )

                # 从redis读取购物车中被勾选的商品信息
                redis_conn = get_redis_connection('carts')
                redis_cart = redis_conn.hgetall('carts_%s' % request.user.id)
                redis_selected = redis_conn.smembers('selected_%s' % request.user.id)
                new_cart_dict = {}
                for sku_id in redis_selected:
                    new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

                # 提取出所有的被勾选的商品的sku_id
                sku_ids = new_cart_dict.keys()

                # 遍历购物车中被勾选的商品信息
                for sku_id in sku_ids:
                    # 以死循环的方式为用户下单，直到库存不足为止
                    while True:
                        # 查询SKU信息
                        sku = SKU.objects.get(id=sku_id)

                        # 在处理订单商品库存和销量之前，我们需要先查询出原始的库存和销量（作为乐观锁的标记）
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        # 判断SKU库存：用户要购买的数量跟库存对比
                        sku_count = new_cart_dict[sku_id]
                        if sku_count > origin_stock:
                            transaction.savepoint_rollback(save_id)
                            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '库存不足'})
                        # 模拟网络延迟：没有实际的意义，仅仅是为了放大错误的效果
                        # import time
                        # time.sleep(10)

                        # SKU减少库存，增加销量
                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()

                        # 使用乐观锁来实现并发下单（减少库存，增加销量）
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count

                        # SKU.objects.filter('使用原始库存查询对应的记录是否存在').update('如果原始库存查询对应的记录是存在的，使用新的库存替换原始库存')
                        # 如果update发现使用原始数据没有查询到记录，说明数据被更改，update不会执行，并返回0
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                        if result == 0:
                            # 库存被更改了：继续为这个商品下单   原始库存10， 被买走了1个，但是用户想买2个
                            # 下单成功满足的两个条件: 只有以下这两个条件同时满足，下单才成功。直到库存不足下单才会结束
                            # 1. 用户的购买量小于库存
                            # 2. 用户再购买时原始库存没有变化
                            continue

                        # 修改SPU销量
                        sku.spu.sales += sku_count
                        sku.spu.save()

                        # 保存订单商品信息 OrderGoods（多）
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price,
                        )

                        # 保存商品订单中总数量和总价(实付款)
                        order.total_count += sku_count
                        order.total_amount += sku_count * sku.price

                        # 如果下单成功，记得break
                        break

                # 添加邮费和保存订单信息（运费只需要累加一次，所以不能在循环中累加运费）
                order.total_amount += order.freight
                order.save()

            except Exception:
                # 暴力回滚：在提交订单期间，有任何错误都会回滚
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '提交订单失败'})

            # 如果数据库操作成功，需要显式的提交一次事务
            transaction.savepoint_commit(save_id)

        # 清除购物车中已结算的商品
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, *redis_selected)
        pl.srem('selected_%s' % user.id, *redis_selected)
        pl.execute()

        # 响应提交订单结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'order_id': order_id})


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """提供订单结算页面"""
        # 查询当前登录用户未被逻辑删除的地址信息
        try:
            # addresses = Address.objects.filter(user=request.user, is_deleted=False)
            addresses = request.user.addresses.filter(is_deleted=False)
        except Exception:
            # 前端通过判断发现，如果没有地址信息，渲染去编辑地址
            addresses = None

        # 查询购物车中被勾选的商品信息
        redis_conn = get_redis_connection('carts')
        redis_cart = redis_conn.hgetall('carts_%s' % request.user.id)
        redis_selected = redis_conn.smembers('selected_%s' % request.user.id)

        # 遍历redis_selected，取出被勾选的商品的sku_id
        new_cart_dict = {}
        for sku_id in redis_selected:
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

        # 通过new_cart_dict查询出被勾选的商品信息
        sku_ids = new_cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)

        total_count = 0
        total_amount = Decimal('0.00')  # 定义总金额的初始值（金钱）

        for sku in skus:
            # 给每款商品绑定数量和价格小计
            sku.count = new_cart_dict[sku.id]
            sku.amount = sku.price * sku.count

            # 计算总件数和总金额
            total_count += sku.count
            total_amount += sku.amount
        # 计算运费和实付款（不是累加，只计算一次，不要在循环里面做）
        freight = Decimal('10.00')
        payment_amount = total_amount + freight

        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': payment_amount
        }
        return render(request, 'place_order.html', context)
