from .common import BaseTestCase


class TestContent(BaseTestCase):

    def test_list_notes_for_different_users(self):
        """Отображаются записи залогиненного пользователя"""
        user_status = (
            (self.author_logged, True),
            (self.reader_logged, False),
        )

        for user, status in user_status:
            with self.subTest(user=user):
                response = user.get(self.NOTES_LIST)
                object_list = response.context["object_list"]
                self.assertEqual(self.note in object_list, status)

    def test_pages_contain_forms(self):
        """
        На страницы создания и редактирования заметок
        передаются формы
        """
        urls = (self.NOTES_ADD, self.NOTES_EDIT)

        for url in urls:
            with self.subTest(url=url):
                response = self.author_logged.get(url)
                self.assertIn("form", response.context)
                self.assertEqual(type(response.context["form"]
                                      ).__name__, "NoteForm")
