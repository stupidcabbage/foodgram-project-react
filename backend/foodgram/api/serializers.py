import base64

from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from djoser.serializers import UserCreateSerializer, UserSerializer
from food.models import (Favourites, Ingredient, IngredientForRecipe, Recipe,
                         Tag)
from rest_framework import serializers
from users.models import Follow, User
from django.shortcuts import  get_object_or_404


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с тэгами."""
    class Meta:
        model = Tag
        fields = ("id", "name", "colour", "slug")


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингридентами в рецепте."""
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientForRecipe
        fields = ("id", "amount")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингридиентами."""
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class Base64ImageField(serializers.ImageField):
    """Перевод картинки из base64 в нормальный формат."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с рецептами в отображении подписок."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class CustomUserSerializer(UserSerializer):
    """Кастомный сериализатор для работы с пользователями."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Получение поля is_subscribed."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientForRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "tags", "author",
                  "ingredients", "name", "image",
                  "text", "cooking_time")

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError({
                'ingredients': 'Необходим хотя бы один ингредиент.'})
        ingredients_list = []
        for ingredient in value:
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError({
                    'ingredients': 'Данного ингредиента не существует.'})

            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты не могут повторяться.'})

            if int(ingredient['amount']) < 1:
                raise serializers.ValidationError({
                    'amount': 'Кол-во ингредиентов должно быть не меньше 1.'})
            ingredients_list.append(ingredient['id'])
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError({
                'tags': "Необходим хотя бы один тэг."})
        return value

    @transaction.atomic
    def create_ingredients_amounts(self, ingredients, recipe):
        """Получение поля ингредиента."""
        IngredientForRecipe.objects.bulk_create(
            [IngredientForRecipe(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe,
                                        ingredients=ingredients)
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance,
                                    context=context).data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов (GET)."""
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "tags", "author",
                  "ingredients", "is_favorited", "name", "image",
                  "text", "cooking_time")
        read_only_fields = ("id", "author")

    def get_ingredients(self, obj):
        """Получение поля ингридиенты."""
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientforrecipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        """Получение поля нахождения в избранном."""
        user = self.context.get('request').user
        favorite = Favourites.objects.filter(recipe=obj, user=user).exists()
        return favorite


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""
    class Meta:
        model = User
        fields = ("email",
                  "id",
                  "username",
                  "first_name",
                  "last_name",
                  "password",)
        read_only_fields = ("id",)


class CustomAuthTokenEmailSerializer(serializers.Serializer):
    """
    Сериализатор для получения токена,
    используя электронный адрес для авторизации пользователя.
    """
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password",),
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(request=self.context.get("request"),
                                email=email, password=password)

            if not user:
                msg = _("Authentication credentials were not provided.")
                raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с подписками."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, attrs):
        """Валидация полей подписок."""
        request = self.context.get('request')
        author = self._args[0]
        follow = Follow.objects.filter(
            user=request.user, author=author).exists()

        if request.method == 'POST':
            if request.user.id == author.id:
                raise serializers.ValidationError({
                    'error': 'Подписка на себя - запрещена.'})
            if follow:
                raise serializers.ValidationError({
                    'error': 'Вы уже подписаны на данного пользователя.'})

        if request.method == 'DELETE':
            if not follow:
                raise serializers.ValidationError({
                    "error": "Вы не подписаны."})
        return attrs

    def get_is_subscribed(self, obj):
        """Получение поля is_subscribed."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        """Получение поля рецепта."""
        recipe = Recipe.objects.filter(author=obj)
        serializer = ShortRecipeSerializer(recipe, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Получение поля recipes_count, отображающий кол-во рецептов,
        созданных пользователем."""
        recipes_count = Recipe.objects.filter(author=obj).count()
        return recipes_count


class FavouriteSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с избранным."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields

    def validate(self, attrs):
        """Валидация полей для добавления в избранные."""
        request = self.context.get('request')
        recipe: Recipe = self._args[0]
        favourite = Favourites.objects.filter(
            user=request.user, recipe=recipe).exists()

        if request.method == 'POST':
            if favourite:
                raise serializers.ValidationError({
                    'error': 'Рецепт уже в избранном.'})
        if request.method == 'DELETE':
            if not favourite:
                raise serializers.ValidationError({
                    'error': 'У вас нет ничего в избранном.'})
        return attrs
