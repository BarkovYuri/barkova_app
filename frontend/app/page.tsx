import type { Metadata } from "next";
import Image from "next/image";
import {
  ArrowRight,
  Award,
  CalendarCheck,
  ClipboardList,
  Hospital,
  MessageCircleHeart,
  Pill,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import { JsonLd } from "../components/common/JsonLd";
import { SectionDivider } from "../components/common/SectionDivider";
import { Faq } from "../components/home/Faq";
import { HowItWorks } from "../components/home/HowItWorks";
import { fetchAPI } from "../lib/api";
import type { DoctorProfile } from "../lib/types";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://doctor-barkova.ru";

export async function generateMetadata(): Promise<Metadata> {
  const doctor = (await fetchAPI("/profile")) as DoctorProfile | null;
  if (!doctor) return {};

  const title = `${doctor.full_name} — врач-инфекционист`;
  const description =
    doctor.description?.slice(0, 200) ||
    `Онлайн-консультации и очный приём. Стаж ${doctor.experience_years ?? 0}+ лет. Запись через сайт.`;
  const photo = doctor.photo_url
    ? doctor.photo_url.startsWith("http")
      ? doctor.photo_url
      : `${SITE_URL}${doctor.photo_url}`
    : undefined;

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      url: SITE_URL,
      type: "profile",
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
  const doctor = (await fetchAPI("/profile")) as DoctorProfile | null;

  if (!doctor) {
    return (
      <main className="min-h-screen bg-neutral-0">
        <div className="container section flex items-center justify-center">
          <div className="card max-w-2xl">
            <h1>Профиль врача не найден</h1>
            <p className="mt-4 text-neutral-600">
              Добавьте профиль врача в админке Django.
            </p>
          </div>
        </div>
      </main>
    );
  }

  const services = [
    {
      icon: ClipboardList,
      title: "Онлайн-консультация",
      description:
        "Быстрая запись через сайт. Выберите дату, время — и приходите на удобный вам формат.",
    },
    {
      icon: Hospital,
      title: "Очный приём",
      description:
        "Личный приём в кабинете. Полная диагностика и индивидуально подобранное лечение.",
    },
    {
      icon: Pill,
      title: "Рекомендации",
      description:
        "Профессиональные советы и назначения, основанные на актуальных клинических протоколах.",
    },
  ];

  const trustItems = [
    { icon: ShieldCheck, label: "Безопасность данных" },
    { icon: Award, label: "Подтверждённый стаж" },
    { icon: MessageCircleHeart, label: "Поддержка в Telegram / VK" },
    { icon: CalendarCheck, label: "Запись 24/7" },
  ];

  // Structured data — Physician schema для Google rich-cards
  const photoAbsolute = doctor.photo_url
    ? doctor.photo_url.startsWith("http")
      ? doctor.photo_url
      : `${SITE_URL}${doctor.photo_url}`
    : undefined;

  const physicianLd: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "Physician",
    name: doctor.full_name,
    medicalSpecialty: "InfectiousDiseases",
    description: doctor.description || undefined,
    image: photoAbsolute,
    url: SITE_URL,
    email: doctor.email || undefined,
    address: doctor.address
      ? {
          "@type": "PostalAddress",
          streetAddress: doctor.address,
          addressCountry: "RU",
        }
      : undefined,
    sameAs: [
      doctor.instagram_url,
      doctor.vk_url,
      doctor.dzen_url,
      doctor.prodoktorov_url,
    ].filter(Boolean),
  };

  // Удаляем undefined-поля
  Object.keys(physicianLd).forEach(
    (k) => physicianLd[k] === undefined && delete physicianLd[k]
  );

  return (
    <main className="bg-neutral-0">
      <JsonLd data={physicianLd} />

      {/* ========== HERO SECTION ========== */}
      <section className="relative overflow-hidden">
        {/* Decorative blurs */}
        <div className="pointer-events-none absolute -left-32 -top-32 h-72 w-72 rounded-full bg-primary-200/40 blur-3xl" />
        <div
          className="pointer-events-none absolute -bottom-40 -right-32 h-80 w-80 rounded-full bg-secondary-100/50 blur-3xl"
        />

        <div className="relative container section">
          <div className="grid gap-12 md:grid-cols-[1.1fr_0.9fr] md:items-center">
            {/* Left: Text Content */}
            <div className="animate-fade-in-up">
              {/* Specialty Badge */}
              <div className="chip">
                <Sparkles className="h-3.5 w-3.5" strokeWidth={2.5} />
                Врач-инфекционист
              </div>

              {/* Doctor Name */}
              <h1 className="mt-6 text-neutral-900">{doctor.full_name}</h1>

              {/* Description */}
              <p className="mt-6 max-w-2xl text-base sm:text-lg leading-relaxed text-neutral-600">
                {doctor.description ||
                  "Помогаю взрослым и детям с инфекционными заболеваниями: от диагностики до длительного сопровождения."}
              </p>

              {/* CTA Buttons */}
              <div className="mt-10 flex flex-col gap-4 sm:flex-row">
                <a href="/booking" className="btn-primary">
                  Записаться на консультацию
                  <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
                </a>

                <a href="/office" className="btn-secondary">
                  Очный приём
                </a>
              </div>

              {/* Stats */}
              <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4">
                {[
                  {
                    label: "Стаж",
                    value: `${doctor.experience_years ?? 0}+ лет`,
                  },
                  { label: "Формат", value: "Онлайн и очно" },
                  { label: "Статус", value: "Принимает" },
                ].map((stat, idx) => (
                  <div
                    key={idx}
                    className="rounded-2xl border border-neutral-200 bg-neutral-0 p-5 transition-all duration-300 hover:-translate-y-0.5 hover:border-primary-200 hover:shadow-md min-w-0"
                  >
                    <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
                      {stat.label}
                    </p>
                    <p className="mt-2 text-lg sm:text-xl font-bold text-neutral-900 font-heading leading-tight break-words">
                      {stat.value}
                    </p>
                  </div>
                ))}
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
              <div className="relative h-[360px] w-full sm:h-[480px] md:h-[600px] rounded-3xl overflow-hidden shadow-2xl">
                {doctor.photo_url ? (
                  <Image
                    src={doctor.photo_url}
                    alt={doctor.full_name}
                    fill
                    priority
                    sizes="(max-width: 768px) 100vw, (max-width: 1280px) 45vw, 540px"
                    className="object-cover"
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

                {/* Floating badge */}
                <div className="absolute bottom-4 left-4 z-10 inline-flex items-center gap-2 bg-neutral-0 border border-neutral-200 rounded-full px-4 py-2 shadow-lg">
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="absolute inline-flex h-full w-full rounded-full bg-secondary-400 opacity-75 animate-pulse-gentle" />
                    <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-secondary-500" />
                  </span>
                  <span className="text-xs font-semibold text-neutral-700 whitespace-nowrap">
                    Принимает записи
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========== TRUST STRIP ========== */}
      <section className="relative">
        <div className="container pb-16">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
            {trustItems.map(({ icon: Icon, label }, idx) => (
              <div
                key={idx}
                className="flex items-center gap-3 rounded-2xl border border-neutral-200 bg-neutral-50 px-4 py-3"
              >
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary-100 text-primary-700">
                  <Icon className="h-4 w-4" strokeWidth={2} />
                </span>
                <span className="text-xs md:text-sm font-medium text-neutral-700 leading-tight">
                  {label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ========== SERVICES SECTION ========== */}
      <section className="py-16 md:py-24">
        <div className="container">
          <div className="text-center mb-12 md:mb-16">
            <p className="chip mx-auto">Услуги</p>
            <h2 className="mt-5 text-neutral-900">Как я помогаю</h2>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {services.map((service, idx) => {
              const Icon = service.icon;
              return (
                <div
                  key={idx}
                  className="group flex flex-col rounded-2xl border border-neutral-200 bg-neutral-0 p-6 md:p-8 transition-all duration-300 hover:-translate-y-1 hover:border-primary-200 hover:shadow-card-hover"
                >
                  <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-100 text-primary-700 transition-colors duration-300 group-hover:bg-primary-600 group-hover:text-neutral-0">
                    <Icon className="h-7 w-7" strokeWidth={1.75} />
                  </div>
                  <h3 className="mt-6 text-neutral-900">{service.title}</h3>
                  <p className="mt-3 text-neutral-600 leading-relaxed flex-1">
                    {service.description}
                  </p>
                  <a
                    href="/booking"
                    className="mt-6 inline-flex items-center gap-2 text-primary-700 font-semibold hover:gap-3 transition-all"
                  >
                    Записаться
                    <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
                  </a>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ========== HOW IT WORKS ========== */}
      <HowItWorks />

      <SectionDivider />

      {/* ========== FAQ ========== */}
      <Faq />

      {/* ========== CTA SECTION ========== */}
      <section className="py-16 md:py-24">
        <div className="container">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-700 via-primary-600 to-primary-500 px-6 py-14 md:px-12 md:py-20 text-center shadow-xl">
            <div className="pointer-events-none absolute -top-24 -left-24 h-64 w-64 rounded-full bg-secondary-300/30 blur-3xl" />
            <div className="pointer-events-none absolute -bottom-24 -right-24 h-64 w-64 rounded-full bg-primary-300/40 blur-3xl" />

            <div className="relative">
              <h2 className="text-neutral-0">Готовы начать?</h2>
              <p className="mt-4 text-base sm:text-lg leading-relaxed text-primary-50 max-w-2xl mx-auto">
                Запишитесь на консультацию уже сегодня и получите
                профессиональную помощь
              </p>
              <a
                href="/booking"
                className="mt-8 inline-flex items-center gap-2 bg-neutral-0 text-primary-700 hover:bg-primary-50 font-semibold px-7 py-4 rounded-[14px] shadow-lg transition-all hover:-translate-y-0.5"
              >
                Записаться сейчас
                <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
              </a>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
