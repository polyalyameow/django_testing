from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

TEXT_COMMENT = "Текст комментария"


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news_detail_url):
    """Анонимный пользователь не может отправить комментарий"""
    response = client.get(news_detail_url)
    assert response.status_code == 200
    initial_count = Comment.objects.count()
    client.post(news_detail_url, data={"text": TEXT_COMMENT})
    assert Comment.objects.count() == initial_count


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author,
                                 news_detail_url, news):
    """
    Залогиненный пользователь может отправить
    комментарий
    """
    response = author_client.get(news_detail_url)
    assert response.status_code == 200
    initial_count = Comment.objects.count()

    response = author_client.post(news_detail_url, data={"text": TEXT_COMMENT})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_count + 1

    new_comment = Comment.objects.latest('id')
    assert new_comment.text == TEXT_COMMENT
    assert new_comment.news == news
    assert new_comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news_detail_url):
    """Нельзя использовать определенные слова"""
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
    """Залогиненный пользователь может удалить свой коммент"""
    initial_count = Comment.objects.count()
    response = author_client.delete(delete_comment_url)
    assertRedirects(response, news_detail_url + "#comments")
    assert not Comment.objects.filter(id=comment.id).exists()
    assert Comment.objects.count() == initial_count - 1


@pytest.mark.django_db
def test_edit_own_comment(author_client, news, comment,
                          news_detail_url, comment_edit_url, author):
    """Залогиненный пользователь может изменить свой коммент"""
    initial_count = Comment.objects.count()
    response = author_client.post(comment_edit_url,
                                  data={"text": TEXT_COMMENT})
    assertRedirects(response, news_detail_url + "#comments")
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == TEXT_COMMENT
    assert updated_comment.news == news
    assert updated_comment.author == comment.author
    assert Comment.objects.count() == initial_count


@pytest.mark.django_db
def test_delete_comment_of_another_user(admin_client, comment,
                                        delete_comment_url):
    """Пользователь не может удалить чужой коммент"""
    initial_comment = Comment.objects.get(id=comment.id)
    initial_count = Comment.objects.count()
    response = admin_client.delete(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count
    assert Comment.objects.filter(id=comment.id).exists()
    assert initial_comment.text == comment.text
    assert initial_comment.author == comment.author
    assert initial_comment.news == comment.news


@pytest.mark.django_db
def test_edit_comment_of_another_user(admin_client, comment, comment_edit_url):
    """Пользователь не может отредактировать чужой коммент"""
    initial_count = Comment.objects.count()
    initial_comment = Comment.objects.get(id=comment.id)
    response = admin_client.post(comment_edit_url, data={"text": TEXT_COMMENT})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count
    assert initial_comment.text == comment.text
    assert initial_comment.author == comment.author
    assert initial_comment.news == comment.news
