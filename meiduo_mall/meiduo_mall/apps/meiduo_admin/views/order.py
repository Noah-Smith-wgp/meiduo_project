from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.order import OrderInfoSerializer
from meiduo_admin.utils import PageNum
from orders.models import OrderInfo


class OrderInfoViewSet(ModelViewSet):

    serializer_class = OrderInfoSerializer
    queryset = OrderInfo.objects.all()
    pagination_class = PageNum

    def destroy(self, request, *args, **kwargs):
        return Response({'errmsg': 'error'})
