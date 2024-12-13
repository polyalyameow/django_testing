from http import HTTPStatus

from django.urls import reverse

from .common import BaseTestCase


URLS = {
    "public": [
        {"url": reverse("notes:home"), "expected_status": HTTPStatus.OK,
         "is_public": True},
        {"url": reverse("users:login"), "expected_status": HTTPStatus.OK,
         "is_public": True},
        {"url": reverse("users:logout"), "expected_status": HTTPStatus.OK,
         "is_public": True},
        {"url": reverse("users:signup"), "expected_status": HTTPStatus.OK,
         "is_public": True},
    ],
    "restricted": [
        {"url": "NOTES_LIST", "expected_status": HTTPStatus.FOUND,
         "is_public": False},
        {"url": "NOTES_ADD", "expected_status": HTTPStatus.FOUND,
         "is_public": False},
        {"url": "NOTES_SUCCESS", "expected_status": HTTPStatus.FOUND,
         "is_public": False},
        {"url": "NOTES_EDIT", "expected_status": HTTPStatus.FOUND,
         "is_public": False},
        {"url": "NOTES_DELETE", "expected_status": HTTPStatus.FOUND,
         "is_public": False},
    ],
    "private_author_only": [
        {"url": "NOTES_EDIT", "expected_status": HTTPStatus.OK,
         "auth_type": "author_logged"},
        {"url": "NOTES_DELETE", "expected_status": HTTPStatus.OK,
         "auth_type": "author_logged"},
    ],
    "private_reader": [
        {"url": "NOTES_EDIT", "expected_status": HTTPStatus.NOT_FOUND,
         "auth_type": "reader_logged"},
        {"url": "NOTES_DELETE", "expected_status": HTTPStatus.NOT_FOUND,
         "auth_type": "reader_logged"},
    ],
}


class TestRoutes(BaseTestCase):
    def test_pages_availability(self):
        """Страницы для залогиненных и анонимных пользователей"""
        urls = URLS["public"] + URLS["restricted"]

        for entry in urls:
            with self.subTest(url=entry["url"]):
                response = self.client.get(getattr(
                    self, entry["url"], entry["url"]))

                self.assertEqual(response.status_code,
                                 entry["expected_status"])

    def test_redirect(self):
        """Страницы, доступные залогиненным пользователям"""
        urls = URLS["restricted"]

        for entry in urls:
            with self.subTest(url=entry["url"]):
                redirect_url = f"{reverse('users:login')}?next={getattr(
                    self, entry['url'], entry['url'])}"
                response = self.client.get(getattr(
                    self, entry["url"], entry["url"]))
                self.assertRedirects(response, redirect_url)
