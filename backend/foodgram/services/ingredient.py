from django.db.models import Sum
from food.models import Ingredient, IngredientForRecipe
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
        ).annotate(total_amount=Sum('amount'))
    return amount


def bulk_create_ingredients_amount(ingredients, recipe):
    IngredientForRecipe.objects.bulk_create([
        IngredientForRecipe(ingredient_id=ingredient['id'],
                            recipe=recipe,
                            amount=ingredient['amount']
                            ) for ingredient in ingredients]
    )


def is_exists(id: int) -> bool:
    """Возвращает результат проверки на существование в БД."""
    return Ingredient.objects.filter(id=id).exists()
