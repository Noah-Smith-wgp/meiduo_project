from django.template import loader
from django.conf import settings
import os

from goods.models import SKU
from contents.utils import get_categories
from goods.utils import get_goods_specs, get_breadcrumb
from celery_tasks.main import celery_app


@celery_app.task(name='generate_static_sku_detail_html')
def generate_static_sku_detail_html(sku_id):
    """
    生成静态商品详情页面
    :param sku_id: 商品sku id
    :return:
    """

    # 查询sku信息
    sku = SKU.objects.get(id=sku_id)

    # 查询商品频道分类
    categories = get_categories()
    # 查询面包屑导航
    bread_crumb = get_breadcrumb(sku.category)

    # 构建当前商品的规格
    goods_specs = get_goods_specs(sku)

    # 构建上下文
    context = {
        'categories': categories,
        'bread_crumb': bread_crumb,
        'sku': sku,
        'specs': goods_specs
    }

    # 获取详情页模板文件
    template = loader.get_template('detail.html')
    # 渲染详情页html字符串
    detail_html_text = template.render(context)

    # 将详情页html字符串写入到指定目录，命名'index.html'
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'detail/' + str(sku_id) + '.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(detail_html_text)