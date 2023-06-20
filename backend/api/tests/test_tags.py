from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from food.models import Tag

FIRST_TAG = 0
FIRST_ENDPOINT_ERROR = 0


class TagsTest(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.tag = Tag.objects.create(
            name="Завтрак",
            color="#8775fD2",
            slug="breakfast"
        )
        cls.data = {"id": TagsTest.tag.id,
                    "name": TagsTest.tag.name,
                    "color": TagsTest.tag.color,
                    "slug": TagsTest.tag.slug}

    def test_get_list_tags(self):
        """
        Проверяем работу эндпойнта по получению списка тэгов.
        """
        url = reverse("routers:tags-list")
        response = self.client.get(url)
        self._assert_status_code_is_200(response.status_code)
        self._assert_serializer_is_correct(
            response.data[FIRST_TAG])

    def test_get_tag_by_id(self):
        """
        Проверяем работу эндпойнта по получения тэга по ID.
        """
        url = reverse("routers:tags-detail", args=[1])
        response = self.client.get(url)
        self._assert_status_code_is_200(response.status_code)
        self._assert_serializer_is_correct(response.data)

        url = reverse("routers:tags-detail", args=[2])
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Проверьте, что эндпойнт возвращает статус " +
            "HTTP_404_NOT_FOUND, если такого объекта не существует.")
        self._assert_data_exists(response.data)
        self.assertEqual(
            response.data.get("detail"),
            NotFound.default_detail,
            "Проверьте, что эндпойнт возвращает ошибку, " +
            "если такого объекта не существует")

    def _assert_status_code_is_200(self, status_code: status):
        "Проверяет, что статус эндпойнта равен HTTP_200_OK."
        self.assertEqual(status_code, status.HTTP_200_OK,
                         "Проверьте, что эндпойнт " +
                         "возвращает статус HTTP_200_OK")

    def _assert_serializer_is_correct(self, data):
        "Проверяет, что у эндпойнта корректно настроен serializer."
        self.assertEqual(data,
                         TagsTest.data,
                         "Проверьте, что у вас правильно настроена." +
                         "выдача тэгов.")

    def _assert_data_exists(self, data):
        "Проверяет, что эндпойнт что-либо возвращает."
        self.assertIsInstance(data, dict,
                              "Проверьте, что эндпойнт что-либо возвращает.")
