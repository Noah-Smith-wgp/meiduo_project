from django.db import models

from meiduo_mall.utils.models import BaseModel

# Create your models here.


class GoodsCategory(BaseModel):
    """商品类别"""
    name = models.CharField(max_length=10, verbose_name='名称')
    parent = models.ForeignKey('self', related_name='subs', null=True,
                               blank=True, on_delete=models.CASCADE, verbose_name='父类别')

    class Meta:
        db_table = 'tb_goods_category'
        verbose_name = '商品类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsChannelGroup(BaseModel):
    """商品频道组"""
    name = models.CharField(max_length=20, verbose_name='频道组名')

    class Meta:
        db_table = 'tb_channel_group'
        verbose_name = '商品频道组'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsChannel(BaseModel):
    """商品频道"""
    group = models.ForeignKey(GoodsChannelGroup, verbose_name='频道组名')
    category = models.ForeignKey(GoodsCategory, on_delete=models.CASCADE, verbose_name='顶级商品类别')
    url = models.CharField(max_length=50, verbose_name='频道页面链接')
    sequence = models.IntegerField(verbose_name='组内顺序')

    class Meta:
        db_table = 'tb_goods_channel'
        verbose_name = '商品频道'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category.name
