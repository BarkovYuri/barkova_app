import type { MetadataRoute } from "next";

import { loadArticles, loadBlogCategories } from "../lib/siteContent";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://doctor-barkova.ru";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const lastModified = new Date();

  const staticUrls: MetadataRoute.Sitemap = [
    { url: `${SITE_URL}/`, lastModified, changeFrequency: "weekly", priority: 1 },
    { url: `${SITE_URL}/about`, lastModified, changeFrequency: "monthly", priority: 0.8 },
    { url: `${SITE_URL}/booking`, lastModified, changeFrequency: "daily", priority: 0.9 },
    { url: `${SITE_URL}/office`, lastModified, changeFrequency: "monthly", priority: 0.7 },
    { url: `${SITE_URL}/contacts`, lastModified, changeFrequency: "monthly", priority: 0.6 },
    { url: `${SITE_URL}/blog`, lastModified, changeFrequency: "weekly", priority: 0.8 },
    { url: `${SITE_URL}/legal/offer`, lastModified, changeFrequency: "yearly", priority: 0.3 },
    { url: `${SITE_URL}/legal/privacy`, lastModified, changeFrequency: "yearly", priority: 0.3 },
    { url: `${SITE_URL}/legal/consent`, lastModified, changeFrequency: "yearly", priority: 0.3 },
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
      lastModified: article.published_at
        ? new Date(article.published_at)
        : lastModified,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    }));
    categoryUrls = categories.map((category) => ({
      url: `${SITE_URL}/blog/category/${category.slug}`,
      lastModified,
      changeFrequency: "weekly" as const,
      priority: 0.7,
    }));
  } catch {
    // Failure — proceed with static URLs only
  }

  return [...staticUrls, ...categoryUrls, ...articleUrls];
}
