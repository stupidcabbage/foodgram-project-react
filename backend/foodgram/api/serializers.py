from rest_framework import serializers
from food.models import Tag, Ingridient, Recipe
from django.core.files.base import ContentFile
import base64
from users.serializers import UserSerializer
from django.db.models import F


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "colour", "slug")


class IngridientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = ("id", "name", "measurement_unit")


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeRedSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    tag = TagSerializer(many=True)
    author = UserSerializer()
    ingridients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "tag", "author",
                  "ingridients", "name", "image",
                  "text", "cooking_time")
        read_only_fields = ("id", "author")

    def get_ingridients(self, obj):
        recipe = obj
        ingridients = recipe.ingridients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingridientforrecipe__amount')
        )
        return ingridients
