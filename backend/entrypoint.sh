#!/bin/sh
set -e

python manage.py migrate
python manage.py collectstatic --noinput
# Уменьшенные копии картинок для карточек и шапки. Сбой не должен мешать старту.
python manage.py generate_image_variants || true

# Несколько воркеров: один синхронный воркер обслуживал весь SSR сайта и
# запись пациентов, и любой медленный запрос блокировал остальные.
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout "${GUNICORN_TIMEOUT:-60}" \
    --access-logfile -