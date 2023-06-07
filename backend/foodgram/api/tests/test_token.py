from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from users.models import User

FIRST_ENDPOINT_ERROR = 0


class GetTokenTest(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(
            email='test@test.com',
            username='testuser',
            first_name='first_test',
            last_name='last_test',
            password='HelloWorldSecurePassword'
        )
        cls.data = {
            "email": 'test@test.com',
            "password": 'HelloWorldSecurePassword'
        }

    def test_get_token_with_correct_data(self):
        """
        Проверяем возможность получения токена с валидными данными.
        """
        url = reverse('login')
        data = GetTokenTest.data
        response = self.client.post(url, data, format='json')
        expected_token, created = Token.objects.get_or_create(
            user=GetTokenTest.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         'Проверьте, что при попытке получения токена, ' +
                         'эндпойнт возвращает статус HTT_200_OK')
        self.assertIsNotNone(response.data.get('auth_token'),
                             'Проверьте сущецствование поля auth_token.')
        self.assertEqual(response.data.get('auth_token'), expected_token.key,
                         'Проверьте, что получении токена ' +
                         'он возвращает верное значение.')

    def test_get_token_without_email_and_password(self):
        """
        Проверяем возможность создания токена с невалидными данными.
        """
        url = reverse('login')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         'Проверьте, что при отсутствии полей эндпойнт' +
                         'возвращает статус HTTP_400_BAD_REQUEST')
        self.assertEqual(Token.objects.count(), 0,
                         'Проверьте, что передаче невалидных данных' +
                         'токен не сохраняется в БД.')
        for field in ('email', 'password'):
            with self.subTest(field=field):
                self.assertEqual(
                    response.data.get(field)[FIRST_ENDPOINT_ERROR].code,
                    'required',
                    f'Проверьте, что в случае отсутствия {field}' +
                    ' эндпойнт возвращает ошибку.')


class LogoutTokenTest(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(
            email='test@test.com',
            username='testuser',
            first_name='first_test',
            last_name='last_test',
            password='HelloWorldSecurePassword'
        )
        cls.url = reverse('logout')

    def setUp(self):
        self.token, self.created = Token.objects.get_or_create(
            user=LogoutTokenTest.user)

    def test_logout_with_correct_data(self):
        """
        Проверяем возможность выхода пользователя с валидными данными.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(LogoutTokenTest.url)
        self.assertEqual(response.status_code,
                         status.HTTP_204_NO_CONTENT,
                         'Проверьте, что при передаче валидных данных' +
                         ' эндпойнт возвращает статус HTTP_204_NO_CONTENT')

    def test_logout_with_incorrect_data(self):
        """
        Проверяем возможность выхода пользователя с невалидными данными.
        """
        response = self.client.post(LogoutTokenTest.url)
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED,
                         'Проверьте, что при передаче невалидных данных' +
                         ' эндпойнт возвращает статус HTTP_401_UNAUTHORIZED')
        self.assertEqual(
            response.data.get('detail'),
            _('Authentication credentials were not provided.'),
            'Проверьте, что если пользователь не авторизован, ' +
            'эндпойнт возвращает ошибку.')
