from django.shortcuts import render
from django.views import View

# Create your views here.


class CartsView(View):
    """购物车管理"""

    def post(self, request):
        """添加购物车"""
        pass
