from rest_framework.viewsets import ModelViewSet

from goods.models import SpecificationOption
from meiduo_admin.serializers.option import OptionSerializer
from meiduo_admin.utils import PageNum


class OptionModelViewSet(ModelViewSet):

    serializer_class = OptionSerializer
    queryset = SpecificationOption.objects.all()
    pagination_class = PageNum