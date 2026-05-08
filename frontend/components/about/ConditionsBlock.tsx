import { Check } from "lucide-react";

import { resolveIcon } from "../../lib/iconMap";
import type { ConditionCategory } from "../../lib/types";

type Props = {
  title?: string;
  subtitle?: string;
  categories: ConditionCategory[];
};

/**
 * Секция «С чем можно обратиться» — группы заболеваний/состояний с
 * пунктами внутри. Используется на /about. Полезна для SEO (длинные
 * хвосты запросов вида «врач инфекционист бруцеллёз томск»).
 *
 * Если categories пуст — секция не рендерится.
 */
export function ConditionsBlock({
  title = "С чем можно обратиться",
  subtitle,
  categories,
}: Props) {
  if (categories.length === 0) return null;

  return (
    <section className="bg-neutral-50 py-16 md:py-24">
      <div className="container">
        <div className="max-w-3xl">
          <span className="chip">Сфера работы</span>
          <h2 className="mt-5 text-h2-mobile sm:text-h2-desktop text-neutral-900">
            {title}
          </h2>
          {subtitle ? (
            <p className="mt-4 text-base sm:text-lg text-neutral-600 leading-relaxed">
              {subtitle}
            </p>
          ) : null}
        </div>

        <div className="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {categories.map((category) => {
            const Icon = resolveIcon(category.icon);
            return (
              <article
                key={category.id}
                className="flex flex-col rounded-3xl border border-neutral-200 bg-neutral-0 p-6 sm:p-7 transition-all hover:-translate-y-1 hover:border-primary-200 hover:shadow-card-hover"
              >
                <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-100 text-primary-700">
                  <Icon className="h-6 w-6" strokeWidth={2} />
                </span>
                <h3 className="mt-5 text-lg font-bold text-neutral-900">
                  {category.title}
                </h3>
                {category.description ? (
                  <p className="mt-2 text-sm text-neutral-600 leading-relaxed">
                    {category.description}
                  </p>
                ) : null}
                <ul className="mt-5 space-y-2.5">
                  {category.items.map((item) => (
                    <li
                      key={item.id}
                      className="flex gap-2.5 text-sm text-neutral-700 leading-relaxed"
                    >
                      <Check
                        className="mt-0.5 h-4 w-4 shrink-0 text-primary-600"
                        strokeWidth={2.5}
                      />
                      <span>{item.text}</span>
                    </li>
                  ))}
                </ul>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
