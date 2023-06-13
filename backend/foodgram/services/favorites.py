from food.models import Favorite, Recipe
from users.models import User


def is_favorite_exists(recipe: Recipe, user=User) -> bool:
    """Возвращает результат проверки на существование в любимом."""
    return Favorite.objects.filter(recipe=recipe, user=user).exists()
