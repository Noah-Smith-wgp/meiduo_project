from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from datetime import date, timedelta
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.mixins import ListModelMixin

from users.models import User
from goods.models import GoodsVisitCount
from meiduo_admin.serializers.statistical import GoodsVisitSerializer


class UserTotalCountAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        count = User.objects.all().count()
        data = {
            'count': count
        }

        return Response(data)


class UserDayCountAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        today = date.today()
        count = User.objects.filter(date_joined__gte=today).count()
        data = {
            'count': count,
            'date': today
        }

        return Response(data)


class UserDayActiveCountAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        today = date.today()
        count = User.objects.filter(last_login__gte=today).count()
        data = {
            'count': count,
            'date': today
        }

        return Response(data)


class UserDayOrderCountAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        today = date.today()
        count = User.objects.filter(orderinfo__create_time__gte=today).count()
        data = {
            'count': count,
            'date': today
        }

        return Response(data)
