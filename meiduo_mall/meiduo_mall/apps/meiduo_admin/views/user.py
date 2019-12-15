from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser

from meiduo_admin.serializers.user import UserListViewSerializer
from users.models import User
from meiduo_admin.utils import PageNum


class UserListView(ListAPIView):

    permission_classes = [IsAdminUser]

    serializer_class = UserListViewSerializer
    queryset = User.objects.all()
    pagination_class = PageNum
