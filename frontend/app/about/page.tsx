import type { Metadata } from "next";
import Image from "next/image";
import {
  ArrowRight,
  ExternalLink,
  GraduationCap,
  MapPin,
  Sparkles,
  TrendingUp,
} from "lucide-react";

import { SectionDivider } from "../../components/common/SectionDivider";
import { fetchAPI } from "../../lib/api";
import { resolveIcon } from "../../lib/iconMap";
import {
  loadApproachItems,
  loadSiteBlocks,
  textOr,
} from "../../lib/siteContent";
import type { DoctorProfile } from "../../lib/types";
import { absoluteMediaUrl } from "../../lib/url";

export async function generateMetadata(): Promise<Metadata> {
  const doctor = (await fetchAPI("/profile")) as DoctorProfile | null;
  const title = doctor ? `О враче · ${doctor.full_name}` : "О враче";
  const description = doctor?.description?.slice(0, 200) ||
    "Образование, опыт и подход к работе врача-инфекциониста.";
  return {
    title,
    description,
    openGraph: { title, description },
  };
}

export default async function AboutPage() {
  const [doctor, approach, blocks] = await Promise.all([
    fetchAPI("/profile") as Promise<DoctorProfile | null>,
    loadApproachItems(),
    loadSiteBlocks(),
  ]);

  if (!doctor) {
    return (
      <main className="min-h-screen bg-neutral-0">
        <div className="container section">
          <div className="card max-w-2xl">
            <h1>О враче</h1>
            <p className="mt-4 text-neutral-600">
              Профиль врача пока не заполнен.
            </p>
          </div>
        </div>
      </main>
    );
  }

  const heroPhoto = absoluteMediaUrl(doctor.photo_url);

  const approachChip = textOr(blocks, "approach.section_chip", "Подход к работе");
  const approachTitle = textOr(
    blocks,
    "approach.section_title",
    "Спокойно, понятно и по делу"
  );
  const ctaTitle = textOr(blocks, "cta.about.title", "Готовы получить помощь?");
  const ctaText = textOr(
    blocks,
    "cta.about.text",
    "Запишитесь на консультацию и начните путь к выздоровлению"
  );
  const ctaButton = textOr(
    blocks,
    "cta.home.button",
    "Записаться сейчас"
  );

  return (
    <main className="bg-neutral-0">
      {/* ========== HERO SECTION ========== */}
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute -left-32 -top-32 h-72 w-72 rounded-full bg-primary-200/40 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-40 -right-32 h-80 w-80 rounded-full bg-secondary-100/50 blur-3xl" />

        <div className="relative container section">
          <div className="grid gap-12 md:grid-cols-[400px_1fr] md:items-center">
            {/* Photo */}
            <div className="order-2 md:order-1 animate-fade-in">
              <div className="relative">
                <div className="pointer-events-none absolute -inset-8 rounded-[48px] bg-gradient-to-br from-primary-200/40 to-secondary-100/30 blur-3xl" />
                <div className="relative h-[360px] w-full sm:h-[480px] md:h-[600px] rounded-3xl overflow-hidden shadow-2xl">
                  {heroPhoto ? (
                    <Image
                      src={heroPhoto}
                      alt={doctor.full_name}
                      fill
                      priority
                      sizes="(max-width: 768px) 100vw, 400px"
                      className="object-cover"
                    />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center bg-neutral-200 text-neutral-500">
                      Фото не загружено
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="order-1 md:order-2 animate-fade-in-up">
              <div className="chip">
                <Sparkles className="h-3.5 w-3.5" strokeWidth={2.5} />
                О враче
              </div>

              <h1 className="mt-6 text-neutral-900">{doctor.full_name}</h1>

              <p className="mt-6 max-w-3xl text-base sm:text-lg leading-relaxed text-neutral-600">
                {doctor.description || "Описание пока не заполнено."}
              </p>

              <div className="mt-10 flex flex-col gap-4 sm:flex-row">
                <a href="/booking" className="btn-primary">
                  Записаться на консультацию
                  <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
                </a>

                {doctor.prodoktorov_url ? (
                  <a
                    href={doctor.prodoktorov_url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn-secondary"
                  >
                    Очный приём (ПроДокторов)
                    <ExternalLink className="h-4 w-4" strokeWidth={2.5} />
                  </a>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ========== STATS SECTION ========== */}
      <section className="py-16 md:py-24">
        <div className="container">
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {/* Experience */}
            <div className="flex flex-col rounded-2xl border border-neutral-200 bg-neutral-0 p-6 md:p-8 transition-all duration-300 hover:-translate-y-1 hover:border-primary-200 hover:shadow-card-hover">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-100 text-primary-700">
                <TrendingUp className="h-6 w-6" strokeWidth={2} />
              </span>
              <p className="mt-5 text-xs font-semibold uppercase tracking-wider text-neutral-500">
                Стаж
              </p>
              <p className="mt-3 text-4xl font-bold font-heading text-neutral-900">
                {doctor.experience_years ?? 0}+
              </p>
              <p className="mt-2 text-neutral-600">лет практического опыта</p>
            </div>

            {/* Education */}
            <div className="flex flex-col rounded-2xl border border-neutral-200 bg-neutral-0 p-6 md:p-8 transition-all duration-300 hover:-translate-y-1 hover:border-primary-200 hover:shadow-card-hover">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-secondary-100 text-secondary-700">
                <GraduationCap className="h-6 w-6" strokeWidth={2} />
              </span>
              <p className="mt-5 text-xs font-semibold uppercase tracking-wider text-neutral-500">
                Образование
              </p>
              <p className="mt-3 font-semibold text-neutral-900 leading-relaxed whitespace-pre-line line-clamp-4">
                {doctor.education || "Информация пока не добавлена"}
              </p>
            </div>

            {/* Office */}
            <div className="flex flex-col rounded-2xl border border-neutral-200 bg-neutral-0 p-6 md:p-8 transition-all duration-300 hover:-translate-y-1 hover:border-primary-200 hover:shadow-card-hover">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-accent-100 text-accent-600">
                <MapPin className="h-6 w-6" strokeWidth={2} />
              </span>
              <p className="mt-5 text-xs font-semibold uppercase tracking-wider text-neutral-500">
                Очный приём
              </p>
              <p className="mt-3 font-semibold text-neutral-900 leading-relaxed line-clamp-3">
                {doctor.address || "Адрес не указан"}
              </p>
              <a
                href="/office"
                className="mt-4 inline-flex items-center gap-2 text-primary-700 font-semibold hover:gap-3 transition-all"
              >
                Подробнее
                <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
              </a>
            </div>
          </div>
        </div>
      </section>

      <SectionDivider />

      {/* ========== APPROACH SECTION ========== */}
      {approach.length > 0 ? (
        <section className="py-16 md:py-24">
          <div className="container">
            <div className="max-w-5xl mx-auto">
              <div className="text-center">
                <p className="chip mx-auto">{approachChip}</p>
                <h2 className="mt-5 text-neutral-900">{approachTitle}</h2>
              </div>

              <div className="mt-12 md:mt-16 grid gap-6 grid-cols-1 sm:grid-cols-3">
                {approach.map((item) => {
                  const Icon = resolveIcon(item.icon);
                  return (
                    <div
                      key={item.id}
                      className="group flex flex-col rounded-2xl border border-neutral-200 bg-neutral-50 p-6 md:p-8 transition-all duration-300 hover:-translate-y-1 hover:border-primary-200 hover:bg-neutral-0 hover:shadow-card-hover"
                    >
                      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-100 text-primary-700 transition-colors duration-300 group-hover:bg-primary-600 group-hover:text-neutral-0">
                        <Icon className="h-7 w-7" strokeWidth={1.75} />
                      </div>
                      <h3 className="mt-6 text-neutral-900">{item.title}</h3>
                      <p className="mt-3 text-neutral-600 leading-relaxed whitespace-pre-line">
                        {item.description}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </section>
      ) : null}

      {/* ========== CTA SECTION ========== */}
      <section className="py-16 md:py-24">
        <div className="container">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary-700 via-primary-600 to-primary-500 px-6 py-14 md:px-12 md:py-20 text-center shadow-xl">
            <div className="pointer-events-none absolute -top-24 -left-24 h-64 w-64 rounded-full bg-secondary-300/30 blur-3xl" />
            <div className="pointer-events-none absolute -bottom-24 -right-24 h-64 w-64 rounded-full bg-primary-300/40 blur-3xl" />

            <div className="relative">
              <h2 className="text-neutral-0">{ctaTitle}</h2>
              <p className="mt-4 text-base sm:text-lg leading-relaxed text-primary-50 max-w-2xl mx-auto whitespace-pre-line">
                {ctaText}
              </p>
              <a
                href="/booking"
                className="mt-8 inline-flex items-center gap-2 bg-neutral-0 text-primary-700 hover:bg-primary-50 font-semibold px-7 py-4 rounded-[14px] shadow-lg transition-all hover:-translate-y-0.5"
              >
                {ctaButton}
                <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
              </a>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
