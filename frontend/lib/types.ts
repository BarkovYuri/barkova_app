// Централизованные DTO-типы фронтенда.
// Единственный источник правды — дублирование из page-файлов устранено.

export type Slot = {
  id: number;
  date: string;
  start_time: string;
  end_time: string;
  is_booked: boolean;
  is_active: boolean;
  is_reserved?: boolean;
};

export type AvailableDateItem =
  | string
  | { date: string; free_slots?: number };

export type NormalizedDate = {
  date: string;
  free_slots?: number;
};

export type CalendarDay = {
  key: string;
  date: Date | null;
  iso: string | null;
  isCurrentMonth: boolean;
  isAvailable: boolean;
  freeSlots?: number;
};

export type DoctorProfile = {
  id: number;
  header_avatar_url?: string | null; 
  // Поля, которые используются в коде AboutPage:
  full_name: string;        // было name
  short_intro?: string;     // короткое описание для hero на главной
  description?: string;     // полное описание для /about
  photo_url?: string | null; // было photo
  experience_years: number;
  education?: string;        // добавьте это поле
  address?: string;          // было office_address
  prodoktorov_url?: string | null; // ссылка на ПроДокторов
  instagram_url?: string | null; // <-- Ошибка здесь
  vk_url?: string | null;
  dzen_url?: string | null;
  yandex_maps_embed_url?: string | null; 
  // Старые поля (если они приходят из API, оставьте их)
  title?: string;
  phone?: string;
  email?: string;
  specialties?: string[];
  prodoktorov_rating?: string | number | null;
  prodoktorov_reviews_count?: number | null;
};

export type ArticleListItem = {
  id: number;
  slug: string;
  title: string;
  excerpt: string;
  cover_url: string | null;
  cover_alt: string;
  published_at: string | null;
  views_count: number;
};

export type ArticleDetail = ArticleListItem & {
  body: string;
  updated_at: string;
  meta_title: string;
  meta_description: string;
  keywords: string;
};

export type BlogCategoryListItem = {
  id: number;
  slug: string;
  name: string;
  description: string;
  cover_url: string | null;
  cover_alt: string;
  articles_count: number;
};

export type BlogCategoryDetail = {
  id: number;
  slug: string;
  name: string;
  description: string;
  cover_url: string | null;
  cover_alt: string;
  meta_title: string;
  meta_description: string;
  keywords: string;
  articles: ArticleListItem[];
};

export type LegalDocument = {
  id: number;
  doc_type: "offer" | "privacy" | "consent";
  title: string;
  content: string;
  version: string;
  is_active: boolean;
  created_at: string;
};

export type CreatedAppointment = {
  id: number;
  slot: number;
  slot_date: string;
  slot_start_time: string;
  slot_end_time: string;
  name: string;
  phone: string;
  vk_link_token: string;
  status: string;
  created_at: string;
};

export type ContactMethod = "vk";

// ============================================================================
// Контент сайта — редактируется врачом через Django-админку
// ============================================================================

export type SiteBlock = {
  id: number;
  key: string;
  title: string;
  content: string;
  updated_at: string;
};

export type Service = {
  id: number;
  icon: string;
  title: string;
  description: string;
  cta_text: string;
  cta_link: string;
  order: number;
};

export type HowItWorksStep = {
  id: number;
  icon: string;
  title: string;
  description: string;
  order: number;
};

export type FaqItem = {
  id: number;
  question: string;
  answer: string;
  order: number;
};

export type ApproachItem = {
  id: number;
  icon: string;
  title: string;
  description: string;
  order: number;
};

export type TrustBadge = {
  id: number;
  icon: string;
  label: string;
  order: number;
};

export type TransportItem = {
  id: number;
  icon: string;
  title: string;
  description: string;
  order: number;
};

export type ConsultationFeature = {
  id: number;
  consultation_type: "online" | "office";
  icon: string;
  title: string;
  description: string;
  order: number;
};

export type ConditionItem = {
  id: number;
  text: string;
  order: number;
};

export type ConditionCategory = {
  id: number;
  icon: string;
  title: string;
  description: string;
  order: number;
  items: ConditionItem[];
};
