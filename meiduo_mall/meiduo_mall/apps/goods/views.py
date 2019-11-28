from django.shortcuts import render
from django.views import View
from django import http
from django.core.paginator import Paginator

from contents.models import GoodsCategory
from goods.models import SKU

# Create your views here.


class ListView(View):
    """商品列表页"""
    def get(self, request, category_id, page_num):
        """查询并渲染商品列表页"""
        #接收参数
        sort = request.GET.get('sort', 'default')

        #校验参数
        try:
            GoodsCategory.objects.get(id =category_id)
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
        page_skus = paginator.page(page_num)
        #总共分了多少页
        total_count = paginator.num_pages
        #查询面包屑导航
        #查询商品分类
        #查询热销排行
        context = {
            'category_id': category_id,
            'sort': sort,
            'page_skus': page_skus,
            'page_num': page_num,
            'total_count': total_count
        }

        return render(request, 'list.html', context)