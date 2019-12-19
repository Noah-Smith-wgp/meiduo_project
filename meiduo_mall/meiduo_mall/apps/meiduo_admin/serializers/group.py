from django.contrib.auth.models import Group
from rest_framework import serializers

from users.models import User


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'
