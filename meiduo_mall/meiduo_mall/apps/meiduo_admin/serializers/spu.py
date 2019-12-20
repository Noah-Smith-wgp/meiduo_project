from rest_framework import serializers

from contents.models import GoodsCategory
from goods.models import SPU, Brand


class SPUSerializer(serializers.ModelSerializer):

    brand = serializers.StringRelatedField()
    brand_id = serializers.IntegerField()

    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()

    class Meta:
        model = SPU
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = '__all__'


class GoodsCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = '__all__'
