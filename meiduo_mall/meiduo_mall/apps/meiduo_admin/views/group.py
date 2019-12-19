from django.contrib.auth.models import Group, Permission
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from meiduo_mall.apps.meiduo_admin.serializers.group import GroupSerializer, AdminSerializer
from meiduo_mall.apps.meiduo_admin.serializers.permission import PermissionSerializer
from meiduo_mall.apps.meiduo_admin.utils import PageNum
from users.models import User


class GroupModelViewSet(ModelViewSet):

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = PageNum


class GroupListAPIView(ListAPIView):

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


# 管理员管理
class AdminModelViewSet(ModelViewSet):

    # 获取管理员用户
    queryset = User.objects.filter(is_staff=True)
    serializer_class = AdminSerializer
    pagination_class = PageNum


class AdminSimpleListAPIView(ListAPIView):

    serializer_class = GroupSerializer
    queryset = Group.objects.all()
