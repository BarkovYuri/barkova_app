import Image from "next/image";
import Link from "next/link";

import type { BlogCategoryListItem } from "../../lib/types";
import { absoluteMediaUrl } from "../../lib/url";

function pluralizeArticles(n: number): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return "статья";
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return "статьи";
  return "статей";
}

/**
 * Компактная карточка кластера блога.
 *
 * Размеры подобраны так, чтобы 5 штук поместились в ряд на десктопе
 * и 2 штуки — на мобильном экране (см. CategoriesGrid).
 *
 * Если у кластера нет обложки — показывается фирменный градиент.
 */
export function CategoryCard({ category }: { category: BlogCategoryListItem }) {
  const cover = absoluteMediaUrl(category.cover_url);

  return (
    <Link
      href={`/blog/category/${category.slug}`}
      className="group flex flex-col h-full overflow-hidden rounded-2xl border border-neutral-200 bg-neutral-0 transition-all hover:-translate-y-1 hover:border-primary-300 hover:shadow-card-hover"
    >
      <div className="relative aspect-[16/10] w-full overflow-hidden bg-gradient-to-br from-primary-100 via-primary-50 to-secondary-50">
        {cover ? (
          <Image
            src={cover}
            alt={category.cover_alt || category.name}
            fill
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 20vw"
            className="object-cover transition-transform duration-500 group-hover:scale-105"
          />
        ) : null}
      </div>

      <div className="flex flex-col gap-1 p-3 sm:p-4">
        <p className="text-sm font-bold text-neutral-900 leading-tight line-clamp-2">
          {category.name}
        </p>
        <p className="text-xs text-neutral-500">
          {category.articles_count}{" "}
          {pluralizeArticles(category.articles_count)}
        </p>
      </div>
    </Link>
  );
}
