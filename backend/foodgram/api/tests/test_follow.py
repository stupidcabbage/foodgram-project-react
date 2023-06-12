import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from food.models import Recipe
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from users.models import Follow, User
from api.tests.service import StandartTest

MEDIA_ROOT = tempfile.mkdtemp()
FIRST_RESULT = 0

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
    )


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class FollowTest(StandartTest):
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
        cls.second_user = User.objects.create_user(
            email="test2@test.com",
            username="testuser2",
            first_name="first_test2",
            last_name="last_test2",
            password="HelloWorldSecurePassword"
            )
        cls.token, cls.created = Token.objects.get_or_create(
            user=FollowTest.user)
        cls.recipe = Recipe.objects.create(
            name="test_recipe",
            image=SimpleUploadedFile('small.gif',
                                     SMALL_GIF,
                                     content_type='image/gif'),
            cooking_time=1,
            author=FollowTest.second_user
        )
        cls.data = {
            "email": FollowTest.second_user.email,
            "id": FollowTest.second_user.id,
            "username": FollowTest.second_user.username,
            "first_name": FollowTest.second_user.first_name,
            "last_name": FollowTest.second_user.last_name,
            "is_subscribed": True,
            "recipes": [{
                "id": FollowTest.recipe.id,
                "name": FollowTest.recipe.name,
                "image": "http://testserver" + FollowTest.recipe.image.url,
                "cooking_time": FollowTest.recipe.cooking_time}],
            "recipes_count": 1
        }

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_subscribe(self):
        """
        Проверяем работу эндпойнта подписки на пользователя.
        """
        url = reverse("routers:user-subscribe", args=[2])

        self.if_is_unathorized_post(url=url, model=Follow)
        self.success_create_test(url=url, model=Follow)
        self.dublicate_create_test(url=url, model=Follow)
        self.success_delete_test(url=url, model=Follow)
        self.delete_non_saved_object_test(url=url, model=Follow)

        url = reverse("routers:user-subscribe", args=[1])
        response = self.client.post(url)
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST,
                         "Проверьте, что при попытке подписки на самого себя" +
                         ", эндпойнт возвращает статус HTTP_400_BAD_REQUEST")

    def test_subscriptions(self):
        """
        Проверяем работу эндпойнта вывода списка подписок.
        """
        url = reverse("routers:user-subscriptions")
        self.if_is_unathorized_post(url=url, model=Follow)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.client.post(
            reverse("routers:user-subscribe", args=[2]))

        response = self.client.get(url)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK,
                         "Проверьте, что эндпойнт " +
                         "возвращает статус HTTP_200_OK")

        self.assertEqual(response.data.get("count"), 1,
                         "Проверьте, что у вас включена пагинация" +
                         "по страницам.")
        self._assert_serializer_is_correct(
            response.data.get("results")[FIRST_RESULT])

    def _assert_response_code_is_unathorized(self, status_code):
        """Прооверяет, что код сооответствует 401_UNATHORIZED."""
        self.assertEqual(status_code,
                         status.HTTP_401_UNAUTHORIZED,
                         "Проверьте, что неавторизованному пользователю " +
                         "эндпойнт возвращает статус HTTP_401_UNAUTHORIZED")

    def _assert_serializer_is_correct(self, data):
        """Проверяет, что у эндпойнта корректно настроен serializer."""
        self._assert_data_exists(data)
        data['recipes'] = [{"id": data['recipes'][0].get('id'),
                            "name": data['recipes'][0].get('name'),
                            "image": data['recipes'][0].get('image'),
                            "cooking_time": data['recipes'][0].get(
                                'cooking_time')}]
        self.assertRaises(
            KeyError,
            msg='Проверьте, что у вас правильно настроена выдача подписок.')
        self.assertEqual(data,
                         FollowTest.data,
                         "Проверьте, что у вас правильно настроена." +
                         "выдача подписок.")

    def _assert_data_exists(self, data):
        """Проверяет, что эндпойнт что-либо возвращает."""
        self.assertIsInstance(data, dict,
                              "Проверьте, что эндпойнт что-либо возвращает.")
