from rest_framework import serializers

from goods.models import SpecificationOption, SPUSpecification


class OptionSerializer(serializers.ModelSerializer):

    spec = serializers.StringRelatedField()
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption
        fields = '__all__'


class OptionSpecificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SPUSpecification
        fields = '__all__'
