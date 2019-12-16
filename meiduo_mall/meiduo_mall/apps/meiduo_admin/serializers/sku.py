from rest_framework import serializers

from contents.models import GoodsCategory
from goods.models import SKU, SPU, SPUSpecification, SpecificationOption, SKUSpecification


# class SKUSpecificationSerializer(serializers.ModelSerializer):
#
#     spec_id = serializers.IntegerField()
#     option_id = serializers.IntegerField()
#
#     class Meta:
#         model = SKUSpecification
#         fields = ['spec_id', 'option_id']


class SKUSerializer(serializers.ModelSerializer):

    spu = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)

    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    # specs = SKUSpecificationSerializer(many=True)

    class Meta:
        model = SKU
        fields = '__all__'

    def create(self, validated_data):
        specs = self.context['request'].data.get('specs')

        sku = SKU.objects.create(**validated_data)

        for item in specs:
            SKUSpecification.objects.create(sku=sku, spec_id=item.get('spec_id'), option_id=item.get('option_id'))

        return sku


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
