import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse

from api.tests.service import StandartTest
from food.models import Favorite, Recipe
from users.models import User

MEDIA_ROOT = tempfile.mkdtemp()
FIRST_RESULT = 0

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
    )


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class FavoritesTest(StandartTest):
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
            user=FavoritesTest.user)
        cls.recipe = Recipe.objects.create(
            name="test_recipe",
            image=SimpleUploadedFile('small.gif',
                                     SMALL_GIF,
                                     content_type='image/gif'),
            cooking_time=1,
            author=FavoritesTest.second_user
        )
        cls.data = {
            "id": FavoritesTest.recipe.id,
            "name": FavoritesTest.recipe.name,
            "image": "http://testserver" + FavoritesTest.recipe.image.url,
            "cooking_time": FavoritesTest.recipe.cooking_time}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_favorite(self):
        """
        Проверяет работу эндпойнта работы с избранными рецептами.
        """
        url = reverse("routers:recipes-favorite", args=[1])

        self.if_is_unathorized_post(url=url, model=Favorite)
        self.success_create_test(url=url, model=Favorite)
        self.dublicate_create_test(url=url, model=Favorite)
        self.success_delete_test(url=url, model=Favorite)
        self.delete_non_saved_object_test(url=url, model=Favorite)

    def _assert_serializer_is_correct(self, data):
        """Проверяет, что у эндпойнта корректно настроен serializer."""
        self._assert_data_exists(data)
        data = {"id": data.get('id'),
                "name": data.get('name'),
                "image": data.get('image'),
                "cooking_time": data.get('cooking_time')
                }
        self.assertEqual(data,
                         FavoritesTest.data,
                         "Проверьте, что у вас правильно настроена." +
                         "выдача избранных товароов.")

    def _assert_data_exists(self, data):
        """Проверяет, что эндпойнт что-либо возвращает."""
        self.assertIsInstance(data, dict,
                              "Проверьте, что эндпойнт что-либо возвращает.")
