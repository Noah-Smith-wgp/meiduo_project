from rest_framework import serializers

from users.models import User


class UserListViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'password']

        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user
