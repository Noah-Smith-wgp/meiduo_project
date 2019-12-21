from rest_framework.viewsets import ModelViewSet

from contents.models import GoodsChannel
from meiduo_admin.serializers.channel import GoodsChannelSerializer
from meiduo_admin.utils import PageNum


class GoodsChannelViewSet(ModelViewSet):

    serializer_class = GoodsChannelSerializer
    queryset = GoodsChannel.objects.all()
    pagination_class = PageNum
