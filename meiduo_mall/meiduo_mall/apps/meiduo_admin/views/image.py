from rest_framework.viewsets import ModelViewSet

from goods.models import SKUImage
from meiduo_admin.serializers.image import ImageSerializer
from meiduo_admin.utils import PageNum


class ImageViewSet(ModelViewSet):

    # 图片序列化器
    serializer_class = ImageSerializer
    # 图片查询集
    queryset = SKUImage.objects.all()
    # 分页  # GenericAPIView 及其子类才有分页
    pagination_class = PageNum