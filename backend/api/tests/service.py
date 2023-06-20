from rest_framework import status
from rest_framework.test import APITestCase

FIRST_RESULT = 0


class StandartTest(APITestCase):
    def if_is_unathorized_post(self, url, model):
        response = self.client.post(url)
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED,
                         "Проверьте, что неавторизованному пользователю " +
                         "эндпойнт возвращает статус HTTP_401_UNAUTHORIZED")
        self.assertEqual(model.objects.all().count(),
                         0,
                         "Проверьте, что неавторизованный пользователь" +
                         " не может создавать объект.")

    def success_create_test(self, url: str, model, data: dict = {}):
        """
        Проверяет эндпойнт на возможность создания с успешными данными.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED,
                         "Проверьте, что при успешном добавлении" +
                         ", эндпойнт возвращает статус HTTP_201_CREATED")
        self._assert_serializer_is_correct(response.data)

    def dublicate_create_test(self, url: str, model):
        """
        Проверяет эндпойнт на возможность создания дубликата.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.client.post(url)
        response = self.client.post(url)
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST,
                         "Проверьте, что при попытке повторного добавления" +
                         ", эндпойнт возвращает" +
                         "статус HTTP_400_BAD_REQUEST")

    def success_delete_test(self, url: str, model):
        """
        Проверяет эндпойнт на возможность удаления объектов.
        """
        old_value = model.objects.all().count()
        response = self.client.delete(url)
        self.assertEqual(response.status_code,
                         status.HTTP_204_NO_CONTENT,
                         "Проверьте, что при успешном удалении от" +
                         " пользователя, эндпойнт возвращает" +
                         "статус HTTP_204_NO_CONTENT")
        self.assertEqual(old_value-1,
                         model.objects.all().count(),
                         "Проверьте, что при успешном ответе эндпойнта" +
                         "объект удаляется из БД.")

    def delete_non_saved_object_test(self, url: str, model):
        """
        Проверяет эндпойнта при попытке удалить несохраненный объект.
        """
        response = self.client.delete(url)
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST,
                         "Проверьте, что при попытке удаления рецепта," +
                         " который не в избранном," +
                         "эндпойнт возвращает статус HTTP_400_BAD_REQUEST")

    def _assert_serializer_is_correct(self, data):
        """Проверяет, что у эндпойнта корректно настроен serializer."""
        pass
