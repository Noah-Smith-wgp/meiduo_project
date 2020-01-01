from rest_framework import serializers

from users.models import User


class UserListViewSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'password', 'password2']

        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError('密码不一致')

        return attrs

    def create(self, validated_data):

        del validated_data['password2']
        user = User.objects.create_user(**validated_data)

        return user


# 前后端分离注册用户
class RegisterSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(max_length=20, min_length=8, required=True, write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'

        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError('密码不一致')

        return attrs

    def create(self, validated_data):

        if validated_data['password2']:
            del validated_data['password2']

        user = User.objects.create_user(**validated_data)

        # 给user 动态添加一个属性
        from rest_framework_jwt.settings import api_settings

        # 获取系统的方法
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        # 2.获取user中的信息，来保存到 payload
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token
        return user
