from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User


class UserTest(APITestCase):
    def test_create_account(self):
        """
        Проверяем возможность создания пользователя с корректными данными.
        """
        url = reverse('register')
        data = {'email': 'testemail@test.com',
                'username': 'testuser',
                'first_name': 'first_test',
                'last_name': 'second_test',
                'password': 'test123123',
                'id': 2}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         'При создании аккаунта статус код не 201_CREATED: ' +
                         f'{response.status_code}' +
                         '\nПроверьте корректность работы эндпойнта.')
        self.assertEqual(User.objects.count(), 1,
                         'Аккаунт не сохраняется в базе данных, ' +
                         'после успешного ответа от эндпойнта.')
        self.assertEqual(response.data.get('id'), 1,
                         'Поле ID не совпадает с ожидаемым.\n' +
                         'Проверьте наличие/возможность изменения поля' +
                         'принудительно при передаче его при регистрациии.')

        del data['password']
        data['id'] = 1
        self.assertEqual(response.data, data,
                         'Проверьте, что все поля соответсвуют документации' +
                         'при успешном запросе.')

    def test_create_account_with_long_values(self):
        """
        Провеярем наличие ошибки при использовании невалидных длинных значений.
        """
