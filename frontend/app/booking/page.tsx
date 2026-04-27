import type { Metadata } from "next";
import { Sparkles } from "lucide-react";
import BookingForm from "../../components/booking/BookingForm";

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

export default function BookingPage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-gradient-to-br from-primary-50 via-neutral-0 to-neutral-0">
      {/* Decorative blurs */}
      <div className="pointer-events-none absolute -left-32 -top-32 h-72 w-72 rounded-full bg-primary-200 opacity-30 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-40 -right-32 h-80 w-80 rounded-full bg-secondary-100 opacity-40 blur-3xl" />

      <div className="relative container py-12 md:py-20">
        <div className="mb-10 max-w-3xl animate-fade-in-up">
          <span className="chip">
            <Sparkles className="h-3.5 w-3.5" strokeWidth={2.5} />
            Онлайн-консультация
          </span>

          <h1 className="mt-5 text-neutral-900">
            Запись на онлайн-консультацию
          </h1>

          <p className="mt-5 text-base-large text-neutral-600">
            Выберите удобную дату и время, затем оставьте свои данные для
            онлайн-консультации.
          </p>
        </div>

        <BookingForm />
      </div>
    </main>
  );
}
