from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from contents.models import GoodsCategory
from goods.models import SPU, Brand
from meiduo_admin.serializers.spu import SPUSerializer, BrandSerializer, GoodsCategorySerializer
from meiduo_admin.utils import PageNum


class SPUModelViewSet(ModelViewSet):

    serializer_class = SPUSerializer
    queryset = SPU.objects.all()
    pagination_class = PageNum


class BrandListAPIView(ListAPIView):

    serializer_class = BrandSerializer
    queryset = Brand.objects.all()


class GoodsCategory1ListAPIView(ListAPIView):

    serializer_class = GoodsCategorySerializer
    queryset = GoodsCategory.objects.filter(parent_id=None)
