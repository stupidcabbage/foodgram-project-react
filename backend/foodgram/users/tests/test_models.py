from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(
            email='test@test.com',
            username='testuser',
            first_name='first_test',
            last_name='last_test',
            password='HelloWorldSecurePassword'
        )

    def test_models_have_correct_objects_name(self):
        """Проверяем корректиность работы __str__."""
        user = UserModelTest.user
        expected_objects_name = user.username
        self.assertEqual(expected_objects_name, str(user))

    def test_models_have_index(self):
        """Проверяем наличие индексации у моделей."""
        user = UserModelTest.user
        self.assertIsNotNone(user.id)
