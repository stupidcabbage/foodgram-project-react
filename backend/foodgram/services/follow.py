from users.models import Follow, User


def create_follow(user: User, author: User) -> Follow:
    """Создает модель подписки."""
    return Follow.objects.create(user=user, author=author)


def delete_follow(user: User, author: User) -> Follow:
    """Удаляет модель подписки."""
    return Follow.objects.filter(user=user, author=author).delete()


def follow_exists(user: User, author: User) -> bool:
    """Возвращает результат проверки на существование подписки."""
    return Follow.objects.filter(user=user, author=author).exists()
