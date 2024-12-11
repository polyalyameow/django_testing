from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

TEXT_COMMENT = "Текст комментария"


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_detail_url):
    response = client.get(news_detail_url)
    assert response.status_code == 200
    initial_count = Comment.objects.count()
    client.post(news_detail_url, data={"text": TEXT_COMMENT})
    assert Comment.objects.count() == initial_count


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author,
                                 news_detail_url, news):
    response = author_client.get(news_detail_url)
    assert response.status_code == 200
    initial_count = Comment.objects.count()
    author_client.post(news_detail_url, data={"text": TEXT_COMMENT})
    assert Comment.objects.count() == initial_count + 1
    comment = Comment.objects.get(author=author, text=TEXT_COMMENT)
    assert comment.text == TEXT_COMMENT
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news_detail_url):
    bad_words_data = {"text": f"Tекст, {BAD_WORDS[0]}, еще текст"}
    response = author_client.get(news_detail_url)
    assert response.status_code == 200
    initial_count = Comment.objects.count()
    response = author_client.post(news_detail_url, data=bad_words_data)
    assertFormError(
        response,
        form="form",
        field="text",
        errors=WARNING
    )
    assert Comment.objects.count() == initial_count


@pytest.mark.django_db
def test_delete_own_comment(author_client, news, comment,
                            news_detail_url, delete_comment_url):
    response = author_client.delete(delete_comment_url)
    assertRedirects(response, news_detail_url + "#comments")
    assert not Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_edit_own_comment(author_client, news, comment,
                          news_detail_url, comment_edit_url, author):
    news_url = news_detail_url
    comment_url = comment_edit_url
    response = author_client.post(comment_url, data={"text": TEXT_COMMENT})
    assertRedirects(response, news_url + "#comments")
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == TEXT_COMMENT
    assert updated_comment.news == news
    assert updated_comment.author == comment.author


@pytest.mark.django_db
def test_delete_comment_of_another_user(admin_client, comment,
                                        delete_comment_url):
    initial_count = Comment.objects.count()
    response = admin_client.delete(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count
    assert Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_edit_comment_of_another_user(admin_client, comment, comment_edit_url):
    initial_comment = Comment.objects.get(id=comment.id)
    response = admin_client.post(comment_edit_url, data={"text": TEXT_COMMENT})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert initial_comment.text == comment.text
