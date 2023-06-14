from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from users.models import User

FIRST_ENDPOINT_ERROR = 0


class SetPasswordTest(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(
            email="test@test.com",
            username="testuser",
            first_name="first_test",
            last_name="last_test",
            password="HelloWorldSecurePassword"
        )
        cls.data = {
            "new_password": "HelloWorldSecurePasswordItNewPassword123123",
            "current_password": "HelloWorldSecurePassword"
        }
        cls.token, cls.created = Token.objects.get_or_create(
            user=SetPasswordTest.user)

        cls.url = reverse("set_password")

    def test_with_unathorized_user(self):
        """
        Проверяем наличие ошиибки при смене пароля с невалидными данными.
        """
        response = self.client.post(SetPasswordTest.url,
                                    data=SetPasswordTest.data,
                                    format="json")
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_with_authorized_user(self):
        """
        Проверяем воозможность смены пароля при валидных даннных.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.post(SetPasswordTest.url,
                                    data=SetPasswordTest.data,
                                    format="json")
        self.assertEqual(response.status_code,
                         status.HTTP_204_NO_CONTENT)

    def test_witout_fields(self):
        """
        Проверяем наличие ошибки при отсутствии обязательных полей.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.post(SetPasswordTest.url,
                                    format="json")

        for field in ("current_password", "new_password"):
            with self.subTest(field=field):
                self.assertEqual(
                    response.data.get(field)[FIRST_ENDPOINT_ERROR].code,
                    "required",
                    "Проверьте, что при отсутствии обязательных полей" +
                    "эндпойнт возвращает ошибку."
                )
