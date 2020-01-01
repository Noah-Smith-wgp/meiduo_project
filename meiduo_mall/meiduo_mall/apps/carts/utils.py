import pickle, base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    """
    登录后合并cookie购物车数据到Redis
    :param request: 本次请求对象，获取cookie中的数据
    :param user: 登录用户信息，获取user_id
    :param response: 本次响应对象，清除cookie中的数据
    :return: response
    """
    # 获取cookie中的购物车数据
    cookie_cart_str = request.COOKIES.get('carts')
    # cookie中没有数据就响应结果
    if not cookie_cart_str:
        return response
    # 如果cookie中有购物车数据，转购物车字典
    cookie_cart_dict = pickle.loads(base64.b64decode(cookie_cart_str.encode()))

    new_cart_dict = {}
    selected_sku_ids = []
    unselected_sku_ids = []

    # 遍历cookie中的购物车字典，将要合并的数据添加到数据容器中
    for sku_id, cart_dict in cookie_cart_dict.items():
        # 合并sku_id和count
        new_cart_dict[sku_id] = cart_dict['count']
        if cart_dict['selected']:
            # 合并勾选商品sku_id
            selected_sku_ids.append(sku_id)
        else:
            # 合并未勾选商品sku_id
            unselected_sku_ids.append(sku_id)

    # 将数据容器中的购物车数据同步到redis数据库(重要)
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()

    # 同步sku_id和count
    pl.hmset('carts_%s' % user.id, new_cart_dict)

    # 同步勾选商品sku_id
    if selected_sku_ids:
        pl.sadd('selected_%s' % user.id, *selected_sku_ids)
    # 同步未勾选商品sku_id
    if unselected_sku_ids:
        pl.srem('selected_%s' % user.id, *unselected_sku_ids)
    pl.execute()

    # 清空cookie中购物车数据
    response.delete_cookie('carts')

    return response
