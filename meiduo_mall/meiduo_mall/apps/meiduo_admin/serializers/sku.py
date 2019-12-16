from rest_framework import serializers

from contents.models import GoodsCategory
from goods.models import SKU, SPU


class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = '__all__'


class SKUCategorieSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class SPUSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model=SPU
        fields='__all__'