from http import HTTPStatus

from django.urls import reverse

from .common import BaseTestCase


class TestRoutes(BaseTestCase):

    def test_pages_availability(self):
        """Страницы для залогиненных и анонимных пользователей"""
        public_urls = [
            reverse("notes:home"), reverse("users:login"),
            reverse("users:logout"), reverse("users:signup")
        ]

        for url in public_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        restricted_urls = [
            self.NOTES_LIST,
            self.NOTES_ADD,
            self.NOTES_SUCCESS,
            self.NOTES_EDIT,
            self.NOTES_DELETE,
        ]

        for url in restricted_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                redirect_url = f"{reverse("users:login")}?next={url}"
                self.assertRedirects(response, redirect_url)

    def test_authenticated_user_access_and_authorization(self):
        """Страницы, доступные залогиненным пользователям"""
        private_urls = [self.NOTES_LIST, self.NOTES_ADD, self.NOTES_SUCCESS]

        for url in private_urls:
            with self.subTest(url=url):
                response = self.author_logged.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        note_urls = [self.NOTES_EDIT, self.NOTES_DELETE]
        for url in note_urls:
            with self.subTest(url=url):
                response = self.reader_logged.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        for url in note_urls:
            with self.subTest(url=url):
                response = self.author_logged.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
