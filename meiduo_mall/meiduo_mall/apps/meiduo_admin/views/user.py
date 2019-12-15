from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import ListCreateAPIView

from meiduo_admin.serializers.user import UserListViewSerializer
from users.models import User
from meiduo_admin.utils import PageNum


class UserListView(ListCreateAPIView):

    permission_classes = [IsAdminUser]

    serializer_class = UserListViewSerializer
    # queryset = User.objects.all()
    pagination_class = PageNum

    def get_queryset(self):
        # 获取前端传递的keyword
        keyword = self.request.query_params.get('keyword')
        if keyword is '' or keyword is None:
            return User.objects.all()
        else:
            return User.objects.filter(username__contains=keyword)
