import type { Metadata } from "next";
import { Sparkles } from "lucide-react";

import BookingForm from "../../components/booking/BookingForm";
import { JsonLd } from "../../components/common/JsonLd";
import { WhatsIncluded } from "../../components/common/WhatsIncluded";
import { buildBreadcrumbSchema } from "../../lib/seo";
import {
  loadConsultationFeatures,
  loadSiteBlocks,
  textOr,
} from "../../lib/siteContent";

export const metadata: Metadata = {
  title: "Онлайн-запись на разбор",
  description:
    "Запись на онлайн-разбор у врача-инфекциониста. Выберите дату и время — подтверждение в VK.",
  openGraph: {
    title: "Онлайн-запись · Кабинет врача-инфекциониста",
    description:
      "Выберите дату и время онлайн-разбора. Подтверждение в VK.",
  },
  alternates: { canonical: "/booking" },
};

const DEFAULT_BOOKING_INTRO =
  "Во время онлайн-разбора мы подробно рассматриваем тему заболевания: что это такое, какие особенности могут встречаться и на что важно обращать внимание.\n\n" +
  "Я объясняю информацию простым и понятным языком, чтобы у вас сформировалось спокойное и понятное понимание медицинской информации без сложных терминов.\n\n" +
  "Также рассказываю, какие обследования обычно используются при подобных состояниях и почему они могут быть информативны. После разбора вы получаете структурированную памятку со всей важной информацией.\n\n" +
  "Вы можете заранее подготовить любые вопросы — я подробно разбираю каждый и стараюсь помочь вам лучше ориентироваться в теме здоровья и обследований.\n\n" +
  "Онлайн-разборы носят информационно-просветительский характер и не заменяют очный приём врача.";

export default async function BookingPage() {
  const [blocks, features] = await Promise.all([
    loadSiteBlocks(),
    loadConsultationFeatures("online"),
  ]);
  const chip = textOr(blocks, "booking.section_chip", "Онлайн-разбор");
  const title = textOr(
    blocks,
    "booking.section_title",
    "Запись на онлайн-разбор"
  );
  const subtitle = textOr(
    blocks,
    "booking.section_subtitle",
    "Выберите удобную дату и время, затем оставьте свои данные для онлайн-разбора."
  );
  const featuresTitle = textOr(
    blocks,
    "booking.features_title",
    "Что входит в онлайн-разбор"
  );
  const featuresSubtitle = textOr(blocks, "booking.features_subtitle", "");
  const featuresIntro = textOr(
    blocks,
    "booking.features_intro",
    DEFAULT_BOOKING_INTRO
  );

  return (
    <>
      <JsonLd
        data={buildBreadcrumbSchema([
          { name: "Главная", href: "/" },
          { name: "Онлайн-разбор", href: "/booking" },
        ])}
      />

      <main id="main" className="relative min-h-screen overflow-hidden bg-gradient-to-br from-primary-50 via-neutral-0 to-neutral-0">
        {/* Decorative blurs */}
        <div className="pointer-events-none absolute -left-32 -top-32 h-72 w-72 rounded-full bg-primary-200 opacity-30 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-40 -right-32 h-80 w-80 rounded-full bg-secondary-100 opacity-40 blur-3xl" />

        <div className="relative container pt-20 pb-12 md:py-20">
          {/* H1 имеет scroll-mt чтобы при возврате к якорю (skip-link или
              ручной скролл к самому верху) заголовок не прятался за
              sticky-header'ом высотой ~72px на mobile. */}
          <div className="mb-10 max-w-3xl animate-fade-in-up scroll-mt-24">
            <span className="chip">
              <Sparkles className="h-3.5 w-3.5" strokeWidth={2.5} />
              {chip}
            </span>

            <h1 className="mt-5 text-neutral-900">{title}</h1>

            <p className="mt-5 text-base-large text-neutral-600 whitespace-pre-line">
              {subtitle}
            </p>
          </div>

          {/* Что входит — ВЫШЕ формы, чтобы пациент знал, на что записывается */}
          <WhatsIncluded
            title={featuresTitle}
            subtitle={featuresSubtitle || undefined}
            intro={featuresIntro}
            features={features}
          />

          <BookingForm />
        </div>
      </main>
    </>
  );
}
