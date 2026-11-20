import type { MetadataRoute } from "next";

import { loadArticles, loadBlogCategories } from "../lib/siteContent";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://doctor-barkova.ru";

// Sitemap собирается на каждый запрос (статьи добавляются через админку),
// при сборке в CI бэкенд недоступен.
export const revalidate = 0;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // lastModified у статичных страниц не указываем: «всегда сегодня» поисковики
  // быстро учатся игнорировать, и сигнал теряется и для статей.
  const staticUrls: MetadataRoute.Sitemap = [
    { url: `${SITE_URL}/`, changeFrequency: "weekly", priority: 1 },
    { url: `${SITE_URL}/about`, changeFrequency: "monthly", priority: 0.8 },
    { url: `${SITE_URL}/booking`, changeFrequency: "daily", priority: 0.9 },
    { url: `${SITE_URL}/office`, changeFrequency: "monthly", priority: 0.7 },
    { url: `${SITE_URL}/contacts`, changeFrequency: "monthly", priority: 0.6 },
    { url: `${SITE_URL}/blog`, changeFrequency: "weekly", priority: 0.8 },
    { url: `${SITE_URL}/legal/offer`, changeFrequency: "yearly", priority: 0.2 },
    { url: `${SITE_URL}/legal/privacy`, changeFrequency: "yearly", priority: 0.2 },
    { url: `${SITE_URL}/legal/consent`, changeFrequency: "yearly", priority: 0.2 },
  ];

  // Динамически добавляем опубликованные статьи и активные кластеры.
  // Если API недоступно (билд при отключённом backend) — сбрасываемся на
  // статические URL.
  let articleUrls: MetadataRoute.Sitemap = [];
  let categoryUrls: MetadataRoute.Sitemap = [];
  try {
    const [articles, categories] = await Promise.all([
      loadArticles(),
      loadBlogCategories(),
    ]);
    articleUrls = articles.map((article) => ({
      url: `${SITE_URL}/blog/${article.slug}`,
      lastModified: article.published_at ? new Date(article.published_at) : undefined,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    }));
    categoryUrls = categories.map((category) => ({
      url: `${SITE_URL}/blog/category/${category.slug}`,
      changeFrequency: "weekly" as const,
      priority: 0.7,
    }));
  } catch {
    // Failure — proceed with static URLs only
  }

  return [...staticUrls, ...categoryUrls, ...articleUrls];
}
