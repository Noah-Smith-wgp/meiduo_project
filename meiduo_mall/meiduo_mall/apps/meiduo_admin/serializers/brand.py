from rest_framework import serializers

from goods.models import Brand


class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = '__all__'

    def create(self, validated_data):

        image = validated_data.get('logo')
        name = validated_data.get('name')
        first_letter = validated_data.get('first_letter')

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
            brand = Brand.objects.create(name=name, logo=image_url, first_letter=first_letter)

            return brand
        else:
            raise serializers.ValidationError('上传失败')
