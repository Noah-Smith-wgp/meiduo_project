from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from goods.models import SKU, SPU
from meiduo_admin.serializers.sku import SKUSerializer, SKUCategorieSerializer, SPUSimpleSerializer
from meiduo_admin.utils import PageNum
from contents.models import GoodsCategory


class SKUModelViewSet(ModelViewSet):

    serializer_class = SKUSerializer
    # queryset = SKU.objects.all()
    pagination_class = PageNum

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')

        if keyword == '' or keyword is None:
            return SKU.objects.all()
        else:
            return SKU.objects.filter(name__contains=keyword)


class SKUCategoryView(ListAPIView):

    serializer_class = SKUCategorieSerializer
    queryset = GoodsCategory.objects.filter(parent_id__gt=37)


class SPUSimpleView(ListAPIView):
    serializer_class = SPUSimpleSerializer
    queryset = SPU.objects.all()