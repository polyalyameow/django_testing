from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse

from .conftest import LOGIN_URL, LOGOUT_URL, NEWS_HOME, SIGNUP_URL


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, expected_status',
    (
        (NEWS_HOME, HTTPStatus.OK),
        (LOGIN_URL, HTTPStatus.OK),
        (LOGOUT_URL, HTTPStatus.OK),
        (SIGNUP_URL, HTTPStatus.OK),
        ("news:delete", HTTPStatus.FOUND),
        ("news:edit", HTTPStatus.FOUND),
        ("news:detail", HTTPStatus.OK),
    ),
)
def test_pages_availability(
    url, client, expected_status, pk_for_args
):
    """Страницы, доступные разным пользователям"""
    if url in ("news:edit", "news:delete", "news:detail"):
        url = reverse(url, args=pk_for_args)
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
