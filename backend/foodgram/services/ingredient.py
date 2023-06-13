from django.db.models import Sum
from food.models import Ingredient, IngredientForRecipe, Recipe
from users.models import User


def get_all_ingredients() -> Ingredient:
    """Возвращает все ингредиенты."""
    return Ingredient.objects.all()


def get_sum_amount(user: User):
    """Возвращает сумму всех продуктов."""
    amount = IngredientForRecipe.objects.filter(
            recipe__shoppingcart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
    return amount


def create_ingredient_for_recipe(ingredient,
                                 recipe: Recipe,
                                 amount: int):
    """Создает запись в промежуточной БД."""
    return IngredientForRecipe.objects.create(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=amount
            )


def is_exists(id: int) -> bool:
    """Возвращает результат проверки на существование в БД."""
    return Ingredient.objects.filter(id=id).exists()
