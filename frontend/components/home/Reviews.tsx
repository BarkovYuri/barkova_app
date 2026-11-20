import { ExternalLink, Quote, Star } from "lucide-react";

import type { Review } from "../../lib/types";

const DATE = new Intl.DateTimeFormat("ru-RU", { month: "long", year: "numeric" });

type Props = {
  reviews: Review[];
  allReviewsUrl?: string | null;
};

/** Отзывы пациентов. Секция не выводится, пока в админке нет отзывов. */
export function Reviews({ reviews, allReviewsUrl }: Props) {
  if (reviews.length === 0) return null;
  return (
    <section className="py-16 md:py-24">
      <div className="container">
        <div className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="chip">Отзывы</p>
            <h2 className="mt-5 text-neutral-900">Что говорят пациенты</h2>
          </div>
          {allReviewsUrl ? (
            <a
              href={allReviewsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 py-1 font-semibold text-primary-700 hover:text-primary-800"
            >
              Все отзывы на ПроДокторов
              <ExternalLink className="h-4 w-4" strokeWidth={2.25} />
            </a>
          ) : null}
        </div>

        <div className="-mx-4 flex snap-x snap-mandatory gap-4 overflow-x-auto px-4 pb-4 sm:mx-0 sm:grid sm:grid-cols-2 sm:overflow-visible sm:px-0 lg:grid-cols-3">
          {reviews.map((review) => (
            <figure
              key={review.id}
              className="flex w-[85%] shrink-0 snap-start flex-col rounded-2xl border border-neutral-200 bg-neutral-0 p-6 sm:w-auto"
            >
              <div className="flex items-center justify-between">
                <Quote className="h-6 w-6 text-primary-300" strokeWidth={2} />
                {review.rating ? (
                  <span className="flex gap-0.5" aria-label={`Оценка ${review.rating} из 5`}>
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star
                        key={i}
                        className={`h-4 w-4 ${i < (review.rating ?? 0) ? "fill-amber-400 text-amber-400" : "text-neutral-300"}`}
                        strokeWidth={1.5}
                      />
                    ))}
                  </span>
                ) : null}
              </div>
              <blockquote className="mt-4 flex-1 text-neutral-700 leading-relaxed whitespace-pre-line">
                {review.text}
              </blockquote>
              <figcaption className="mt-5 text-sm">
                <span className="font-semibold text-neutral-900">{review.author_name}</span>
                <span className="text-neutral-500">
                  {review.date ? ` · ${DATE.format(new Date(review.date))}` : ""}
                  {review.source ? ` · ${review.source}` : ""}
                </span>
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}
