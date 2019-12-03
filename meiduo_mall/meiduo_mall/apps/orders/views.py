from decimal import Decimal

from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django_redis import get_redis_connection

from meiduo_mall.utils.views import LoginRequiredJSONMixin
from goods.models import SKU
# Create your views here.


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """提供订单结算页面"""
        #查询当前登录用户未被逻辑删除的地址信息
        try:
            addresses = request.user.addresses.filter(is_deleted = False)
        except Exception:
            addresses = None

        redis_conn = get_redis_connection('carts')
        redis_cart = redis_conn.hgetall('carts_%s' % request.user.id)
        redis_selected = redis_conn.smembers('selected_%s' % request.user.id)
        new_cart_dict = {}
        for sku_id in redis_selected:
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

        sku_ids = new_cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)

        total_count = 0
        total_amount = Decimal('0.00')

        for sku in skus:
            sku.count = new_cart_dict[sku.id]
            sku.amount = sku.price * sku.count

            total_count += sku.count
            total_amount += sku.amount
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
