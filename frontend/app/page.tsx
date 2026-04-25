import { fetchAPI } from "../lib/api";
import type { DoctorProfile } from "../lib/types";

export default async function Home() {
  const doctor = (await fetchAPI("/profile")) as DoctorProfile | null;

  if (!doctor) {
    return (
      <main className="min-h-screen bg-neutral-0">
        <div className="container section flex items-center justify-center">
          <div className="card max-w-2xl">
            <h1>Профиль врача не найден</h1>
            <p className="mt-4 text-neutral-600">
              Добавь профиль врача в админке Django.
            </p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="bg-neutral-0">
      {/* ========== HERO SECTION ========== */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-50 via-neutral-0 to-neutral-0">
        {/* Decorative blurs */}
        <div className="absolute -left-32 -top-32 h-64 w-64 rounded-full bg-primary-100 opacity-40 blur-3xl" />
        <div className="absolute -bottom-32 -right-32 h-64 w-64 rounded-full bg-primary-50 opacity-30 blur-3xl" />

        <div className="relative container section">
          <div className="grid gap-12 md:grid-cols-[1.1fr_0.9fr] md:items-center">
            {/* Left: Text Content */}
            <div className="animate-fade-in-up">
              {/* Specialty Badge */}
              <div className="inline-flex items-center gap-2 rounded-full bg-primary-100 px-4 py-2 text-ui-label text-primary-600 font-semibold uppercase tracking-wider">
                <span className="w-2 h-2 bg-secondary-600 rounded-full" />
                Врач-инфекционист
              </div>

              {/* Doctor Name */}
              <h1 className="mt-6 text-neutral-900">
                {doctor.full_name}
              </h1>

              {/* Description */}
              <p className="mt-6 max-w-2xl text-base-large text-neutral-600">
                {doctor.description || "Описание пока не заполнено."}
              </p>

              {/* CTA Buttons */}
              <div className="mt-10 flex flex-col gap-4 sm:flex-row">
                <a
                  href="/booking"
                  className="btn-primary text-center sm:text-left"
                >
                  Записаться на консультацию
                </a>

                <a
                  href="/office"
                  className="btn-secondary text-center sm:text-left"
                >
                  Очный приём
                </a>
              </div>

              {/* Stats */}
              <div className="mt-12 grid gap-4 sm:grid-cols-3">
                {[
                  { label: "Стаж", value: `${doctor.experience_years ?? 0}+ лет` },
                  { label: "Формат", value: "Онлайн и очно" },
                  { label: "Статус", value: "Принимает" },
                ].map((stat, idx) => (
                  <div
                    key={idx}
                    className="card-interactive bg-gradient-card"
                  >
                    <p className="text-ui-label text-neutral-500 uppercase tracking-wider">
                      {stat.label}
                    </p>
                    <p className="mt-3 text-2xl font-bold text-neutral-900">
                      {stat.value}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Photo */}
            <div className="relative animate-fade-in" style={{ animationDelay: "0.2s" }}>
              {/* Photo Container */}
              <div className="card shadow-xl">
                {doctor.photo_url ? (
                  <img
                    src={doctor.photo_url}
                    alt={doctor.full_name}
                    className="h-[280px] w-full sm:h-[350px] md:h-[500px] rounded-lg object-cover"
                  />
                ) : (
                  <div className="flex h-[280px] w-full sm:h-[350px] md:h-[500px] items-center justify-center rounded-lg bg-neutral-200 text-neutral-500">
                    <span className="text-center">
                      Фото врача
                      <br />
                      не загружено
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========== SERVICES SECTION ========== */}
      <section className="bg-neutral-50 section-vertical-spacing">
        <div className="container">
          <h2 className="section-title">Как я помогаю</h2>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: "📋",
                title: "Онлайн-консультация",
                description:
                  "Быстрая запись через сайт. Выберите дату, время и оставьте данные.",
              },
              {
                icon: "🏥",
                title: "Очный приём",
                description:
                  "Личный приём в кабинете. Полная диагностика и лечение.",
              },
              {
                icon: "💊",
                title: "Рекомендации",
                description:
                  "Профессиональные советы и назначения для вашего здоровья.",
              },
            ].map((service, idx) => (
              <div
                key={idx}
                className="card-interactive border-t-4 border-primary-600"
                style={{ animationDelay: `${idx * 100}ms` }}
              >
                <div className="text-5xl">{service.icon}</div>
                <h3 className="mt-4 text-neutral-900">{service.title}</h3>
                <p className="mt-3 text-neutral-600">{service.description}</p>
                <a
                  href="/booking"
                  className="mt-6 inline-flex items-center gap-2 text-primary-600 font-medium hover:gap-3 transition-all"
                >
                  Узнать больше
                  <span>→</span>
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========== CTA SECTION ========== */}
      <section className="section-vertical-spacing">
        <div className="container text-center">
          <h2 className="text-h2-mobile md:text-h2-desktop text-neutral-900 mb-6">
            Готовы начать?
          </h2>
          <p className="text-base-large text-neutral-600 mb-8 max-w-2xl mx-auto">
            Запишитесь на консультацию уже сегодня и получите профессиональную помощь
          </p>
          <a href="/booking" className="btn-primary text-lg">
            Записаться сейчас
          </a>
        </div>
      </section>
    </main>
  );
}