from django.conf import settings
from django.urls import reverse

import pytest

# 1. Количество новостей на главной странице — не более 10.
# 2. Новости отсортированы от самой свежей к самой старой.
# Свежие новости в начале списка.
# 3. Комментарии на странице отдельной новости отсортированы
# в хронологическом порядке: старые в начале списка, новые — в конце.
# 4. Анонимному пользователю недоступна форма для отправки комментария
# на странице отдельной новости, а авторизованному доступна.


@pytest.mark.django_db
def test_news_count(client, list_news):
    url = reverse("news:home")
    response = client.get(url)
    object_list = response.context["object_list"]
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, list_news):
    url = reverse("news:home")
    response = client.get(url)
    object_list = response.context["object_list"]
    all_news = [news for news in object_list]
    sorted_news = sorted(all_news, key=lambda x: x.date, reverse=True)
    assert sorted_news == list_news


@pytest.mark.django_db
def test_comments_order(client, news, list_comments):
    url = reverse("news:detail", args=(news.id,))
    response = client.get(url)
    assert "news" in response.context
    news = response.context["news"]
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.parametrize(
    "parametrized_client, status",
    (
        (pytest.lazy_fixture("client"), False),
        (pytest.lazy_fixture("author_client"), True)
    ),
)
@pytest.mark.django_db
def test_anonymous_client_has_no_form(parametrized_client, status, comment):
    url = reverse("news:detail", args=(comment.id,))
    response = parametrized_client.get(url)
    assert ("form" in response.context) is status
