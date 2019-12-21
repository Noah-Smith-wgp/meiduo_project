from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from contents.models import GoodsChannel, GoodsChannelGroup
from meiduo_admin.serializers.channel import GoodsChannelSerializer, ChannelGroupSerializer
from meiduo_admin.utils import PageNum


class GoodsChannelViewSet(ModelViewSet):

    serializer_class = GoodsChannelSerializer
    queryset = GoodsChannel.objects.all()
    pagination_class = PageNum


class ChannelGroupListAPIView(ListAPIView):

    serializer_class = ChannelGroupSerializer
    queryset = GoodsChannelGroup.objects.all()
