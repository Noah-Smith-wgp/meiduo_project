from rest_framework.viewsets import ModelViewSet

from goods.models import SPUSpecification
from meiduo_admin.serializers.spec import SpecificationSerializer
from meiduo_admin.utils import PageNum


class SpecificationViewSet(ModelViewSet):

    serializer_class = SpecificationSerializer
    queryset = SPUSpecification.objects.all()
    pagination_class = PageNum
