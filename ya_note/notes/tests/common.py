from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class BaseTestCase(TestCase):
    """Общий сет-ап для тестов"""

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
        cls.NOTES_LIST = reverse("notes:list")
        cls.NOTES_ADD = reverse("notes:add")
        cls.NOTES_EDIT = reverse("notes:edit", args=(cls.note.slug,))
        cls.NOTES_DELETE = reverse("notes:delete", args=(cls.note.slug,))
        cls.USERS_LOGIN = reverse("users:login")
        cls.NOTES_SUCCESS = reverse("notes:success")
