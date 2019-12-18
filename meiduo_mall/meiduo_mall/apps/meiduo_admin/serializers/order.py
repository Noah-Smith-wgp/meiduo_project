from rest_framework import serializers

from orders.models import OrderInfo


class OrderInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderInfo
        fields = '__all__'
