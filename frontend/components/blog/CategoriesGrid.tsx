import { CategoryCard } from "./CategoryCard";
import type { BlogCategoryListItem } from "../../lib/types";

type Props = {
  categories: BlogCategoryListItem[];
  title?: string;
};

/**
 * Сетка кластеров над списком статей блога.
 *
 * - mobile (< 640px): 2 в ряд
 * - tablet (640–1024): 3 в ряд
 * - desktop (≥ 1024): 5 в ряд
 *
 * Если кластеров нет — секция не рендерится, чтобы не было сиротливого
 * заголовка над пустотой.
 */
export function CategoriesGrid({ categories, title }: Props) {
  if (categories.length === 0) return null;

  return (
    <section className="mb-10 md:mb-14">
      {title ? (
        <h2 className="mb-5 text-base sm:text-lg font-bold text-neutral-900">
          {title}
        </h2>
      ) : null}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-5 lg:gap-4 auto-rows-fr">
        {categories.map((category) => (
          <CategoryCard key={category.id} category={category} />
        ))}
      </div>
    </section>
  );
}
