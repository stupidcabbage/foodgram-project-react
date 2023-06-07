from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from users.models import User

FIRST_RESULT = 0


class UserTest(APITestCase):
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
        cls.token, cls.created = Token.objects.get_or_create(
            user=UserTest.user)
        cls.data = {
            "email": UserTest.user.email,
            "id": UserTest.user.id,
            "username": UserTest.user.username,
            "first_name": UserTest.user.first_name,
            "last_name": UserTest.user.last_name
        }

    def test_get_users_list(self):
        """
        Проверяет возможность получения списка всех пользователей.
        """
        url = reverse("routers:user-list")
        response = self.client.get(url)
        self._assert_status_code_is_401(response.status_code)

        response = self._authorize_client_and_get_response(url=url)
        self._assert_status_code_is_200(response.status_code)
        self.assertEqual(response.data.get("count"), 1,
                         "Проверьте, что у вас включена пагинация" +
                         "по страницам.")
        self._assert_serializer_is_correct(
            response.data.get('results')[FIRST_RESULT])

    def test_get_user_by_id(self):
        """
        Проверяет эндпойнт получения пользователя по ID.
        """
        url = reverse("routers:user-detail", args=[2])

        response = self.client.get(url)
        self._assert_status_code_is_401(response.status_code)

        response = self._authorize_client_and_get_response(url=url)
        self.assertEqual(response.status_code,
                         status.HTTP_404_NOT_FOUND,
                         "Проверьте, что если пользователя не существует" +
                         " эндпойнт возвращает статус HTTP_404_NOT_FOUND")

        url = reverse("routers:user-detail", args=[1])
        response = self._authorize_client_and_get_response(url=url)

        self._assert_status_code_is_200(response.status_code)
        self._assert_serializer_is_correct(response.data)

    def test_self_user_account(self):
        """
        Проверяет энпойнт получения личного аккаунта.
        """
        url = reverse('routers:user-me')
        response = self.client.get(url)
        self._assert_status_code_is_401(response.status_code)

        response = self._authorize_client_and_get_response(url=url)
        self._assert_status_code_is_200(response.status_code)
        self._assert_serializer_is_correct(response.data)

    def _authorize_client_and_get_response(self, url: str):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        return self.client.get(url)

    def _assert_status_code_is_200(self, status_code: status):
        "Проверяет, что статус эндпойнта равен HTTP_200_OK."
        self.assertEqual(status_code, status.HTTP_200_OK,
                         "Проверьте, что эндпойнт " +
                         "возвращает статус HTTP_200_OK")

    def _assert_status_code_is_401(self, status_code: status):
        "Проверяет, что статус эндпойнта равен HTTP_401_UNAUTHORIZED."
        self.assertEqual(status_code,
                         status.HTTP_401_UNAUTHORIZED,
                         "Проверьте, что неавторизованным пользователям" +
                         " эндпойнт возвращает статус HTTP_401_UNAUTHORIZED")

    def _assert_serializer_is_correct(self, data):
        "Проверяет, что у эндпойнта корректно настроен serializer."
        self._assert_data_exists(data)
        self.assertEqual(data,
                         UserTest.data,
                         "Проверьте, что у вас правильно настроен serializer" +
                         "для эндпойнта.")

    def _assert_data_exists(self, data):
        "Проверяет, что эндпойнт что-либо возвращает."
        self.assertIsInstance(data, dict,
                              "Проверьте, что эндпойнт что-либо возвращает.")
