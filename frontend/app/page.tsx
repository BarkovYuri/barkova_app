import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { ArrowRight, CalendarClock, ExternalLink, Sparkles, Star } from "lucide-react";

import { JsonLd } from "../components/common/JsonLd";
import { buildPhysicianSchema } from "../lib/seo";
import { SectionDivider } from "../components/common/SectionDivider";
import { Faq } from "../components/home/Faq";
import { HowItWorks } from "../components/home/HowItWorks";
import { Reviews } from "../components/home/Reviews";
import { fetchAPI } from "../lib/api";
import { resolveIcon } from "../lib/iconMap";
import {
  loadReviews,
  loadServices,
  loadSiteBlocks,
  loadTrustBadges,
  textOr,
} from "../lib/siteContent";
import type { DoctorProfile, Slot } from "../lib/types";
import { absoluteMediaUrl } from "../lib/url";

const MONTHS_GENITIVE = [
  "января", "февраля", "марта", "апреля", "мая", "июня",
  "июля", "августа", "сентября", "октября", "ноября", "декабря",
];

/** «25 ноября, 10:00» — время по поясу расписания, как в календаре записи. */
function formatSlot(slot: Slot): string {
  const [, month, day] = slot.date.split("-").map(Number);
  return `${day} ${MONTHS_GENITIVE[month - 1]}, ${slot.start_time.slice(0, 5)}`;
}

function pluralizeReviews(n: number): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return "отзыв";
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return "отзыва";
  return "отзывов";
}

// Страница рендерится на каждый запрос, а данные из API кэшируются на
// минуту в lib/api.ts. Так сборка в CI не требует работающего бэкенда.
export const revalidate = 0;

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://doctor-barkova.ru";

export async function generateMetadata(): Promise<Metadata> {
  const doctor = (await fetchAPI("/profile")) as DoctorProfile | null;
  if (!doctor) return {};

  const title = `${doctor.full_name} — врач-инфекционист в Томске`;
  const description =
    doctor.short_intro?.trim() ||
    doctor.description?.slice(0, 200) ||
    `Онлайн-разборы и очный приём. Стаж ${doctor.experience_years ?? 0}+ лет. Запись через сайт.`;
  const photo = absoluteMediaUrl(doctor.photo_url) || undefined;

  return {
    title,
    description,
    alternates: { canonical: "/" },
    openGraph: {
      title,
      description,
      url: SITE_URL,
      type: "profile",
      locale: "ru_RU",
      images: photo ? [{ url: photo, width: 800, height: 1000, alt: doctor.full_name }] : [],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: photo ? [photo] : [],
    },
  };
}

