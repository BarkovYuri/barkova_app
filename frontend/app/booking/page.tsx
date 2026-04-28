import type { Metadata } from "next";
import { Sparkles } from "lucide-react";
import Script from "next/script";

import BookingForm from "../../components/booking/BookingForm";
import { loadSiteBlocks, textOr } from "../../lib/siteContent";

export const metadata: Metadata = {
  title: "Онлайн-запись на консультацию",
  description:
    "Запись на онлайн-консультацию к врачу-инфекционисту. Выберите дату и время — подтверждение в Telegram или VK.",
  openGraph: {
    title: "Онлайн-запись · Кабинет врача-инфекциониста",
    description:
      "Выберите дату и время онлайн-консультации. Подтверждение в Telegram или VK.",
  },
  alternates: { canonical: "/booking" },
};

export default async function BookingPage() {
  const blocks = await loadSiteBlocks();
  const chip = textOr(blocks, "booking.section_chip", "Онлайн-консультация");
  const title = textOr(
    blocks,
    "booking.section_title",
    "Запись на онлайн-консультацию"
  );
  const subtitle = textOr(
    blocks,
    "booking.section_subtitle",
    "Выберите удобную дату и время, затем оставьте свои данные для онлайн-консультации."
  );

  return (
    <>
      {/* Telegram WebApp SDK — нужен когда страница открыта как Mini App.
       * Скрипт ничего не делает в обычном браузере, но даёт глобал
       * window.Telegram.WebApp когда мы внутри Telegram-клиента. */}
      <Script
        src="https://telegram.org/js/telegram-web-app.js"
        strategy="beforeInteractive"
      />

      <main className="relative min-h-screen overflow-hidden bg-gradient-to-br from-primary-50 via-neutral-0 to-neutral-0">
        {/* Decorative blurs */}
        <div className="pointer-events-none absolute -left-32 -top-32 h-72 w-72 rounded-full bg-primary-200 opacity-30 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-40 -right-32 h-80 w-80 rounded-full bg-secondary-100 opacity-40 blur-3xl" />

        <div className="relative container py-12 md:py-20">
          <div className="mb-10 max-w-3xl animate-fade-in-up">
            <span className="chip">
              <Sparkles className="h-3.5 w-3.5" strokeWidth={2.5} />
              {chip}
            </span>

            <h1 className="mt-5 text-neutral-900">{title}</h1>

            <p className="mt-5 text-base-large text-neutral-600 whitespace-pre-line">
              {subtitle}
            </p>
          </div>

          <BookingForm />
        </div>
      </main>
    </>
  );
}
