from django.conf import settings

import pytest

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, home_url, list_news):
    """10 новостей на главной странице"""
    response = client.get(home_url)
    object_list = response.context["object_list"]
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, home_url, list_news):
    """Сортировка новостей - от нового к старому"""
    response = client.get(home_url)
    object_list = response.context["object_list"]
    all_news = [news for news in object_list]
    sorted_news = sorted(all_news, key=lambda x: x.date, reverse=True)
    assert sorted_news == list(object_list)


@pytest.mark.django_db
def test_comments_order(client, news_detail_url, list_comments):
    """Сортировка новостей - от старого к новому"""
    response = client.get(news_detail_url)
    assert "news" in response.context
    news = response.context["news"]
    all_comments = news.comment_set.order_by("created")
    assert all(c1.created <= c2.created for c1, c2 in zip(
        all_comments, all_comments[1:]))


@pytest.mark.parametrize(
    "parametrized_client, status",
    (
        (pytest.lazy_fixture("client"), False),
        (pytest.lazy_fixture("author_client"), True)
    ),
)
@pytest.mark.django_db
def test_anonymous_client_has_no_form(parametrized_client, status,
                                      news_detail_url):
    """
    Анонимному пользователю недостурна форма
    для отправки комментов
    """
    response = parametrized_client.get(news_detail_url)
    has_form = "form" in response.context and isinstance(
        response.context["form"], CommentForm)
    assert has_form == status
