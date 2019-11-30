from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django import http
from django.core.paginator import Paginator, EmptyPage
from django.db import DatabaseError

from contents.models import GoodsCategory
from goods.models import SKU, GoodsVisitCount
from contents.utils import get_categories
from goods.utils import get_breadcrumb, get_goods_specs
from meiduo_mall.utils.response_code import RETCODE
# Create your views here.


class DetailVisitView(View):
    """统计分类商品的访问量"""

    def post(self, request, category_id):
        """
        实现统计分类商品的访问量逻辑
        :param category_id: 要统计的商品的分类
        :return: JSON
        """
        # 校验category_id
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('缺少必传参数')

        # 获取当天的日期:t 对应的是时间对象DateTime 2019-11-29
        t = timezone.localtime()
        # 拼接时间字符串
        today_str = '%d-%02d-%02d' % (t.year, t.month, t.day)
        # 将时间字符串转时间对象 strptime : 将时间字符串转成时间对象。strftime ：时间对象转时间字符串
        today_date = timezone.datetime.strptime(today_str, '%Y-%m-%d')

        # 判断当天category_id对应的访问记录是否存在
        try:
            goods_count = GoodsVisitCount.objects.get(category=category, date=today_date)
        except GoodsVisitCount.DoesNotExist:
            # 如果不存在：新建记录，并保存本次访问量
            goods_count = GoodsVisitCount()

        # 如果已存在或者新建了记录，直接累加本次访问量
        try:
            goods_count.category_id = category_id
            goods_count.date = today_date
            goods_count.count += 1
            goods_count.save()
        except DatabaseError:
            return http.HttpResponseServerError('统计失败')

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class DetailView(View):
    """商品详情页"""
    def get(self, request, sku_id):
        """提供商品详情页"""
        try:
            sku = SKU.objects.get(id = sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        #查询商品频道分类
        categories = get_categories()
        #查询面包屑导航
        bread_crumb = get_breadcrumb(sku.category)

        #构建当前商品的规格
        goods_specs = get_goods_specs(sku)

        #构建上下文
        context = {
            'categories': categories,
            'bread_crumb': bread_crumb,
            'sku': sku,
            'specs': goods_specs
        }
        return render(request, 'detail.html', context)


class HotGoodsView(View):
    """商品热销排行"""
    def get(self, request, category_id):
        # 校验参数
        try:
            category3 = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('参数category_id有误')

        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]

        hot_skus = []
        for sku in skus:
            hot_dict = {
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            }
            hot_skus.append(hot_dict)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})


class ListView(View):
    """商品列表页"""
    def get(self, request, category_id, page_num):
        """查询并渲染商品列表页"""
        #接收参数
        sort = request.GET.get('sort', 'default')

        #校验参数
        try:
            category3 = GoodsCategory.objects.get(id =category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('参数category_id有误')

        # 先排序查询：排序字段必须是模型类某个属性
        if sort == 'price':  #按照价格由低到高排序
            sort_field = 'price'
        elif sort == 'hot':  #按照销量有高到底排序
            sort_field = '-sales'
        else:  #按照创建时间排序，新品在前
            sort = 'default'  #无论用户传的是什么，这里都重置为default
            sort_field = '-create_time'
        skus = SKU.objects.filter(category_id=category_id, is_launched = True).order_by(sort_field)

        #再分页查询 Paginator 分页器
        #创建分页器:对skus进行分页，每页5条记录
        paginator = Paginator(skus, 5)
        #查询指定页对应的数据
        try:
            page_skus = paginator.page(page_num)
        except EmptyPage:
            return render(request, '404.html')
        #总共分了多少页
        total_count = paginator.num_pages

        #查询商品分类
        categories = get_categories()

        # 查询面包屑导航
        # cat2 = category3.parent
        # cat1 = cat2.parent
        # bread_crumb = {
        #     'cat1': cat1,
        #     'cat2': cat2,
        #     'cat3': category3
        # }
        bread_crumb = get_breadcrumb(category3)

        #查询热销排行
        context = {
            'category_id': category_id,
            'sort': sort,
            'page_skus': page_skus,
            'page_num': page_num,
            'total_count': total_count,
            'categories': categories,
            'bread_crumb': bread_crumb
        }

        return render(request, 'list.html', context)