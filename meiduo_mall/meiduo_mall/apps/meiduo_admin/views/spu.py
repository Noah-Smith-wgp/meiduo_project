from rest_framework.viewsets import ModelViewSet

from goods.models import SPU
from meiduo_admin.serializers.spu import SPUSerializer
from meiduo_admin.utils import PageNum


class SPUModelViewSet(ModelViewSet):

    serializer_class = SPUSerializer
    queryset = SPU.objects.all()
    pagination_class = PageNum
