/**
 * Превращает относительный путь (`/media/doctor/abc.jpg`) в абсолютный URL.
 * Next.js Image не умеет оптимизировать относительные пути, если файлы
 * физически живут не на frontend-контейнере, а на backend через nginx.
 */
export function absoluteMediaUrl(
  url: string | null | undefined
): string | null {
  if (!url) return null;
  if (url.startsWith("http://") || url.startsWith("https://")) return url;

  const base =
    process.env.NEXT_PUBLIC_SITE_URL ||
    process.env.NEXT_PUBLIC_MEDIA_BASE_URL ||
    "https://doctor-barkova.ru";

  return `${base}${url.startsWith("/") ? url : `/${url}`}`;
}
