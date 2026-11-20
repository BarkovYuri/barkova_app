"""
Уменьшенные копии загруженных изображений.

Next.js-оптимизатор картинок на сайте выключен, поэтому раньше в карточку
40×40 отдавалось фото 720×1080, а в плитку 171 px — обложка 1200 px.
Здесь рядом с оригиналом создаётся WebP-копия нужной ширины, один раз,
и дальше переиспользуется. Оригинал не трогаем: он нужен статье и OG.
"""

from __future__ import annotations

import logging
import os
from io import BytesIO

from django.core.files.base import ContentFile

logger = logging.getLogger("apps.core.images")

AVATAR_SIZE = 128
CARD_WIDTH = 720
TILE_WIDTH = 480


def variant_name(name: str, width: int, square: bool = False) -> str:
    base, _ = os.path.splitext(name)
    return f"{base}__{'sq' if square else 'w'}{width}.webp"


def ensure_variant(field_file, width: int, square: bool = False) -> str | None:
    """Имя файла уменьшенной копии; создаёт её при первом обращении."""
    if not field_file or not field_file.name:
        return None
    storage = field_file.storage
    name = variant_name(field_file.name, width, square)
    if storage.exists(name):
        return name
    try:
        from PIL import Image, ImageOps

        with storage.open(field_file.name, "rb") as fh:
            image = Image.open(fh)
            image = ImageOps.exif_transpose(image)
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            if square:
                # Лицо на портретах обычно в верхней трети кадра.
                image = ImageOps.fit(image, (width, width), centering=(0.5, 0.3))
            elif image.width > width:
                image.thumbnail((width, width * 10))
            buffer = BytesIO()
            image.save(buffer, "WEBP", quality=82, method=6)
        storage.save(name, ContentFile(buffer.getvalue()))
        return name
    except Exception:
        logger.exception("Не удалось создать копию %s для %s", name, field_file.name)
        return None


def variant_url(field_file, width: int, square: bool = False) -> str | None:
    """URL уменьшенной копии, а если её не удалось сделать — оригинала."""
    if not field_file or not field_file.name:
        return None
    name = ensure_variant(field_file, width, square)
    return field_file.storage.url(name) if name else field_file.url
