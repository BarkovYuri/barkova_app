"""Тесты обновлений сайта: копии картинок, отзывы, документы, тексты."""

import importlib
from io import BytesIO

import pytest
from django.apps import apps as django_apps
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from apps.content.models import Article, Credential, FaqItem, Review, Service, SiteBlock, TransportItem
from apps.doctors.models import DoctorProfile

pytestmark = pytest.mark.django_db


def _jpeg(width=1200, height=800, name="cover.jpg"):
    buffer = BytesIO()
    Image.new("RGB", (width, height), (40, 120, 140)).save(buffer, "JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


@pytest.fixture
def media(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    return tmp_path


def test_article_list_returns_small_webp_cover(media):
    Article.objects.create(title="Статья", slug="statya", body="текст", is_published=True, cover=_jpeg())

    item = APIClient().get("/api/articles/").json()[0]

    assert item["cover_url"].endswith(".jpg")
    assert item["cover_thumb_url"].endswith("__w720.webp")
    thumb_path = media / item["cover_thumb_url"].removeprefix("/media/")
    with Image.open(thumb_path) as thumb:
        assert thumb.width == 720


def test_header_avatar_is_square_thumbnail(media):
    DoctorProfile.objects.create(full_name="Врач", photo=_jpeg(720, 1080, "photo.jpg"))

    url = APIClient().get("/api/profile/").json()["header_avatar_url"]

    assert url.endswith("__sq128.webp")
    with Image.open(media / url.removeprefix("/media/")) as avatar:
        assert avatar.size == (128, 128)


def test_reviews_and_credentials_endpoints(media):
    Review.objects.create(author_name="Анна", text="Спасибо", rating=5)
    Review.objects.create(author_name="Скрытый", text="-", is_active=False)
    Credential.objects.create(title="Диплом", year="2022", image=_jpeg(name="diploma.jpg"))

    reviews = APIClient().get("/api/reviews/").json()
    credentials = APIClient().get("/api/credentials/").json()

    assert [r["author_name"] for r in reviews] == ["Анна"]
    assert credentials[0]["thumb_url"].endswith("__w480.webp")


def test_schedule_info_contains_community_link(settings):
    settings.VK_GROUP_ID = "123"
    settings.VK_GROUP_DOMAIN = "doctor_club"
    assert APIClient().get("/api/schedule-info/").json()["community_url"] == "https://vk.me/doctor_club"


def test_wording_migration_updates_only_untouched_texts():
    migration = importlib.import_module("apps.content.migrations.0011_informational_wording")
    Service.objects.all().delete()
    TransportItem.objects.all().delete()
    Service.objects.create(title="Рекомендации", description="x", cta_link="/booking")
    office = Service.objects.create(title="Очный приём", description="x", cta_link="/booking", cta_text="Записаться")
    TransportItem.objects.create(title="На такси", description="Яндекс.Такси, Uber или Gett — удобно и быстро")
    faq = FaqItem.objects.create(question="Как?", answer="Детали врач уточнит в Telegram или VK после записи.")
    edited = FaqItem.objects.create(question="Свой", answer="Текст, который врач уже переписала.")
    SiteBlock.objects.update_or_create(key="contacts.social.title", defaults={"content": "Мессенджеры"})
    profile = DoctorProfile.objects.create(
        full_name="Врач", short_intro="Помогаю: разбираемся в причинах, объясняю простым языком, лечу без паники."
    )

    migration.forwards(django_apps, None)

    assert not Service.objects.get(title="Рекомендации").is_active
    office.refresh_from_db()
    assert (office.cta_link, office.cta_text) == ("/office", "Подробнее")
    assert "Uber" not in TransportItem.objects.get().description
    faq.refresh_from_db()
    assert "Telegram" not in faq.answer and "по телефону" in faq.answer
    edited.refresh_from_db()
    assert edited.answer == "Текст, который врач уже переписала."
    assert SiteBlock.objects.get(key="contacts.social.title").content == "Соцсети и почта"
    profile.refresh_from_db()
    assert "лечу" not in profile.short_intro
