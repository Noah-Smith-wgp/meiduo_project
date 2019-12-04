from django.shortcuts import render
from django.views import View

from meiduo_mall.utils.views import LoginRequiredJSONMixin
# Create your views here.


class PaymentView(LoginRequiredJSONMixin, View):
    """订单支付功能"""

    def get(self,request, order_id):
        # 查询要支付的订单
        pass