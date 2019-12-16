from rest_framework.viewsets import ModelViewSet

from goods.models import SKU
from meiduo_admin.serializers.sku import SKUSerializer
from meiduo_admin.utils import PageNum


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
