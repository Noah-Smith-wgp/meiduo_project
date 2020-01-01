from django.shortcuts import render
from django.views import View
import json, pickle, base64
from django import http
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE

# Create your views here.


class CartsSelectAllView(View):
    """购物车全选"""

    def put(self, request):
        """实现购物车全选"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)

        # 校验参数
        if not isinstance(selected, bool):
            return http.HttpResponseForbidden({'参数selected有误'})

        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            # 读取hash中所有的sku_id {b'sku_id1': b'count1', b'sku_id2':b'coun2'}
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            # 读取字典中所有的sku_id [b'sku_id1', b'sku_id2']
            sku_ids = redis_cart.keys()

            if selected:
                # 确定全选：将sku_ids中所有的sku_id添加到set
                redis_conn.sadd('selected_%s' % user.id, *sku_ids)
            else:
                # 取消全选:将sku_ids中所有的sku_id从set中移除
                redis_conn.srem('selected_%s' % user.id, *sku_ids)

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

        else:
            cart_str = request.COOKIES.get('carts')
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

                # 将购物车字典中的所有selected字段设置为True或False
                for sku_id in cart_dict.keys():
                    cart_dict[sku_id]['selected'] = selected

                cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                response.set_cookie('carts', cookie_cart_str)

            return response


class CartsView(View):
    """购物车管理"""

    def post(self, request):
        """添加购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')  # 必须是数字或者数字字符串
        selected = json_dict.get('selected', True)  # 必须是布尔类型

        # 校验参数
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count错误')
        if not isinstance(selected, bool):
            return http.HttpResponseForbidden('参数selected错误')

        # 判断用户是否登录：如果用户已登录is_authenticated返回True，反之返回False
        user = request.user
        if user.is_authenticated:
            # 如果用户已登录，添加redis购物车
            # 创建连接到redis的对象
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()

            # 判断要添加的商品在购物车是否存在，如果存在，直接累加数量，反之，新增新的数据
            pl.hincrby('carts_%s' % user.id, sku_id, count)
            # 如果商品被勾选，将该商品的sku_id添加到set
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
        else:
            # 用户未登录，则添加cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes类型的字符串cart_str_bytes
                cart_str_bytes = cart_str.encode()
                # 将cart_str_bytes使用base64解码成为cart_dict_bytes
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将cart_dict_bytes使用pickle反序列化成为cart_dict
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

            # 向购物车字典添加购物车数据
            # 判断要添加的商品在购物车是否存在，如果存在，直接累加数量，反之，新增新的数据
            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count += origin_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            cart_dict_bytes = pickle.dumps(cart_dict)  # 将cart_dict使用pickle序列化成为cart_dict_bytes
            cart_str_bytes = base64.b64encode(cart_dict_bytes)  # 将cart_dict_bytes使用base64编码成为cart_str_bytes
            cookie_cart_str = cart_str_bytes.decode()  # 将cart_str_bytes转成字符串cookie_cart_str

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
            response.set_cookie('carts', cookie_cart_str)
            return response

    def get(self, request):
        """展示购物车"""
        user = request.user
        if user.is_authenticated:
            # 用户已登录，查询redis购物车
            redis_conn = get_redis_connection('carts')

            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            redis_selected = redis_conn.smembers('selected_%s' % user.id)

            # 将redis购物车数据转存到字典
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected
                }
        else:
            # 用户未登录，查询cookies购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            sku_dict = {
                'id': sku.id,
                'name': sku.name,
                'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                'default_image_url': sku.default_image.url,
                'count': cart_dict[sku.id]['count'],
                'selected': str(cart_dict[sku.id]['selected']),
                'amount': str(sku.price * cart_dict[sku.id]['count'])
            }
            cart_skus.append(sku_dict)

        context = {
            'cart_skus': cart_skus
        }

        return render(request, 'cart.html', context)

    def put(self, request):
        """修改购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 校验参数
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count错误')
        if not isinstance(selected, bool):
            return http.HttpResponseForbidden('参数selected错误')

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            # 修改商品数量
            redis_conn.hset('carts_%s' % user.id, sku_id, count)
            if selected:
                # 确定勾选：将修改的商品sku_id添加到set
                redis_conn.sadd('selected_%s' % user.id, sku_id)
            else:
                # 取消勾选:将修改的商品sku_id从set中移除
                redis_conn.srem('selected_%s' % user.id, sku_id)

            cart_sku = {
                'id': sku_id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url,
                'count': count,
                'selected': selected,
                'amount': sku.price * count
            }
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
            # 修改购物车字典：覆盖写入
            cart_dict[sku_id] = {
                "count": count,
                "selected": selected
            }

            # 将购物车字典转字符串并写入到cookie
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            cart_sku = {
                'id': sku_id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url,
                'count': count,
                'selected': selected,
                'amount': sku.price * count
            }

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
            response.set_cookie('carts', cookie_cart_str)
            return response

    def delete(self, request):
        """删除购物车"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')

        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            # 删除hash中的购物车数据
            redis_conn.hdel('carts_%s' % user.id, sku_id)
            # 删除set中的勾选状态
            redis_conn.srem('selected_%s' % user.id, sku_id)
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
        else:
            cart_str = request.COOKIES.get('carts')

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
                # 删除购物车字典中的key
                if sku_id in cart_dict:  # 判断是为了防止报错，# 只能删除存在的key.如果删除了不存在的key会抛出异常
                    del cart_dict[sku_id]

                # 将购物车字典转字符串并写入到cookie
                cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                response.set_cookie('carts', cookie_cart_str)

            return response
