from rest_framework import serializers

from goods.models import GoodsVisitCount


class GoodsVisitSerializer(serializers.ModelSerializer):

    category = serializers.StringRelatedField()

    class Meta:
        model = GoodsVisitCount
        fields = ['id', 'count', 'category']
