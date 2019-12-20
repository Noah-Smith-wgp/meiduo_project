from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from .views import statistical
from .views import user
from .views import image
from .views import sku
from .views import order
from .views import permission
from .views import group
from .views import spu
from .views import spec
from .views import option


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

    # 获取sku表id
    url(r'^skus/simple/$', image.SKUListView.as_view()),

    # 获取sku三级分类信息
    url(r'^skus/categories/$', sku.SKUCategoryView.as_view()),
    # 获取spu表名称数据
    url(r'^goods/simple/$', sku.SPUSimpleView.as_view()),
    # 获取spu商品规格
    url(r'^goods/(?P<pk>\d+)/specs/$', sku.SPUSpecificationView.as_view()),

    # 获取权限类型列表数据
    url(r'^permission/content_types/$', permission.ContentTypeView.as_view()),
    # 获取权限表数据
    url(r'^permission/simple/$', group.GroupListAPIView.as_view()),
    # 管理员获取分组表数据
    url(r'^permission/groups/simple/$', group.AdminSimpleListAPIView.as_view()),
    # 获取spu品牌信息
    url(r'^goods/brands/simple/$', spu.BrandListAPIView.as_view()),
    # 获取一级分类信息
    url(r'^goods/channel/categories/$', spu.GoodsCategory1ListAPIView.as_view()),
    # 获取二三级分类信息
    url(r'^goods/channel/categories/(?P<pk>\d+)/$', spu.GoodsCategory2or3ListAPIView.as_view()),
]

router = DefaultRouter()

# 获取图片列表数据
router.register(r'skus/images', image.ImageViewSet, basename='image')
urlpatterns += router.urls

# 获取SKU表数据
router.register(r'skus', sku.SKUModelViewSet, basename='sku')
urlpatterns += router.urls

# 获取订单表表数据
router.register(r'orders', order.OrderInfoViewSet, basename='orders')
urlpatterns += router.urls

# 获取权限数据
router.register(r'permission/perms', permission.PermissionViewSet, basename='perms')
urlpatterns += router.urls

# 获取用户组数据
router.register(r'permission/groups', group.GroupModelViewSet, basename='groups')
urlpatterns += router.urls

# 获取管理员数据
router.register(r'permission/admins', group.AdminModelViewSet, basename='admins')
urlpatterns += router.urls

# 获取spu表数据
router.register(r'goods', spu.SPUModelViewSet, basename='goods')
urlpatterns += router.urls

# 获取规格表数据
router.register(r'goods/specs', spec.SpecificationViewSet, basename='specs')
urlpatterns += router.urls

# 获取规格选项表数据
router.register(r'specs/options', option.OptionModelViewSet, basename='options')
urlpatterns += router.urls
