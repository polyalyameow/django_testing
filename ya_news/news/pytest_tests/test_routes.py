from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse

from .conftest import LOGIN_URL, LOGOUT_URL, NEWS_HOME, SIGNUP_URL

# from .conftest import ADMIN, AUTHOR, CLIENT


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, expected_status',
    (
        # ('home_url', CLIENT, HTTPStatus.OK),
        # ('news_detail_url', CLIENT, HTTPStatus.OK),
        # (URL.login, CLIENT, HTTPStatus.OK),
        # (URL.logout, CLIENT, HTTPStatus.OK),
        # (URL.signup, CLIENT, HTTPStatus.OK),
        # ('comment_edit_url', AUTHOR, HTTPStatus.OK),
        # ('delete_comment_url', AUTHOR, HTTPStatus.OK),
        # ('comment_edit_url', ADMIN, HTTPStatus.NOT_FOUND),
        # ('delete_comment_url', ADMIN, HTTPStatus.NOT_FOUND),
        (NEWS_HOME, HTTPStatus.OK),
        (LOGIN_URL, HTTPStatus.OK),
        (LOGOUT_URL, HTTPStatus.OK),
        (SIGNUP_URL, HTTPStatus.OK),
        ("news:delete", HTTPStatus.FOUND),
        ("news:edit", HTTPStatus.FOUND),
        # ("news:edit", ADMIN, HTTPStatus.NOT_FOUND),
        # ("news:edit", ADMIN, HTTPStatus.NOT_FOUND),
    ),
)

def test_pages_availability(
    url, client, expected_status, pk_for_args
):
    """Страницы, доступные разным пользователям"""
    # client = request.getfixturevalue(client_fixture)
    # url_value = request.getfixturevalue(url)
    # response = client.get(url_value)
    # assert response.status_code == expected_status
    if url in ("news:edit", "news:delete"):
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
