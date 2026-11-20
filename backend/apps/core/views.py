from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


@never_cache
@require_GET
def healthz(_request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as exc:
        return JsonResponse(
            {"status": "error", "component": "db", "detail": str(exc)},
            status=503,
        )
    return JsonResponse({"status": "ok"})


@never_cache
@require_GET
def livez(_request):
    return JsonResponse({"status": "ok"})


def protected_media(request, path: str):
    """
    Выдача файлов пациентов только сотрудникам.

    Файлы лежат в MEDIA_ROOT, но nginx не отдаёт их публично. В проде
    Django проверяет права и передаёт выдачу nginx через X-Accel-Redirect
    на internal-location, в DEBUG отдаёт файл сам.
    """
    import mimetypes
    import posixpath

    from django.conf import settings
    from django.http import FileResponse, Http404, HttpResponse
    from django.shortcuts import redirect

    user = getattr(request, "user", None)
    if not (user and user.is_authenticated and user.is_staff):
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")

    normalized = posixpath.normpath(path).lstrip("/")
    if normalized.startswith("..") or "/../" in f"/{normalized}/":
        raise Http404
    full_path = settings.MEDIA_ROOT / normalized
    if not full_path.is_file():
        raise Http404

    content_type = mimetypes.guess_type(str(full_path))[0] or "application/octet-stream"
    if settings.DEBUG:
        response = FileResponse(open(full_path, "rb"), content_type=content_type)  # noqa: SIM115 — FileResponse сам закрывает файл
    else:
        response = HttpResponse(content_type=content_type)
        response["X-Accel-Redirect"] = f"/_protected_media/{normalized}"
    response["Cache-Control"] = "private, no-store"
    response["X-Robots-Tag"] = "noindex"
    return response
