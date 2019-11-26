from django.shortcuts import render

from django.views import View
from contents.models import GoodsChannel
# Create your views here.


class IndexView(View):
    """首页广告"""
    def get(self, request):
        """提供首页广告页面"""
        #提供商品分类
        #准备商品分类字典
        categories = {}

        #查询37个频道
        channels = GoodsChannel.objects.order_by('group_id', 'sequence')
        #遍历37个频道可以获取到频道对应的组号
        for channel in channels:

            group_id = channel.group_id
            #对频道进行分组
            if group_id not in categories:
                categories[group_id] = {'channels': [], 'sub_cats': []}

            #填充每组频道数据
            #获取频道对应的一级类别，方便获取到name
            cat1 = channel.category   #通过外键获取一级商品分类对象
            categories[group_id]['channels'].append({
                'id': channel.id,  #频道编号
                'name': cat1.name,
                'url': channel.url
            })

            for cat2 in cat1.subs.all():
                #使用cat2查询cat3
                sub_cats = []
                for cat3 in cat2.subs.all():
                    sub_cats.append({
                        'id': cat3.id,
                        'name': cat3.name
                    })
                #查询每组中二级或三级分类
                categories[group_id]['sub_cats'].append({
                    'id': cat2.id,
                    'name': cat2.name,
                    'sub_cats': sub_cats
                })

        context = {
            'categories': categories
        }
        return render(request, 'index.html', context)