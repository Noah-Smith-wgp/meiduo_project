from django.contrib.auth.models import Group
from rest_framework import serializers

from users.models import User


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'


# 管理员管理
class AdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    # 自定义保存方法，加密密码
    def create(self, validated_data):
        admin = super().create(validated_data)

        password = validated_data.get('password')
        admin.set_password(password)
        admin.is_staff = True
        admin.save()

        return admin
