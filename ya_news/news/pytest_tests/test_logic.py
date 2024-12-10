from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

# Анонимный пользователь не может отправить комментарий.
# Авторизованный пользователь может отправить комментарий.
# Если комментарий содержит запрещённые слова, он не будет
# опубликован, а форма вернёт ошибку.
# Авторизованный пользователь может редактировать или
# удалять свои комментарии.
# Авторизованный пользователь не может редактировать
# или удалять чужие комментарии.

TEXT_COMMENT = "Текст комментария"


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, new_text_comment, news):
    url = reverse("news:detail", args=(news.id,))
    client.post(url, data=new_text_comment)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, new_text_comment,
                                 news):
    url = reverse("news:detail", args=(news.id,))
    author_client.post(url, data=new_text_comment)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == new_text_comment["text"]
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    bad_words_data = {"text": f"Tекст, {BAD_WORDS[0]}, еще текст"}
    url = reverse("news:detail", args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form="form",
        field="text",
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_delete_own_comment(author_client, news, comment):
    news_url = reverse("news:detail", args=(news.id,))
    url_to_comments = reverse("news:delete", args=(comment.id,))
    response = author_client.delete(url_to_comments)
    assertRedirects(response, news_url + "#comments")
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_edit_own_comment(author_client, new_text_comment, news, comment):
    news_url = reverse("news:detail", args=(news.id,))
    comment_url = reverse("news:edit", args=(comment.id,))
    response = author_client.post(comment_url, data=new_text_comment)
    assertRedirects(response, news_url + "#comments")
    comment.refresh_from_db()
    assert comment.text == new_text_comment["text"]


def test_delete_comment_of_another_user(admin_client, comment):
    comment_url = reverse("news:delete", args=(comment.id,))
    response = admin_client.delete(comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_edit_comment_of_another_user(admin_client, new_text_comment, comment):
    comment_url = reverse("news:edit", args=(comment.id,))
    response = admin_client.post(comment_url, data=new_text_comment)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == TEXT_COMMENT
