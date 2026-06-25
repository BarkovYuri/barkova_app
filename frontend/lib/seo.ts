/**
 * Хелперы для structured data (schema.org JSON-LD).
 *
 * Каждый builder возвращает plain-object с уже выпиленными undefined,
 * готовый для передачи в <JsonLd data={...}/>.
 */

import type { DoctorProfile, FaqItem } from "./types";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://doctor-barkova.ru";

// Координаты по умолчанию — Томск, Советская 86 (геокод).
// Можно переопределить через env, если адрес изменится.
const DEFAULT_LATITUDE = process.env.NEXT_PUBLIC_GEO_LATITUDE || "56.4694";
const DEFAULT_LONGITUDE = process.env.NEXT_PUBLIC_GEO_LONGITUDE || "84.9518";
const DEFAULT_LOCALITY = process.env.NEXT_PUBLIC_GEO_LOCALITY || "Томск";
const DEFAULT_POSTAL_CODE = process.env.NEXT_PUBLIC_GEO_POSTAL_CODE || "634034";
const DEFAULT_REGION = process.env.NEXT_PUBLIC_GEO_REGION || "Томская область";

function clean<T extends Record<string, unknown>>(obj: T): T {
  Object.keys(obj).forEach((k) => {
    const v = obj[k];
    if (v === undefined || v === null || v === "" ||
        (Array.isArray(v) && v.length === 0)) {
      delete obj[k];
    }
  });
  return obj;
}

function buildPostalAddress(doctor: DoctorProfile | null) {
  if (!doctor?.address) return undefined;
  return clean({
    "@type": "PostalAddress",
    streetAddress: doctor.address,
    addressLocality: DEFAULT_LOCALITY,
    addressRegion: DEFAULT_REGION,
    postalCode: DEFAULT_POSTAL_CODE,
    addressCountry: "RU",
  });
}

function buildGeo() {
  if (!DEFAULT_LATITUDE || !DEFAULT_LONGITUDE) return undefined;
  return {
    "@type": "GeoCoordinates",
    latitude: DEFAULT_LATITUDE,
    longitude: DEFAULT_LONGITUDE,
  };
}

function buildAggregateRating(doctor: DoctorProfile): Record<string, unknown> | undefined {
  const rating = doctor.prodoktorov_rating;
  const count = doctor.prodoktorov_reviews_count;
  if (rating == null || count == null || Number(count) <= 0) {
    return undefined;
  }
  return {
    "@type": "AggregateRating",
    ratingValue: String(rating),
    reviewCount: count,
    bestRating: 5,
    worstRating: 1,
  };
}

export function buildPhysicianSchema(
  doctor: DoctorProfile,
  photoAbsolute: string | undefined,
): Record<string, unknown> {
  return clean({
    "@context": "https://schema.org",
    "@type": "Physician",
    name: doctor.full_name,
    medicalSpecialty: ["InfectiousDisease"],
    description: doctor.description || doctor.short_intro || undefined,
    image: photoAbsolute,
    url: SITE_URL,
    email: doctor.email || undefined,
    telephone: doctor.phone || undefined,
    address: buildPostalAddress(doctor),
    geo: buildGeo(),
    areaServed: { "@type": "City", name: DEFAULT_LOCALITY },
    aggregateRating: buildAggregateRating(doctor),
    availableService: [
      {
        "@type": "MedicalTherapy",
        name: "Онлайн-разбор",
        description:
          "Информационно-просветительский разбор инфекционных и связанных с ними состояний по видеосвязи.",
      },
      {
        "@type": "MedicalProcedure",
        name: "Очный приём",
        description: "Консультация инфекциониста в кабинете в Томске.",
      },
    ],
    sameAs: [
      doctor.instagram_url,
      doctor.vk_url,
      doctor.dzen_url,
      doctor.prodoktorov_url,
    ].filter(Boolean),
  });
}

export function buildMedicalBusinessSchema(
  doctor: DoctorProfile,
  photoAbsolute: string | undefined,
): Record<string, unknown> {
  return clean({
    "@context": "https://schema.org",
    "@type": "MedicalBusiness",
    name: `Кабинет врача-инфекциониста · ${doctor.full_name}`,
    image: photoAbsolute,
    url: SITE_URL,
    telephone: doctor.phone || undefined,
    email: doctor.email || undefined,
    address: buildPostalAddress(doctor),
    geo: buildGeo(),
    priceRange: "₽₽",
    areaServed: { "@type": "City", name: DEFAULT_LOCALITY },
    aggregateRating: buildAggregateRating(doctor),
    sameAs: [
      doctor.instagram_url,
      doctor.vk_url,
      doctor.dzen_url,
      doctor.prodoktorov_url,
    ].filter(Boolean),
  });
}

export function buildFaqPageSchema(
  items: FaqItem[],
): Record<string, unknown> | null {
  if (!items.length) return null;
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  };
}

type ArticleSchemaInput = {
  title: string;
  description?: string;
  slug: string;
  body?: string;
  coverUrl?: string;
  publishedAt?: string;
  updatedAt?: string;
  categoryName?: string;
};

export function buildArticleSchema(
  article: ArticleSchemaInput,
): Record<string, unknown> {
  // wordCount — приблизительная оценка по словам в Markdown-теле.
  // Точность не критична, Google использует это как сигнал «лонгрид vs
  // короткая заметка».
  const wordCount = article.body
    ? article.body.trim().split(/\s+/).filter(Boolean).length
    : undefined;

  return clean({
    "@context": "https://schema.org",
    "@type": "Article",
    headline: article.title,
    description: article.description,
    image: article.coverUrl,
    datePublished: article.publishedAt,
    dateModified: article.updatedAt,
    wordCount,
    articleSection: article.categoryName,
    author: {
      "@type": "Person",
      name: "Баркова Елена Игоревна",
      url: `${SITE_URL}/about`,
    },
    publisher: {
      "@type": "Organization",
      name: "Кабинет врача-инфекциониста",
      url: SITE_URL,
    },
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": `${SITE_URL}/blog/${article.slug}`,
    },
  });
}

export function buildBreadcrumbSchema(
  items: { name: string; href: string }[],
): Record<string, unknown> {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, idx) => ({
      "@type": "ListItem",
      position: idx + 1,
      name: item.name,
      item: item.href.startsWith("http") ? item.href : `${SITE_URL}${item.href}`,
    })),
  };
}
