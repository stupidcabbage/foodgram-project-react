from rest_framework import serializers
from food.models import Tag, Ingridient


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "colour", "slug")


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = ("id", "name", "measurement_unit")
