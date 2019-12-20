from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from goods.models import SpecificationOption, SPUSpecification
from meiduo_admin.serializers.option import OptionSerializer, OptionSpecificationSerializer
from meiduo_admin.utils import PageNum


class OptionModelViewSet(ModelViewSet):

    serializer_class = OptionSerializer
    queryset = SpecificationOption.objects.all()
    pagination_class = PageNum


class OptionListAPIView(ListAPIView):

    serializer_class = OptionSpecificationSerializer
    queryset = SPUSpecification.objects.all()
