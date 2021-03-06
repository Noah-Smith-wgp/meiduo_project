from rest_framework import serializers

from contents.models import GoodsCategory
from goods.models import SKU, SPU, SPUSpecification, SpecificationOption, SKUSpecification
from django.db import transaction


class SKUSpecificationSerializer(serializers.ModelSerializer):

    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = ['spec_id', 'option_id']


class SKUSerializer(serializers.ModelSerializer):

    spu = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)

    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    specs = SKUSpecificationSerializer(many=True)

    class Meta:
        model = SKU
        fields = '__all__'

    def create(self, validated_data):

        specs = self.context['request'].data.get('specs')

        # 把validated_data中的 specs 删除掉
        if 'specs' in validated_data:
            del validated_data['specs']
        # 开启事务
        with transaction.atomic():
            # 设置还原点
            save_point = transaction.savepoint()

            try:
                # 保存数据
                # sku = super().create(validated_data)
                sku = SKU.objects.create(**validated_data)

                # 自定义方法保存specs
                for item in specs:
                    SKUSpecification.objects.create(sku=sku, spec_id=item.get('spec_id'), option_id=item.get('option_id'))
            except Exception:
                # 捕获异常，数据库回滚到还原点
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('保存失败')
            else:
                # 数据库未报异常，提交保存
                transaction.savepoint_commit(save_point)

                # 因前端未设置上传图片的选项，此处为了防止celery生成静态页面时报错，自己添加一个保存图片操作，无意义
                # sku.default_image = 'group1/M00/00/02/CtM3BVrRdPeAXNDMAAYJrpessGQ9777651'
                # sku.save()

                # 生成详情页面
                from celery_tasks.html.tasks import generate_static_sku_detail_html
                generate_static_sku_detail_html.delay(sku.id)

        return sku

    def update(self, instance, validated_data):

        specs = validated_data.get('specs')

        if 'specs' in validated_data:
            del validated_data['specs']

        with transaction.atomic():
            save_point = transaction.savepoint()

            try:
                # instance = super().update(instance, validated_data)
                SKU.objects.filter(id=instance.id).update(**validated_data)

                for item in specs:
                    SKUSpecification.objects.filter(
                        sku_id=instance.id, spec_id=item.get('spec_id')).update(option_id=item.get('option_id'))
            except Exception:
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('更新失败')
            else:
                transaction.savepoint_commit(save_point)

                # 生成详情页面
                from celery_tasks.html.tasks import generate_static_sku_detail_html
                generate_static_sku_detail_html.delay(instance.id)

        return instance


class SKUCategorieSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        fields = "__all__"


class SPUSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = SPU
        fields = '__all__'


class SpecificationOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpecificationOption
        fields = ['id', 'value']


class SPUSpecificationSerializer(serializers.ModelSerializer):

    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField(read_only=True)

    options = SpecificationOptionSerializer(read_only=True, many=True)

    class Meta:
        model = SPUSpecification
        fields = '__all__'
