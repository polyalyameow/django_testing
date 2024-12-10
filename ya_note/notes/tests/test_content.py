
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


# 1. отдельная заметка передаётся на страницу со
# списком заметок в списке object_list в словаре context;
# 2. в список заметок одного пользователя не попадают
# заметки другого пользователя;
# 3. на страницы создания и редактирования заметки
# передаются формы.

User = get_user_model()


class TestContent(TestCase):

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

    def test_list_notes_for_different_users(self):

        user_status = (
            (self.author_logged, True),
            (self.reader_logged, False),
        )

        for user, status in user_status:
            with self.subTest():
                response = user.get(self.NOTES_LIST)
                object_list = response.context["object_list"]
                self.assertEqual(self.note in object_list, status)

    def test_pages_contain_forms(self):
        urls = (self.NOTES_ADD, self.NOTES_EDIT)

        for url in urls:
            with self.subTest():
                response = self.author_logged.get(url)
                self.assertIn("form", response.context)
