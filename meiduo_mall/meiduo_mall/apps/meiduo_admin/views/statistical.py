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


class UserMonthAddCountAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        today = date.today()
        # 获取一个月前的时间
        month_ago_date = today - timedelta(days=30)
        # 构建数据列表
        data = []
        for i in range(1, 31):
            current_date = month_ago_date + timedelta(days=i)
            next_date = month_ago_date + timedelta(days=i+1)
            count = User.objects.filter(date_joined__gte=current_date, date_joined__lt=next_date).count()
            data.append({
                'count': count,
                'date': current_date
            })

        return Response(data)


# class CategoryDayVisitCountView(APIView):
#
#     permission_classes = [IsAdminUser]
#
#     def get(self, request):
#
#         today = date.today()
#         data = GoodsVisitCount.objects.filter(date__gte=today)
#         serializer = GoodsVisitSerializer(data, many=True)
#         return Response(serializer.data)


# class CategoryDayVisitCountView(ListModelMixin, GenericAPIView):
#
#     permission_classes = [IsAdminUser]
#
#     serializer_class = GoodsVisitSerializer
#     queryset = GoodsVisitCount.objects.filter(date__gte=date.today())
#
#     def get(self, request):
#
#         return self.list(request)


class CategoryDayVisitCountView(ListAPIView):

    permission_classes = [IsAdminUser]

    serializer_class = GoodsVisitSerializer
    queryset = GoodsVisitCount.objects.filter(date__gte=date.today())
