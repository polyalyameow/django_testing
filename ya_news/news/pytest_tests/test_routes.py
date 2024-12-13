from http import HTTPStatus

from django.test import Client
import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse

from .conftest import LOGIN_URL, LOGOUT_URL, NEWS_HOME, SIGNUP_URL


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, client, expected_status',
    (
        (NEWS_HOME, Client(), HTTPStatus.OK),
        (LOGIN_URL, Client(), HTTPStatus.OK),
        (LOGOUT_URL, Client(), HTTPStatus.OK),
        (SIGNUP_URL, Client(), HTTPStatus.OK),
        ("news:detail", Client(), HTTPStatus.OK),
        (NEWS_HOME, pytest.lazy_fixture("author_client"), HTTPStatus.OK),
        (LOGIN_URL, pytest.lazy_fixture("author_client"), HTTPStatus.OK),
        (LOGOUT_URL, pytest.lazy_fixture("author_client"), HTTPStatus.OK),
        (SIGNUP_URL, pytest.lazy_fixture("author_client"), HTTPStatus.OK),
        ("news:delete", pytest.lazy_fixture("author_client"), HTTPStatus.OK),
        ("news:edit", pytest.lazy_fixture("author_client"), HTTPStatus.OK),
        ("news:detail", pytest.lazy_fixture("author_client"), HTTPStatus.OK),
        (NEWS_HOME, pytest.lazy_fixture("reader_client"), HTTPStatus.OK),
        (LOGIN_URL, pytest.lazy_fixture("reader_client"), HTTPStatus.OK),
        (LOGOUT_URL, pytest.lazy_fixture("reader_client"), HTTPStatus.OK),
        (SIGNUP_URL, pytest.lazy_fixture("reader_client"), HTTPStatus.OK),
        ("news:delete", pytest.lazy_fixture("reader_client"), HTTPStatus.NOT_FOUND),
        ("news:edit", pytest.lazy_fixture("reader_client"), HTTPStatus.NOT_FOUND),
        ("news:detail", pytest.lazy_fixture("reader_client"), HTTPStatus.OK),
    ),
)
def test_pages_availability(
    url, client, expected_status, news, comment
):
    """Страницы, доступные разным пользователям"""
    if url == "news:detail":
        url = reverse(url, args=[news.id])
    elif url in ("news:delete", "news:edit"):
        url = reverse(url, args=[comment.id])

    response = client.get(url)
    assert response.status_code == expected_status
    

@pytest.mark.django_db
@pytest.mark.parametrize(
    "name",
    ("news:delete", "news:edit")
)
def test_redirect_for_anonymous_client(client, comment, name):
    """
    Переадресация анонимного пользователя
    на страницу входа, если пользователь пытается
    перейти на страницу редактирования или удаления
    """
    login_url = reverse("users:login")
    url = reverse(name, args=(comment.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
