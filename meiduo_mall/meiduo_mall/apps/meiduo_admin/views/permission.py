from django.contrib.auth.models import Permission, ContentType
# from django.contrib.contenttypes.models import ContentType
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.permission import PermissionSerializer, ContentTypeSerializer
from meiduo_admin.utils import PageNum


class PermissionViewSet(ModelViewSet):

    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
    pagination_class = PageNum


class ContentTypeView(ListAPIView):

    serializer_class = ContentTypeSerializer
    queryset = ContentType.objects.all()
