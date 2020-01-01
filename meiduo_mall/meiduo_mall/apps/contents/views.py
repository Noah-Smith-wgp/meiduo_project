from django.shortcuts import render
from django.views import View

from contents.utils import get_categories
from contents.models import ContentCategory, Content
# Create your views here.


# url(r'^$', views.IndexView.as_view(), name='index')
class IndexView(View):
    """首页广告"""

    def get(self, request):
        """提供首页广告页面"""
        # 查询商品分类
        categories = get_categories()

        # 查询首页广告
        # 准备首页广告数据字典
        contents = {}
        # 查询所有的广告分类数据
        content_categories = ContentCategory.objects.all()
        # 遍历广告分类并提取key
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
            # contents[cat.key] = Content.objects.filter(category=cat, status=True).order_by('sequence')

        # 构造上下文
        context = {
            'categories': categories,
            'contents': contents
        }

        return render(request, 'index.html', context)
