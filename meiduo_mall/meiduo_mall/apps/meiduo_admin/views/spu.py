from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from goods.models import SPU, Brand
from meiduo_admin.serializers.spu import SPUSerializer, BrandSerializer
from meiduo_admin.utils import PageNum


class SPUModelViewSet(ModelViewSet):

    serializer_class = SPUSerializer
    queryset = SPU.objects.all()
    pagination_class = PageNum


class BrandListAPIView(ListAPIView):

    serializer_class = BrandSerializer
    queryset = Brand.objects.all()