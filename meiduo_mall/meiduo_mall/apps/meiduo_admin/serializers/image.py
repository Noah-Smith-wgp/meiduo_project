from rest_framework import serializers

from goods.models import SKUImage


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKUImage
        fields = ['id', 'sku', 'image']