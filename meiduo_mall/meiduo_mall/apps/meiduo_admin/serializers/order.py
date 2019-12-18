from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods


class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['name', 'default_image']


class OrderGoodsSerializer(serializers.ModelSerializer):

    sku = SKUSerializer()

    class Meta:
        model = OrderGoods
        fields = ['count', 'price', 'sku']


class OrderInfoSerializer(serializers.ModelSerializer):

    skus = OrderGoodsSerializer(many=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = OrderInfo
        fields = '__all__'
