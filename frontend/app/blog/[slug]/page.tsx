import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, ArrowRight, CalendarDays } from "lucide-react";

import { ArticleBody } from "../../../components/blog/ArticleBody";
import { ArticleViewCounter } from "../../../components/blog/ArticleViewCounter";
import { RelatedArticles } from "../../../components/blog/RelatedArticles";
import { JsonLd } from "../../../components/common/JsonLd";
import { buildBreadcrumbSchema } from "../../../lib/seo";
import { loadArticleBySlug, loadArticles } from "../../../lib/siteContent";
import { absoluteMediaUrl } from "../../../lib/url";

export const revalidate = 60;

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://doctor-barkova.ru";

const FORMATTER = new Intl.DateTimeFormat("ru-RU", {
  day: "numeric",
  month: "long",
  year: "numeric",
});

type Params = Promise<{ slug: string }>;

export async function generateMetadata({
  params,
}: {
  params: Params;
}): Promise<Metadata> {
  const { slug } = await params;
  const article = await loadArticleBySlug(slug);
  if (!article) {
    return { title: "Статья не найдена" };
  }
  const title = article.meta_title || article.title;
  const description =
    article.meta_description ||
    article.excerpt ||
    "Статья врача-инфекциониста.";
  const cover = absoluteMediaUrl(article.cover_url) || undefined;
  const canonical = `/blog/${article.slug}`;
  return {
    title,
    description,
    keywords: article.keywords ? article.keywords.split(",").map((k) => k.trim()) : undefined,
    alternates: { canonical },
    openGraph: {
      title,
      description,
      type: "article",
      publishedTime: article.published_at || undefined,
      modifiedTime: article.updated_at,
      images: cover ? [{ url: cover, alt: article.cover_alt || article.title }] : undefined,
    },
    twitter: {
      card: cover ? "summary_large_image" : "summary",
      title,
      description,
      images: cover ? [cover] : undefined,
    },
  };
}

export default async function ArticlePage({ params }: { params: Params }) {
  const { slug } = await params;
  const [article, allArticles] = await Promise.all([
    loadArticleBySlug(slug),
    loadArticles(),
  ]);
  if (!article) {
    notFound();
  }

  const cover = absoluteMediaUrl(article.cover_url);
  const dateLabel = article.published_at
    ? FORMATTER.format(new Date(article.published_at))
    : null;

  // Article schema для rich-card в Google.
  const articleLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: article.title,
    description: article.meta_description || article.excerpt || undefined,
    image: cover || undefined,
    datePublished: article.published_at || undefined,
    dateModified: article.updated_at,
    author: { "@type": "Person", name: "Баркова Елена Игоревна" },
    publisher: {
      "@type": "Organization",
      name: "Кабинет врача-инфекциониста",
      url: SITE_URL,
    },
    mainEntityOfPage: { "@type": "WebPage", "@id": `${SITE_URL}/blog/${article.slug}` },
  };
  Object.keys(articleLd).forEach((k) => {
    if ((articleLd as Record<string, unknown>)[k] === undefined) {
      delete (articleLd as Record<string, unknown>)[k];
    }
  });

  return (
    <main id="main" className="bg-neutral-0">
      <JsonLd data={articleLd} />
      <JsonLd
        data={buildBreadcrumbSchema([
          { name: "Главная", href: "/" },
          { name: "Блог", href: "/blog" },
          { name: article.title, href: `/blog/${article.slug}` },
        ])}
      />

      <article className="container max-w-3xl py-12 md:py-20">
        <Link
          href="/blog"
          className="inline-flex items-center gap-1.5 text-sm text-neutral-500 hover:text-primary-700 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" strokeWidth={2.2} />
          Все статьи
        </Link>

        <header className="mt-6 mb-8">
          <h1 className="text-neutral-900">{article.title}</h1>
          <div className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2">
            {dateLabel ? (
              <p className="inline-flex items-center gap-1.5 text-sm text-neutral-500">
                <CalendarDays className="h-3.5 w-3.5" strokeWidth={2.2} />
                {dateLabel}
              </p>
            ) : null}
            <ArticleViewCounter
              slug={article.slug}
              initialCount={article.views_count ?? 0}
            />
          </div>
          {article.excerpt ? (
            <p className="mt-5 text-base sm:text-lg text-neutral-600 leading-relaxed">
              {article.excerpt}
            </p>
          ) : null}
        </header>

        {cover ? (
          <div className="relative mb-10 aspect-[16/9] w-full overflow-hidden rounded-3xl bg-neutral-100">
            <Image
              src={cover}
              alt={article.cover_alt || article.title}
              fill
              priority
              sizes="(max-width: 768px) 100vw, 768px"
              className="object-cover"
            />
          </div>
        ) : null}

        <ArticleBody markdown={article.body} />

        {/* Глазик с числом просмотров после тела — для тех, кто читает
            до конца. Тот же компонент уже стоит в шапке, но на длинной
            статье полезен и здесь. */}
        <div className="mt-10 flex justify-end">
          <ArticleViewCounter
            slug={article.slug}
            initialCount={article.views_count ?? 0}
          />
        </div>

        {/* CTA в конце статьи — главная цель блога. Идёт СРАЗУ после
            тела, чтобы дочитавший пациент видел «Записаться» первым,
            а не после соблазна уйти читать другую статью. */}
        <div className="mt-16 rounded-3xl border border-primary-200 bg-gradient-to-br from-primary-50 via-neutral-0 to-secondary-50 p-6 sm:p-10 text-center">
          <h2 className="text-h3-mobile sm:text-h3-desktop text-neutral-900">
            Остались вопросы?
          </h2>
          <p className="mt-3 text-base sm:text-lg text-neutral-600 max-w-xl mx-auto">
            Запишитесь на онлайн-разбор — разберём вашу ситуацию подробно
            и&nbsp;на понятном языке.
          </p>
          <a
            href="/booking"
            className="mt-6 inline-flex items-center gap-2 btn-primary"
          >
            Записаться
            <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
          </a>
        </div>

        {/* Похожие статьи — для тех, кто не готов записываться прямо
            сейчас. Внутренние ссылки усиливают SEO. */}
        <RelatedArticles articles={allArticles} currentSlug={article.slug} />
      </article>
    </main>
  );
}
