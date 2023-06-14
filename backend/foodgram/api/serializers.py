from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from food.models import (Favorite, Ingredient, IngredientForRecipe, Recipe,
                         ShoppingCart, Tag)
from services import favorites as fav
from services import follow as fol
from services import ingredient as ingr
from services import model as m
from services import recipe as rec
from services import shopping_cart as sc
from services import tag as tg
from users.models import User

from .fields import Base64ImageField


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


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с рецептами в отображении подписок."""
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")

    def _validate(self, attrs, model):
        request = self.context.get('request')
        recipe: Recipe = self._args[0]
        value = m.is_exists(request.user, recipe, model)

        if request.method == 'POST':
            if value:
                raise serializers.ValidationError({
                    'errors': 'Рецепт уже добавлен.'})
        if request.method == 'DELETE':
            if not value:
                raise serializers.ValidationError({
                    'errors': 'Ничего не добавлено.'})
        return attrs


class ShoppingCartSerializer(ShortRecipeSerializer):
    """Сериализатор для работы со списком предметов."""

    def validate(self, attrs):
        """Валидация полей для добавления в список предметов."""
        return super()._validate(attrs=attrs, model=ShoppingCart)


class FavoriteSerializer(ShortRecipeSerializer):
    """Сериализатор для работы со списком избранных предметов."""

    def validate(self, attrs):
        """Валидация полей для добавления в избранные."""
        return super()._validate(attrs=attrs, model=Favorite)


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
        return fol.follow_exists(user, obj)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientForRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=tg.get_all_tags(),
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
        ingr.bulk_create_ingredients_amount(ingredients, recipe)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = rec.create_recipe(validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe,
                                        ingredients=ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(recipe=instance,
                                        ingredients=ingredients)
        return instance

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
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "tags", "author",
                  "ingredients", "is_favorited", "is_in_shopping_cart", "name",
                  "image", "text", "cooking_time")
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
        if user.is_authenticated:
            return fav.is_favorite_exists(obj, user)
        return False

    def get_is_in_shopping_cart(self, obj):
        """Получение поля нахождения в списке предметов."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return sc.is_shopping_cart_exists(obj, user)
        return False


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
        follow = fol.follow_exists(request.user, author)

        if request.method == 'POST':
            if request.user.id == author.id:
                raise serializers.ValidationError({
                    'errors': 'Подписка на себя - запрещена.'})
            if follow:
                raise serializers.ValidationError({
                    'errors': 'Вы уже подписаны на данного пользователя.'})

        if request.method == 'DELETE':
            if not follow:
                raise serializers.ValidationError({
                    "errors": "Вы не подписаны."})
        return attrs

    def get_is_subscribed(self, obj):
        """Получение поля is_subscribed."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return fol.follow_exists(user, obj)

    def get_recipes(self, obj):
        """Получение поля рецепта."""
        recipe = rec.filter_by_author(author=obj)
        serializer = ShortRecipeSerializer(
            recipe, context=self.context, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Получение поля recipes_count, отображающий кол-во рецептов,
        созданных пользователем."""
        recipes_count = rec.get_count_recipe_filtering_author(obj)
        return recipes_count
