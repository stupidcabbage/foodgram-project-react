from django_filters import FilterSet, filters

from services import tag
from food.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """Фильтер ингредиентов."""
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    """Фильтер рецептов."""
    STATUS_CHOICES = (
        (0, 'false'),
        (1, 'true')
    )

    is_favorited = filters.ChoiceFilter(
        method='filter_is_favorited',
        choices=STATUS_CHOICES)
    is_in_shopping_cart = filters.ChoiceFilter(
        method='filter_is_in_shopping_cart',
        choices=STATUS_CHOICES)

    tags = filters.ModelMultipleChoiceFilter(
        queryset=tag.get_all_tags(),
        field_name='tags__slug',
        to_field_name='slug'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited')

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shoppingcart__user=self.request.user)
        return queryset
