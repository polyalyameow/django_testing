from http import HTTPStatus
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

from .common import BaseTestCase


class TestNoteCreation(BaseTestCase):
    NOTE_TEXT = "Новый текст"
    NOTE_TITLE = "Новый заголовок"
    NOTE_SLUG = "new-slug"

    def setUp(self):
        self.form_data = {
            "title": self.NOTE_TITLE,
            "text": self.NOTE_TEXT,
            "slug": self.NOTE_SLUG
        }

    def tearDown(self):
        Note.objects.all().delete()

    def test_anonymous_user_cant_create_note(self):
        """
        Анонимный пользователь не может создать заметку,
        происходит переадресация на страницу входа
        """
        initial_count = Note.objects.count()
        response = self.client.post(self.NOTES_ADD, data=self.form_data)
        self.assertRedirects(response,
                             f"{self.USERS_LOGIN}?next={self.NOTES_ADD}")
        self.assertEqual(Note.objects.count(), initial_count)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку"""
        initial_count = Note.objects.count()
        response = self.author_logged.post(
            self.NOTES_ADD,
            data=self.form_data
        )
        self.assertRedirects(response, self.NOTES_SUCCESS)
        created_note = Note.objects.exclude(id=self.note.id).get()
        self.assertEqual(Note.objects.count(), initial_count + 1)
        self.assertEqual(created_note.title, self.form_data["title"])
        self.assertEqual(created_note.text, self.form_data["text"])
        self.assertEqual(created_note.slug, self.form_data["slug"])
        self.assertEqual(created_note.author, self.author)

    def test_not_unique_slug(self):
        """Нельзя создать запись с одинаковым slug"""
        self.form_data["slug"] = self.note.slug
        response = self.author_logged.post(
            self.NOTES_ADD,
            data=self.form_data
        )
        self.assertFormError(
            response,
            "form",
            "slug",
            errors=(self.note.slug + WARNING)
        )

    def test_empty_slug(self):
        """
        Если slug не указан, он должен сформироваться
        автоматически
        """
        self.form_data.pop("slug")
        response = self.author_logged.post(
            self.NOTES_ADD,
            data=self.form_data
        )
        self.assertRedirects(response, self.NOTES_SUCCESS)
        created_note = Note.objects.exclude(id=self.note.id).first()
        self.assertEqual(created_note.slug, slugify(self.form_data["title"]))

    def test_author_can_edit_note(self):
        """
        Если залогиненный пользователь - создатель заметки,
        то он может редактировать свои заметки
        """
        initial_count = Note.objects.count()
        response = self.author_logged.post(
            self.NOTES_EDIT,
            data=self.form_data
        )
        self.assertRedirects(response, self.NOTES_SUCCESS)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.form_data["title"])
        self.assertEqual(updated_note.text, self.form_data["text"])
        self.assertEqual(updated_note.slug, self.form_data["slug"])
        self.assertEqual(initial_count, Note.objects.count())

    def test_other_user_cant_edit_note(self):
        """
        Пользователь, не являющийся автором заметки,
        не может редактировать заметки
        """
        initial_count = Note.objects.count()
        response = self.reader_logged.post(
            self.NOTES_EDIT,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(initial_count, Note.objects.count())

    def test_author_can_delete_note(self):
        """
        Если залогиненный пользователь - создатель заметки,
        то он может удалять свои заметки
        """
        initial_count = Note.objects.count()
        response = self.author_logged.post(self.NOTES_DELETE)
        self.assertRedirects(response, self.NOTES_SUCCESS)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())
        self.assertEqual(initial_count - 1, Note.objects.count())

    def test_other_user_cant_delete_note(self):
        """
        Пользователь, не являющийся автором заметки,
        не может удалять заметки
        """
        initial_count = Note.objects.count()
        response = self.reader_logged.post(self.NOTES_DELETE)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        self.assertEqual(initial_count, Note.objects.count())