export default async function Home() {
  const [doctor, services, trustBadges, blocks, nearestSlot, reviews] = await Promise.all([
    fetchAPI("/profile") as Promise<DoctorProfile | null>,
    loadServices(),
    loadTrustBadges(),
    loadSiteBlocks(),
    // Ближайшее свободное время вместо статичного «Принимает»: если слотов
    // нет, сайт не обещает запись, которой нет.
    (fetchAPI("/nearest-slot").catch(() => null)) as Promise<Slot | null>,
    loadReviews(),
  ]);

  if (!doctor) {
    // Без профиля главная бессмысленна. Бросаем ошибку, а не отдаём
    // заглушку со статусом 200: иначе при сбое API поисковик может
    // проиндексировать «Профиль врача не найден» вместо главной.
    throw new Error("Doctor profile is not available");
  }

  // Тексты с fallback'ами
  const heroChip = textOr(blocks, "hero.specialty_chip", "Врач-инфекционист");
  // На главной hero — короткий. Приоритет:
  //   1. short_intro из профиля (отдельное поле специально для главной)
  //   2. первый абзац полного описания (для совместимости со старыми
  //      профилями, где заполнено только description)
  //   3. SiteBlock «hero.subtitle»
  //   4. дефолтный текст
  const firstParagraph = doctor.description?.split(/\n\s*\n/)[0]?.trim();
  const heroSubtitle =
    doctor.short_intro?.trim() ||
    firstParagraph ||
    textOr(
      blocks,
      "hero.subtitle",
      "Помогаю взрослым и детям с инфекционными заболеваниями: от диагностики до длительного сопровождения."
    );
  const servicesChip = textOr(blocks, "services.section_chip", "Услуги");
  const servicesTitle = textOr(
    blocks,
    "services.section_title",
    "Как я помогаю"
  );
  const ctaTitle = textOr(blocks, "cta.home.title", "Готовы начать?");
  const ctaText = textOr(
    blocks,
    "cta.home.text",
    "Запишитесь на онлайн-разбор и спокойно разберитесь в своей ситуации вместе с врачом"
  );
  const ctaButton = textOr(blocks, "cta.home.button", "Записаться сейчас");

  // Structured data — Physician (подтип MedicalBusiness в schema.org) для
  // карточки врача и local-pack по запросам «врач инфекционист Томск».
  const photoAbsolute = absoluteMediaUrl(doctor.photo_url) || undefined;
  const heroPhoto = absoluteMediaUrl(doctor.photo_url);

  const physicianLd = buildPhysicianSchema(doctor, photoAbsolute);

  return (
    <main id="main" className="bg-neutral-0">
      <JsonLd data={physicianLd} />

      {/* ========== HERO SECTION ========== */}
      <section className="relative overflow-hidden">
        {/* Decorative blurs */}
        <div className="pointer-events-none absolute -left-32 -top-32 h-72 w-72 rounded-full bg-primary-200/40 blur-3xl" />
        <div
          className="pointer-events-none absolute -bottom-40 -right-32 h-80 w-80 rounded-full bg-secondary-100/50 blur-3xl"
        />

        <div className="relative container section">
          <div className="grid gap-10 lg:gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
            {/* Left: Text Content */}
            <div className="animate-fade-in-up">
              {/* Specialty Badge */}
              <div className="chip">
                <Sparkles className="h-3.5 w-3.5" strokeWidth={2.5} />
                {heroChip}
              </div>

              {/* Doctor Name */}
              {/* В H1 — имя, специальность и город: главный запрос
                  страницы «врач инфекционист Томск». */}
              <h1 className="mt-6 text-neutral-900">
                {doctor.full_name}
                <span className="mt-3 block font-sans text-xl font-semibold text-primary-700 sm:text-2xl">
                  {textOr(blocks, "hero.h1_subtitle", "Врач-инфекционист в Томске")}
                </span>
              </h1>

              {/* Description */}
              <p className="mt-6 max-w-2xl text-base sm:text-lg leading-relaxed text-neutral-600 whitespace-pre-line">
                {heroSubtitle}
              </p>

              {/* Рейтинг ПроДокторов — рендерим только если в админке
                  заполнены поля. В schema.org его не размечаем: отзывы
                  собраны на стороннем сайте. */}
              {doctor.prodoktorov_rating && doctor.prodoktorov_reviews_count ? (
                <a
                  href={doctor.prodoktorov_url || "#"}
                  target={doctor.prodoktorov_url ? "_blank" : undefined}
                  rel={doctor.prodoktorov_url ? "noreferrer" : undefined}
                  className="mt-6 inline-flex items-center gap-3 rounded-full border border-amber-200 bg-amber-50 px-4 py-2 text-sm hover:border-amber-300 transition-colors group"
                >
                  <span className="flex items-center gap-1 text-amber-500">
                    <Star className="h-4 w-4 fill-amber-500" strokeWidth={0} />
                    <span className="font-bold text-neutral-900">
                      {doctor.prodoktorov_rating}
                    </span>
                  </span>
                  <span className="text-neutral-700">
                    <span className="font-semibold">
                      {doctor.prodoktorov_reviews_count}
                    </span>{" "}
                    {pluralizeReviews(Number(doctor.prodoktorov_reviews_count))}{" "}
                    на ПроДокторов
                  </span>
                  {doctor.prodoktorov_url ? (
                    <ExternalLink
                      className="h-3.5 w-3.5 text-neutral-400 group-hover:text-neutral-600"
                      strokeWidth={2}
                    />
                  ) : null}
                </a>
              ) : null}

              {/* CTA Buttons */}
              <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:gap-4">
                <Link href="/booking" className="btn-primary">
                  Записаться на онлайн-разбор
                  <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
                </Link>

                <Link href="/office" className="btn-secondary">
                  Очный приём
                </Link>
              </div>

              {/* Стаж и ближайшее свободное время — компактно, в одну строку */}
              <div className="mt-8 grid grid-cols-2 gap-3 sm:max-w-md">
                <div className="rounded-2xl border border-neutral-200 bg-neutral-0 px-4 py-3">
                  <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500">Стаж</p>
                  <p className="mt-1 text-lg font-bold text-neutral-900 font-heading">
                    {doctor.experience_years ?? 0}+ лет
                  </p>
                </div>
                <Link
                  href="/booking"
                  className="rounded-2xl border border-neutral-200 bg-neutral-0 px-4 py-3 transition-colors hover:border-primary-300"
                >
                  <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
                    {nearestSlot ? "Ближайшее окно" : "Запись"}
                  </p>
                  <p className="mt-1 text-lg font-bold text-neutral-900 font-heading leading-tight">
                    {nearestSlot ? formatSlot(nearestSlot) : "Скоро новые даты"}
                  </p>
                </Link>
              </div>
            </div>

            {/* Right: Photo */}
            <div
              className="relative animate-fade-in"
              style={{ animationDelay: "0.2s" }}
            >
              {/* Soft halo */}
              <div className="pointer-events-none absolute -inset-8 rounded-[48px] bg-gradient-to-br from-primary-200/40 to-secondary-100/30 blur-3xl" />

              {/* Photo */}
              <div className="relative h-[340px] w-full sm:h-[440px] lg:h-[600px] rounded-3xl overflow-hidden shadow-2xl">
                {heroPhoto ? (
                  <Image
                    src={heroPhoto}
                    alt={doctor.full_name}
                    fill
                    preload
                    sizes="(max-width: 1024px) 100vw, (max-width: 1280px) 45vw, 540px"
                    className="object-cover object-[50%_20%]"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center bg-neutral-200 text-neutral-500">
                    <span className="text-center">
                      Фото врача
                      <br />
                      не загружено
                    </span>
                  </div>
                )}

                {/* Плашка — только когда есть свободное время */}
                {nearestSlot ? (
                  <div className="absolute bottom-4 left-4 right-4 z-10 inline-flex w-fit max-w-[calc(100%-2rem)] items-center gap-2 rounded-full border border-neutral-200 bg-neutral-0 px-4 py-2 shadow-lg">
                    <CalendarClock className="h-4 w-4 shrink-0 text-secondary-600" strokeWidth={2.25} />
                    <span className="truncate text-xs font-semibold text-neutral-700">
                      Ближайшая запись: {formatSlot(nearestSlot)}
                    </span>
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========== TRUST STRIP ========== */}
      {trustBadges.length > 0 ? (
        <section className="relative">
          <div className="container pb-16">
            <div className="flex flex-wrap gap-3 md:gap-4">
              {trustBadges.map((badge) => {
                const Icon = resolveIcon(badge.icon);
                return (
                  <div
                    key={badge.id}
                    className="flex min-w-[150px] flex-1 items-center gap-3 rounded-2xl border border-neutral-200 bg-neutral-50 px-4 py-3 sm:flex-none"
                  >
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary-100 text-primary-700">
                      <Icon className="h-4 w-4" strokeWidth={2} />
                    </span>
                    <span className="text-xs md:text-sm font-medium text-neutral-700 leading-tight">
                      {badge.label}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      ) : null}

      <SectionDivider />

      {/* ========== SERVICES SECTION ========== */}
      {services.length > 0 ? (
        <section className="py-16 md:py-24">
          <div className="container">
            <div className="text-center mb-12 md:mb-16">
              <p className="chip mx-auto">{servicesChip}</p>
              <h2 className="mt-5 text-neutral-900">{servicesTitle}</h2>
            </div>

            <div className={`grid gap-6 sm:grid-cols-2 ${services.length >= 3 ? "lg:grid-cols-3" : ""}`}>
              {services.map((service) => {
                const Icon = resolveIcon(service.icon);
                return (
                  <div
                    key={service.id}
                    className="group flex flex-col rounded-2xl border border-neutral-200 bg-neutral-0 p-6 md:p-8 transition-all duration-300 hover:-translate-y-1 hover:border-primary-200 hover:shadow-card-hover"
                  >
                    <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-100 text-primary-700 transition-colors duration-300 group-hover:bg-primary-600 group-hover:text-white">
                      <Icon className="h-7 w-7" strokeWidth={1.75} />
                    </div>
                    <h3 className="mt-6 text-neutral-900">{service.title}</h3>
                    <p className="mt-3 text-neutral-600 leading-relaxed flex-1 whitespace-pre-line">
                      {service.description}
                    </p>
                    <Link
                      href={service.cta_link || "/booking"}
                      className="mt-6 inline-flex items-center gap-2 py-1 text-primary-700 font-semibold hover:gap-3 transition-all"
                    >
                      {service.cta_text || "Записаться"}
                      <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
                    </Link>
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      ) : null}

      <SectionDivider />

      {/* ========== HOW IT WORKS ========== */}
      <HowItWorks />

      <SectionDivider />

      {/* ========== ОТЗЫВЫ ========== */}
      <Reviews reviews={reviews} allReviewsUrl={doctor.prodoktorov_url} />

      {/* ========== FAQ ========== */}
      <Faq />

      {/* ========== CTA SECTION ========== */}
      <section className="py-16 md:py-24">
        <div className="container">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#155e75] via-primary-600 to-primary-500 px-6 py-14 md:px-12 md:py-20 text-center shadow-xl">
            <div className="pointer-events-none absolute -top-24 -left-24 h-64 w-64 rounded-full bg-secondary-300/30 blur-3xl" />
            <div className="pointer-events-none absolute -bottom-24 -right-24 h-64 w-64 rounded-full bg-primary-300/40 blur-3xl" />

            <div className="relative">
              <h2 className="text-white">{ctaTitle}</h2>
              <p className="mt-4 text-base sm:text-lg leading-relaxed text-white/85 max-w-2xl mx-auto whitespace-pre-line">
                {ctaText}
              </p>
              <Link
                href="/booking"
                className="mt-8 inline-flex items-center gap-2 bg-white text-[#155e75] hover:bg-[#f0fafb] font-semibold px-7 py-4 rounded-[14px] shadow-lg transition-all hover:-translate-y-0.5"
              >
                {ctaButton}
                <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
