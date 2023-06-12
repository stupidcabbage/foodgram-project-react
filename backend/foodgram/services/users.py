from users.models import User


def get_all_users() -> User:
    """Возвращает список всех пользователей."""
    return User.objects.all()


def get_user_sucribers(value: User) -> User:
    """Возвращает список пользователей, на которых он подписан."""
    return User.objects.filter(subscriber__user=value)
