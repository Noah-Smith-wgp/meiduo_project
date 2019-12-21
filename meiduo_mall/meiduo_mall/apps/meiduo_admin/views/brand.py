from rest_framework.viewsets import ModelViewSet

from goods.models import Brand
from meiduo_admin.serializers.brand import BrandSerializer
from meiduo_admin.utils import PageNum


class BrandViewSet(ModelViewSet):

    serializer_class = BrandSerializer
    queryset = Brand.objects.all()
    pagination_class = PageNum
