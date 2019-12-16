from rest_framework import serializers

from contents.models import GoodsCategory
from goods.models import SKU, SPU, SPUSpecification, SpecificationOption


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
        model = SPU
        fields = '__all__'


class SpecificationOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpecificationOption
        fields = ['id', 'value']


class SPUSpecificationSerializer(serializers.ModelSerializer):

    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField(read_only=True)

    options = SpecificationOptionSerializer(read_only=True, many=True)

    class Meta:
        model = SPUSpecification
        fields = '__all__'
