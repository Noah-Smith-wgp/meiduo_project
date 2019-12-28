from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_admin.serializers.user import UserListViewSerializer, RegisterSerializer
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


# 使用前后端分离实现用户注册（在postman上测试）
class RegisterAPIView(APIView):

    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
