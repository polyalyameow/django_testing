# 1. Главная страница доступна анонимному пользователю.
# 2. Страница отдельной новости доступна анонимному пользователю.
# 3. Страницы удаления и редактирования комментария
# доступны автору комментария.
# 4. При попытке перейти на страницу редактирования или удаления
# комментария анонимный пользователь перенаправляется на страницу авторизации.
# 5. Авторизованный пользователь не может зайти на страницы
# редактирования или удаления чужих комментариев (возвращается ошибка 404).
# 6. Страницы регистрации пользователей, входа в учётную запись
# и выхода из неё доступны анонимным пользователям.

from http import HTTPStatus
from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name",
    ("news:home", "users:login", "users:logout", "users:signup")
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_page(client, news):
    url = reverse("news:detail", args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "parametrized_client, expected_status",
    (
        (pytest.lazy_fixture("admin_client"), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture("author_client"), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    "name",
    ("news:edit", "news:delete"),
)
def test_availability_for_comment_edit_and_delete_for_author(
        parametrized_client, expected_status, name, comment
):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name",
    ("news:edit", "news:delete"),
)
def test_redirect_for_anonymous_client(client, name, comment):
    login_url = reverse("users:login")
    url = reverse(name, args=(comment.id,))
    expected_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)
