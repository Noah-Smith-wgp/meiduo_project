from django.shortcuts import render

from django.views import View
from contents.utils import get_categories
from contents.models import ContentCategory, Content
# Create your views here.


class IndexView(View):
    """首页广告"""
    def get(self, request):
        """提供首页广告页面"""
        # 查询商品分类
        categories = get_categories()

        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
            # contents[cat.key] = Content.objects.filter(category=cat, status=True).order_by('sequence')
        # 构造上下文
        context = {
            'categories': categories,
            'contents': contents
        }
        return render(request, 'index.html', context)