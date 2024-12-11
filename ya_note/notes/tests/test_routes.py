from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username="Автор")
        cls.reader = User.objects.create(username="Читатель")
        cls.author_logged = Client()
        cls.reader_logged = Client()
        cls.author_logged.force_login(cls.author)
        cls.reader_logged.force_login(cls.reader)
        cls.note = Note.objects.create(
            title="Заголовок",
            text="Текст заметки",
            slug="note-slug",
            author=cls.author,
        )
        cls.NOTES_HOME = reverse("notes:home")
        cls.USERS_LOGIN = reverse("users:login")
        cls.USERS_LOGOUT = reverse("users:logout")
        cls.USERS_SIGNUP = reverse("users:signup")
        cls.NOTES_LIST = reverse("notes:list")
        cls.NOTES_ADD = reverse("notes:add")
        cls.NOTES_SUCCESS = reverse("notes:success")
        cls.NOTES_DETAIL = reverse("notes:detail", args=(cls.note.slug,))
        cls.NOTES_EDIT = reverse("notes:edit", args=(cls.note.slug,))
        cls.NOTES_DELETE = reverse("notes:delete", args=(cls.note.slug,))

    def test_pages_availability(self):
        urls = (
            self.NOTES_HOME,
            self.USERS_LOGIN,
            self.USERS_LOGOUT,
            self.USERS_SIGNUP,
        )

        for url in urls:
            with self.subTest():
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            self.NOTES_LIST,
            self.NOTES_ADD,
            self.NOTES_SUCCESS,
        )
        for url in urls:
            with self.subTest():
                response = self.reader_logged.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_list_edit_and_delete(self):
        users_statuses = (
            (self.author_logged, HTTPStatus.OK),
            (self.reader_logged, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            for url in (
                self.NOTES_DETAIL,
                self.NOTES_EDIT,
                self.NOTES_DELETE
            ):
                with self.subTest():
                    response = user.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            self.NOTES_DETAIL,
            self.NOTES_EDIT,
            self.NOTES_DELETE,
            self.NOTES_ADD,
            self.NOTES_SUCCESS,
            self.NOTES_LIST,
        )
        for url in urls:
            with self.subTest():
                redirect_url = f"{self.USERS_LOGIN}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
