from food.models import Recipe, ShoppingCart
from users.models import User


def is_shopping_cart_exists(recipe: Recipe, user=User) -> bool:
    """Возвращает результат проверки на существование в избранном."""
    return ShoppingCart.objects.filter(recipe=recipe, user=user).exists()
