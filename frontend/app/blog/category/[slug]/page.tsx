import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, ArrowRight, Sparkles } from "lucide-react";

import { ArticleCard } from "../../../../components/blog/ArticleCard";
import { JsonLd } from "../../../../components/common/JsonLd";
import { buildBreadcrumbSchema } from "../../../../lib/seo";
import { loadBlogCategoryBySlug } from "../../../../lib/siteContent";
import { absoluteMediaUrl } from "../../../../lib/url";

export const revalidate = 60;

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://doctor-barkova.ru";

type Params = Promise<{ slug: string }>;

export async function generateMetadata({
  params,
}: {
  params: Params;
}): Promise<Metadata> {
  const { slug } = await params;
  const category = await loadBlogCategoryBySlug(slug);
  if (!category) {
    return { title: "Кластер не найден" };
  }
  const title = category.meta_title || `${category.name} — статьи блога`;
  const description =
    category.meta_description ||
    category.description ||
    `Подборка статей блога по теме «${category.name}».`;
  const cover = absoluteMediaUrl(category.cover_url) || undefined;
  return {
    title,
    description,
    keywords: category.keywords
      ? category.keywords.split(",").map((k) => k.trim())
      : undefined,
    alternates: { canonical: `/blog/category/${category.slug}` },
    openGraph: {
      title,
      description,
      type: "website",
      images: cover ? [{ url: cover, alt: category.cover_alt || category.name }] : undefined,
    },
    twitter: {
      card: cover ? "summary_large_image" : "summary",
      title,
      description,
      images: cover ? [cover] : undefined,
    },
  };
}

export default async function CategoryPage({ params }: { params: Params }) {
  const { slug } = await params;
  const category = await loadBlogCategoryBySlug(slug);
  if (!category) {
    notFound();
  }

  const cover = absoluteMediaUrl(category.cover_url);

  // CollectionPage schema: даёт Google понимание, что это страница-сборник
  // с коллекцией статей внутри.
  const collectionLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: category.name,
    description: category.description || undefined,
    url: `${SITE_URL}/blog/category/${category.slug}`,
    image: cover || undefined,
    mainEntity: {
      "@type": "ItemList",
      itemListElement: category.articles.map((a, idx) => ({
        "@type": "ListItem",
        position: idx + 1,
        url: `${SITE_URL}/blog/${a.slug}`,
        name: a.title,
      })),
    },
  };

  return (
    <main id="main" className="bg-neutral-0">
      <JsonLd data={collectionLd} />
      <JsonLd
        data={buildBreadcrumbSchema([
          { name: "Главная", href: "/" },
          { name: "Блог", href: "/blog" },
          { name: category.name, href: `/blog/category/${category.slug}` },
        ])}
      />

      <section className="container py-12 md:py-20">
        <Link
          href="/blog"
          className="inline-flex items-center gap-1.5 text-sm text-neutral-500 hover:text-primary-700 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" strokeWidth={2.2} />
          Все статьи
        </Link>

        <div className="mt-6 grid gap-6 md:gap-10 md:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)] md:items-center mb-10 md:mb-14">
          <div>
            <p className="chip">
              <Sparkles className="h-3.5 w-3.5" strokeWidth={2.5} />
              Подборка статей
            </p>
            <h1 className="mt-5 text-neutral-900">{category.name}</h1>
            {category.description ? (
              <p className="mt-5 text-base sm:text-lg text-neutral-600 leading-relaxed whitespace-pre-line">
                {category.description}
              </p>
            ) : null}
            <p className="mt-5 text-sm text-neutral-500">
              {category.articles.length === 0
                ? "В этом кластере пока нет статей"
                : `${category.articles.length} ${pluralizeArticles(category.articles.length)} в подборке`}
            </p>
          </div>

          {cover ? (
            <div className="relative aspect-[16/10] w-full overflow-hidden rounded-3xl bg-neutral-100">
              <Image
                src={cover}
                alt={category.cover_alt || category.name}
                fill
                priority
                sizes="(max-width: 768px) 100vw, 480px"
                className="object-cover"
              />
            </div>
          ) : null}
        </div>

        {category.articles.length === 0 ? (
          <div className="rounded-3xl border border-dashed border-neutral-300 bg-neutral-50 px-6 py-16 text-center">
            <p className="text-base text-neutral-600">
              Здесь пока нет статей. Посмотрите{" "}
              <Link href="/blog" className="text-primary-700 underline-offset-4 hover:underline">
                все статьи блога
              </Link>{" "}
              или приходите на онлайн-разбор.
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
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 auto-rows-fr">
            {category.articles.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

function pluralizeArticles(n: number): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return "статья";
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return "статьи";
  return "статей";
}
