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
