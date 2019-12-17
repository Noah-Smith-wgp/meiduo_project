from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from goods.models import SKUImage, SKU
from meiduo_admin.serializers.image import ImageSerializer, SKUSerializer
from meiduo_admin.utils import PageNum


class ImageViewSet(ModelViewSet):

    # 图片序列化器
    serializer_class = ImageSerializer
    # 图片查询集
    queryset = SKUImage.objects.all()
    # 分页  # GenericAPIView 及其子类才有分页
    pagination_class = PageNum

    def create(self, request, *args, **kwargs):

        sku_id = request.data.get('sku')
        image = request.FILES.get('image')

        from fdfs_client.client import Fdfs_client
        # 创建fastdfs连接对象
        client = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')

        result = client.upload_by_buffer(image.read())

        if result['Status'] == 'Upload successed.':
            # 获取上传后的路径
            image_url = result.get('Remote file_id')

            # windows系统需要用此方法修改image_url,将group1\\M00/00/02/...改为group1/M00/00/02/...
            image_url = image_url.replace('\\', '/')

            # 保存图片
            img = SKUImage.objects.create(sku_id=sku_id, image=image_url)

            return Response({
                'id': img.id,
                'sku_id': sku_id,
                'image': img.image.url
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class SKUListView(ListAPIView):

    serializer_class = SKUSerializer
    queryset = SKU.objects.all()
