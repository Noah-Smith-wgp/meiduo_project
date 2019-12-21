from rest_framework import serializers

from contents.models import GoodsChannel


class GoodsChannelSerializer(serializers.ModelSerializer):

    group = serializers.StringRelatedField()
    group_id = serializers.IntegerField()

    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField()

    class Meta:
        model = GoodsChannel
        fields = '__all__'
