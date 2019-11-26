from django.shortcuts import render

from django.views import View
from contents.utils import get_categories
from contents.models import GoodsChannel
# Create your views here.


class IndexView(View):
    """首页广告"""
    def get(self, request):
        """提供首页广告页面"""
        # 查询商品分类
        categories = get_categories()
        # 构造上下文
        context = {
            'categories': categories
        }
        return render(request, 'index.html', context)