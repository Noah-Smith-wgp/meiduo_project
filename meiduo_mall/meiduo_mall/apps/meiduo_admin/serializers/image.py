from rest_framework import serializers

from goods.models import SKUImage, SKU


class ImageSerializer(serializers.ModelSerializer):

    # 返回图片关联的sku的id
    sku = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SKUImage
        fields = ['id', 'sku', 'image']


class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['id', 'name']
