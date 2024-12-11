from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = "Новый текст"
    NOTE_TITLE = "Новый заголовок"
    NOTE_SLUG = "new-slug"

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

        cls.form_data = {
            "title": cls.NOTE_TITLE,
            "text": cls.NOTE_TEXT,
            "slug": cls.NOTE_SLUG
        }
        cls.NOTES_BEFORE_REQUEST = Note.objects.count()
        cls.NOTES_ADD = reverse("notes:add")
        cls.USERS_LOGIN = reverse("users:login")
        cls.NOTES_EDIT = reverse("notes:edit", args=(cls.note.slug,))
        cls.NOTES_DELETE = reverse("notes:delete", args=(cls.note.slug,))
        cls.NOTES_SUCCESS = reverse("notes:success")

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.NOTES_ADD, data=self.form_data)
        self.assertRedirects(response,
                             f"{self.USERS_LOGIN}?next={self.NOTES_ADD}")
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.NOTES_BEFORE_REQUEST)

    def test_user_can_create_note(self):
        response = self.author_logged.post(
            self.NOTES_ADD,
            data=self.form_data
        )
        self.assertRedirects(response, self.NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE_REQUEST + 1)
        new_note = Note.objects.order_by("id").last()
        self.assertEqual(new_note.title, self.form_data["title"])
        self.assertEqual(new_note.text, self.form_data["text"])
        self.assertEqual(new_note.slug, self.form_data["slug"])
        self.assertEqual(new_note.author, self.author)

    def test_not_unique_slug(self):
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
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE_REQUEST)

    def test_empty_slug(self):
        self.form_data.pop("slug")
        response = self.author_logged.post(
            self.NOTES_ADD,
            data=self.form_data
        )
        self.assertRedirects(response, self.NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE_REQUEST + 1)
        new_note = Note.objects.order_by("id").last()
        expected_slug = slugify(self.form_data["title"])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        response = self.author_logged.post(
            self.NOTES_EDIT,
            data=self.form_data
        )
        self.assertRedirects(response, self.NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE_REQUEST)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data["title"])
        self.assertEqual(new_note.text, self.form_data["text"])
        self.assertEqual(new_note.slug, self.form_data["slug"])

    def test_other_user_cant_edit_note(self):
        response = self.reader_logged.post(
            self.NOTES_EDIT,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        response = self.author_logged.post(self.NOTES_DELETE)
        self.assertRedirects(response, self.NOTES_SUCCESS)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE_REQUEST - 1)

    def test_other_user_cant_delete_note(self):
        response = self.reader_logged.post(self.NOTES_DELETE)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), self.NOTES_BEFORE_REQUEST)
