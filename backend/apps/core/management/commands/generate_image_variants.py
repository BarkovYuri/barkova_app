from django.core.management.base import BaseCommand

from apps.content.models import Article, BlogCategory
from apps.core.images import AVATAR_SIZE, CARD_WIDTH, TILE_WIDTH, ensure_variant
from apps.doctors.models import DoctorProfile


class Command(BaseCommand):
    help = "Создаёт уменьшенные WebP-копии обложек и аватара врача (повторный запуск ничего не делает)."

    def handle(self, *args, **options):
        made = 0
        for article in Article.objects.exclude(cover=""):
            made += bool(ensure_variant(article.cover, CARD_WIDTH))
        for category in BlogCategory.objects.exclude(cover=""):
            made += bool(ensure_variant(category.cover, TILE_WIDTH))
        for profile in DoctorProfile.objects.all():
            source = profile.header_avatar or profile.photo
            if source:
                made += bool(ensure_variant(source, AVATAR_SIZE, square=True))
        self.stdout.write(f"Копий изображений готово: {made}")
