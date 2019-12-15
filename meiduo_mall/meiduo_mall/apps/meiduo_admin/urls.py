from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from .views import statistical
from .views import user


urlpatterns = [
    # 管理员登录
    url(r'^authorizations/$', obtain_jwt_token),
    # 用户总量
    url(r'^statistical/total_count/$', statistical.UserTotalCountAPIView.as_view()),
    # 日增用户统计
    url(r'^statistical/day_increment/$', statistical.UserDayCountAPIView.as_view()),
    # 日活跃用户统计
    url(r'^statistical/day_active/$', statistical.UserDayActiveCountAPIView.as_view()),
    # 日下单用户量统计
    url(r'^statistical/day_orders/$', statistical.UserDayOrderCountAPIView.as_view()),
    # 月增用户统计
    url(r'^statistical/month_increment/$', statistical.UserMonthAddCountAPIView.as_view()),
    # # 日分类商品访问量
    url(r'^statistical/goods_day_views/$', statistical.CategoryDayVisitCountView.as_view()),

    # 查询用户
    url(r'^users/$', user.UserListView.as_view()),
]
