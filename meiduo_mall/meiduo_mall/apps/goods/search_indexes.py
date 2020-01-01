from haystack import indexes

from .models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """
    SKU索引类
    搜索引擎根据这个索引类指定的关键字，对数据进行预处理，并建立索引
    """
    # 用于指定建立索引的模型字段
    # 例如：可以使用商品名字来搜索，或者商品副标题来搜索
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)
