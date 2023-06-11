from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from users.models import User

FIRST_ENDPOINT_ERROR = 0


class UserRegisterTest(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.url = reverse("routers:user-list")

    def test_create_account(self):
        """
        Проверяем возможность создания пользователя с корректными данными.
        """
        url = UserRegisterTest.url
        data = {"email": "testemail@test.com",
                "username": "testuser",
                "first_name": "first_test",
                "last_name": "second_test",
                "password": "test123123",
                "id": 2}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         "При создании аккаунта статус код не 201_CREATED: " +
                         f"{response.status_code}" +
                         "\nПроверьте корректность работы эндпойнта.")
        self.assertEqual(User.objects.count(), 1,
                         "Аккаунт не сохраняется в базе данных, " +
                         "после успешного ответа от эндпойнта.")
        self.assertEqual(response.data.get("id"), 1,
                         "Поле ID не совпадает с ожидаемым.\n" +
                         "Проверьте наличие/возможность изменения поля" +
                         "принудительно при передаче его при регистрациии.")

        del data["password"]
        data["id"] = 1
        self.assertEqual(response.data, data,
                         "Проверьте, что все поля соответсвуют документации" +
                         "при успешном запросе.")

    def test_create_account_with_long_values(self):
        """
        Провеярем наличие ошибки при использовании невалидных длинных значений.
        """
        url = UserRegisterTest.url
        data = {"email": f"{'a'*245}@test.test",
                "username": "a"*151,
                "first_name": "a"*151,
                "last_name": "a"*151,
                "password": "test123123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         "При отправлении некорректных данных эндпойнт" +
                         "должен возвращать 400_BAD_REQUEST")
        self.assertEqual(User.objects.count(), 0,
                         "Аккаунт сохраняется в базе данных, " +
                         "после неуспешного ответа от эндпойнта.")

        del data["password"]
        for field in data:
            with self.subTest(field=field):
                self.assertEqual(
                    response.data.get(field)[FIRST_ENDPOINT_ERROR].code,
                    "max_length",
                    f"Провеьте, что при отправлении длинного поля {field}," +
                    " эндпойнт возвращает ошибку")

    def test_create_dublicate_account(self):
        """
        Проверяем отсутствие возможности создать два одиноковых аккаунтов.
        """
        url = UserRegisterTest.url
        data = {"email": "testemail@test.com",
                "username": "testuser",
                "first_name": "first_test",
                "last_name": "second_test",
                "password": "test123123"}
        self.client.post(url, data, format="json")
        second_response = self.client.post(url, data, format="json")

        self.assertEqual(User.objects.count(), 1,
                         "Проверьте, что аккаунт дубликат не может быть создан"
                         )

        for field in ("username", "email"):
            with self.subTest(field=field):
                self.assertEqual(
                    second_response.data.get(field)[FIRST_ENDPOINT_ERROR].code,
                    "unique",
                    "Проверьте, что невозможно создать аккаунты" +
                    "с одинаковыми полями и эндпойнт возвращает ошибку."
                )
