// Централизованные DTO-типы фронтенда.
// Единственный источник правды — дублирование из page-файлов устранено.

export type Slot = {
  id: number;
  date: string;
  start_time: string;
  end_time: string;
  is_booked: boolean;
  is_active: boolean;
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
  id?: number;
  full_name: string;
  title?: string;
  description?: string;
  bio?: string;
  education?: string;
  experience_years?: number;
  address?: string;
  email?: string;
  photo?: string | null;
  photo_url?: string | null;
  header_avatar_url?: string | null;
  prodoktorov_url?: string;
  yandex_maps_embed_url?: string;
  instagram_url?: string;
  vk_url?: string;
  dzen_url?: string;
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
  telegram_link_token: string;
  vk_link_token: string;
  status: string;
  created_at: string;
};

export type ContactMethod = "telegram" | "vk";
