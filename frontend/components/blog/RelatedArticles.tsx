import { ArticleCard } from "./ArticleCard";
import type { ArticleListItem } from "../../lib/types";

type Props = {
  articles: ArticleListItem[];
  currentSlug: string;
  limit?: number;
};

/**
 * Блок «См. также» в конце статьи. Показывает до `limit` других статей
 * блога, исключая текущую. Если кроме текущей других нет — секция
 * не рендерится, чтоб не было пустого заголовка на проде.
 */
export function RelatedArticles({ articles, currentSlug, limit = 3 }: Props) {
  const others = articles
    .filter((a) => a.slug !== currentSlug)
    .slice(0, limit);

  if (others.length === 0) return null;

  return (
    <section className="mt-16 pt-10 border-t border-neutral-200">
      <h2 className="text-h3-mobile sm:text-h3-desktop text-neutral-900">
        Полезно почитать
      </h2>
      <p className="mt-2 text-sm text-neutral-500">
        Другие статьи в блоге — простыми словами о&nbsp;медицине.
      </p>
      <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 auto-rows-fr">
        {others.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>
    </section>
  );
}
