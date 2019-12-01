from django.shortcuts import render
from django.views import View
import json, pickle, base64
from django import http
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE

# Create your views here.


class CartsView(View):
    """购物车管理"""

    def post(self, request):
        """添加购物车"""
        #接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        #校验参数
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            SKU.objects.get(id = sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count错误')
        if not isinstance(selected, bool):
            return http.HttpResponseForbidden('参数selected错误')

        #判断用户是否登录：如果用户已登录is_authenticated返回True，反之返回False
        user = request.user
        if user.is_authenticated:
            #如果用户已登录，添加redis购物车
            #创建连接到redis的对象
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()

            pl.hincrby('carts_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_str_bytes = cart_str.encode()
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count += origin_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            cart_dict_bytes = pickle.dumps(cart_dict)
            cart_str_bytes = base64.b64encode(cart_dict_bytes)
            cookie_cart_str = cart_str_bytes.decode()

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
            response.set_cookie('carts', cookie_cart_str)
            return response

    def get(self, request):
        """展示购物车"""
        return render(request, 'cart.html')
        pass

    def put(self, request):
        """修改购物车"""
        pass

    def delete(self, request):
        """删除购物车"""
        pass
