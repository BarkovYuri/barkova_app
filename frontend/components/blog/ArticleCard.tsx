import Image from "next/image";
import Link from "next/link";
import { ArrowRight, CalendarDays } from "lucide-react";

import type { ArticleListItem } from "../../lib/types";
import { absoluteMediaUrl } from "../../lib/url";

const FORMATTER = new Intl.DateTimeFormat("ru-RU", {
  day: "numeric",
  month: "long",
  year: "numeric",
});

function formatDate(iso: string | null): string | null {
  if (!iso) return null;
  try {
    return FORMATTER.format(new Date(iso));
  } catch {
    return null;
  }
}

export function ArticleCard({ article }: { article: ArticleListItem }) {
  const cover = absoluteMediaUrl(article.cover_url);
  const dateLabel = formatDate(article.published_at);

  return (
    <Link
      href={`/blog/${article.slug}`}
      className="group flex h-full flex-col overflow-hidden rounded-3xl border border-neutral-200 bg-neutral-0 transition-all hover:-translate-y-1 hover:border-primary-200 hover:shadow-card-hover"
    >
      {cover ? (
        <div className="relative aspect-[16/10] w-full overflow-hidden bg-neutral-100">
          <Image
            src={cover}
            alt={article.cover_alt || article.title}
            fill
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
            className="object-cover transition-transform duration-500 group-hover:scale-105"
          />
        </div>
      ) : (
        <div className="aspect-[16/10] w-full bg-gradient-to-br from-primary-100 via-primary-50 to-secondary-50" />
      )}

      <div className="flex flex-1 flex-col gap-3 p-6">
        {dateLabel ? (
          <p className="inline-flex items-center gap-1.5 text-xs text-neutral-500">
            <CalendarDays className="h-3.5 w-3.5" strokeWidth={2.2} />
            {dateLabel}
          </p>
        ) : null}
        <h3 className="text-lg font-bold text-neutral-900 leading-snug">
          {article.title}
        </h3>
        {article.excerpt ? (
          <p className="text-sm text-neutral-600 leading-relaxed line-clamp-3">
            {article.excerpt}
          </p>
        ) : null}
        <p className="mt-auto inline-flex items-center gap-1.5 text-sm font-semibold text-primary-700">
          Читать
          <ArrowRight
            className="h-4 w-4 transition-transform group-hover:translate-x-1"
            strokeWidth={2.5}
          />
        </p>
      </div>
    </Link>
  );
}
