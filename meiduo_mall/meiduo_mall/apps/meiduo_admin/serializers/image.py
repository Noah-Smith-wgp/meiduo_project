from rest_framework import serializers

from goods.models import SKUImage, SKU


class ImageSerializer(serializers.ModelSerializer):

    # 返回图片关联的sku的id
    # sku = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SKUImage
        fields = ['id', 'sku', 'image']

    def create(self, validated_data):
        sku = validated_data.get('sku')
        image = validated_data.get('image')

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
            img = SKUImage.objects.create(sku=sku, image=image_url)

            return img
        else:
            raise serializers.ValidationError('上传失败')


class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['id', 'name']
