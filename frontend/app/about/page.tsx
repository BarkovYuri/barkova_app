import { fetchAPI } from "../../lib/api";
import type { DoctorProfile } from "../../lib/types";

export default async function AboutPage() {
  const doctor = (await fetchAPI("/profile")) as DoctorProfile | null;

  if (!doctor) {
    return (
      <main className="min-h-screen bg-neutral-0">
        <div className="container section">
          <div className="card max-w-2xl">
            <h1>О враче</h1>
            <p className="mt-4 text-neutral-600">Профиль врача пока не заполнен.</p>
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
          <div className="grid gap-12 md:grid-cols-[380px_1fr] md:items-center">
            {/* Photo */}
            <div className="order-2 md:order-1 animate-fade-in">
              <div className="card shadow-xl">
                {doctor.photo_url ? (
                  <img
                    src={doctor.photo_url}
                    alt={doctor.full_name}
                    className="h-[280px] w-full sm:h-[350px] md:h-[500px] rounded-lg object-cover"
                  />
                ) : (
                  <div className="flex h-[280px] w-full sm:h-[350px] md:h-[500px] items-center justify-center rounded-lg bg-neutral-200 text-neutral-500">
                    Фото не загружено
                  </div>
                )}
              </div>
            </div>

            {/* Content */}
            <div className="order-1 md:order-2 animate-fade-in-up">
              {/* Badge */}
              <div className="inline-flex items-center gap-2 rounded-full bg-primary-100 px-4 py-2 text-ui-label text-primary-600 font-semibold uppercase tracking-wider">
                <span className="w-2 h-2 bg-secondary-600 rounded-full" />
                О враче
              </div>

              {/* Name */}
              <h1 className="mt-6 text-neutral-900">
                {doctor.full_name}
              </h1>

              {/* Description */}
              <p className="mt-6 max-w-3xl text-base-large text-neutral-600">
                {doctor.description || "Описание пока не заполнено."}
              </p>

              {/* CTA Buttons */}
              <div className="mt-10 flex flex-col gap-4 sm:flex-row">
                <a href="/booking" className="btn-primary">
                  Записаться на консультацию
                </a>

                {doctor.prodoktorov_url ? (
                  <a
                    href={doctor.prodoktorov_url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn-secondary"
                  >
                    Очный прием (ПроДокторов)
                  </a>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========== STATS SECTION ========== */}
      <section className="section-vertical-spacing">
        <div className="container">
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {/* Experience */}
            <div className="card-interactive border-l-4 border-primary-600">
              <p className="text-ui-label text-primary-600 font-semibold uppercase tracking-wider">
                📚 Стаж
              </p>
              <p className="mt-4 text-4xl font-bold text-neutral-900">
                {doctor.experience_years ?? 0}+
              </p>
              <p className="mt-2 text-neutral-600">
                лет практического опыта
              </p>
            </div>

            {/* Education */}
            <div className="card-interactive border-l-4 border-secondary-600">
              <p className="text-ui-label text-secondary-600 font-semibold uppercase tracking-wider">
                🎓 Образование
              </p>
              <p className="mt-4 font-semibold text-neutral-900 line-clamp-3">
                {doctor.education || "Информация пока не добавлена"}
              </p>
            </div>

            {/* Office */}
            <div className="card-interactive border-l-4 border-accent-600">
              <p className="text-ui-label text-accent-600 font-semibold uppercase tracking-wider">
                🏥 Очный приём
              </p>
              <p className="mt-4 font-semibold text-neutral-900 line-clamp-3">
                {doctor.address || "Адрес не указан"}
              </p>
              <a
                href="/office"
                className="mt-4 inline-flex items-center gap-2 text-primary-600 font-medium hover:gap-3 transition-all"
              >
                Подробнее
                <span>→</span>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ========== APPROACH SECTION ========== */}
      <section className="section-vertical-spacing bg-neutral-50">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <p className="text-ui-label text-primary-600 font-semibold uppercase tracking-wider">
              Подход к работе
            </p>

            <h2 className="mt-4 text-h2-mobile md:text-h2-desktop text-neutral-900">
              Спокойно, понятно и по делу
            </h2>

            <div className="mt-12 grid gap-8 sm:grid-cols-3">
              {[
                {
                  icon: "📋",
                  title: "Разбор жалоб",
                  description:
                    "Детальный анализ симптомов, анализов и уже проведённых обследований",
                },
                {
                  icon: "📊",
                  title: "Структурированный план",
                  description:
                    "Пациент получает ясный план: что делать, что наблюдать, какие обследования нужны",
                },
                {
                  icon: "✅",
                  title: "Удобный формат",
                  description:
                    "Онлайн-консультация через сайт или очный прием через ПроДокторов",
                },
              ].map((item, idx) => (
                <div
                  key={idx}
                  className="card-interactive bg-gradient-card"
                  style={{ animationDelay: `${idx * 100}ms` }}
                >
                  <div className="text-5xl">{item.icon}</div>
                  <h3 className="mt-4 text-neutral-900">{item.title}</h3>
                  <p className="mt-3 text-neutral-600">{item.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ========== CTA SECTION ========== */}
      <section className="section-vertical-spacing">
        <div className="container text-center">
          <h2 className="text-h2-mobile md:text-h2-desktop text-neutral-900 mb-6">
            Готовы получить помощь?
          </h2>
          <p className="text-base-large text-neutral-600 mb-8 max-w-2xl mx-auto">
            Запишитесь на консультацию и начните путь к выздоровлению
          </p>
          <a href="/booking" className="btn-primary text-lg">
            Записаться сейчас
          </a>
        </div>
      </section>
    </main>
  );
}