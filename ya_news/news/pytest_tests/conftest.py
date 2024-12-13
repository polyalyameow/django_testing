from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.test import Client

from news.models import News, Comment

TEXT_COMMENT = "Текст комментария"
NEWS_HOME = reverse("news:home")
LOGIN_URL = reverse("users:login")
LOGOUT_URL = reverse("users:logout")
SIGNUP_URL = reverse("users:signup")


@pytest.fixture
def home_url():
    return reverse("news:home")


@pytest.fixture
def news_detail_url(news):
    return reverse("news:detail", args=(news.id,))


@pytest.fixture
def delete_comment_url(comment):
    return reverse("news:delete", args=(comment.id,))


@pytest.fixture
def comment_edit_url(comment):
    return reverse("news:edit", args=(comment.id,))


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username="Автор")


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username="Не автор")


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title="Заголовок",
        text="Текст новости",
        date=datetime.today(),
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        text=TEXT_COMMENT,
        news=news,
        author=author
    )
    return comment


@pytest.fixture
def list_news():
    today = datetime.today()
    return [
        News.objects.create(
            title=f"Новость {index}",
            text="Текст новости",
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]


@pytest.fixture
def list_comments(news, author):
    now, list_comment = timezone.now(), []
    for index in range(2):
        comment = Comment.objects.create(
            text="Текст {index}",
            news=news,
            author=author,
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        list_comment.append(comment)
