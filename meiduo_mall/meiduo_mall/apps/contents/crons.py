from django.template import loader
import os, time
from django.conf import settings

from contents.utils import get_categories
from contents.models import ContentCategory


def generate_static_index_html():
    """生成静态的主页HTML文件"""

    print('%s: generate_static_index_html' % time.ctime())

    # 查询商品分类
    categories = get_categories()

    #广告内容
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

    #获取首页模板文件
    template = loader.get_template('index.html')
    #渲染首页HTML字符串
    html_text = template.render(context)
    #将首页html字符串写入到指定目录，命名‘index.html
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)