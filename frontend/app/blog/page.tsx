import type { Metadata } from "next";
import { ArrowRight, Sparkles } from "lucide-react";

import { ArticleCard } from "../../components/blog/ArticleCard";
import { CategoriesGrid } from "../../components/blog/CategoriesGrid";
import { JsonLd } from "../../components/common/JsonLd";
import { buildBreadcrumbSchema } from "../../lib/seo";
import { loadArticles, loadBlogCategories } from "../../lib/siteContent";

export const revalidate = 60;

export const metadata: Metadata = {
  title: "Блог — статьи врача-инфекциониста",
  description:
    "Понятным языком о болезнях, анализах и лечении: гепатиты, паразитозы, TORCH-инфекции, длительная температура и другие темы инфекционной медицины.",
  alternates: { canonical: "/blog" },
  openGraph: {
    title: "Блог — статьи врача-инфекциониста",
    description:
      "Понятным языком о болезнях, анализах и лечении инфекционных заболеваний.",
    type: "website",
  },
};

function pluralizeArticles(n: number): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return "статья";
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return "статьи";
  return "статей";
}

export default async function BlogIndexPage() {
  const [articles, categories] = await Promise.all([
    loadArticles(),
    loadBlogCategories(),
  ]);

  return (
    <main id="main" className="bg-neutral-0">
      <JsonLd
        data={buildBreadcrumbSchema([
          { name: "Главная", href: "/" },
          { name: "Блог", href: "/blog" },
        ])}
      />

      <section className="container py-12 md:py-20">
        <div className="max-w-3xl mb-10 md:mb-14">
          <p className="chip">
            <Sparkles className="h-3.5 w-3.5" strokeWidth={2.5} />
            Блог
          </p>
          <h1 className="mt-5 text-neutral-900">
            Простыми словами о&nbsp;сложных диагнозах
          </h1>
          <p className="mt-5 text-base sm:text-lg text-neutral-600 leading-relaxed">
            Здесь я разбираю инфекционные заболевания, анализы и подходы к
            лечению — без сложных терминов. Если в&nbsp;статье не нашёлся
            ответ на ваш вопрос — приходите на онлайн-разбор, разберёмся
            вместе.
          </p>
        </div>

        {/* Кластеры (категории) — компактная сетка над списком статей.
            5 в ряд на десктопе, 3 на планшете, 2 на мобильном. */}
        <CategoriesGrid categories={categories} title="Тематические подборки" />

        {articles.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-neutral-300 bg-neutral-50 px-6 py-16 text-center">
            <p className="text-base text-neutral-600">
              Скоро тут появятся статьи. А пока — записывайтесь на
              онлайн-разбор, разберём ваш вопрос лично.
            </p>
            <a
              href="/booking"
              className="mt-6 inline-flex items-center gap-2 btn-primary"
            >
              Записаться на онлайн-разбор
              <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
            </a>
          </div>
        ) : (
          <>
            {/* Разделитель между подборками и общим списком. Тонкая
                линия + заголовок + счётчик материалов. */}
            <div className="mb-6 mt-2 flex items-baseline justify-between gap-4 border-t border-neutral-200 pt-8">
              <h2 className="text-h3-mobile sm:text-h3-desktop text-neutral-900">
                Все статьи
              </h2>
              <p className="text-sm text-neutral-500 shrink-0">
                {articles.length} {pluralizeArticles(articles.length)} в блоге
              </p>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 auto-rows-fr">
              {articles.map((article) => (
                <ArticleCard key={article.id} article={article} />
              ))}
            </div>
          </>
        )}
      </section>
    </main>
  );
}
