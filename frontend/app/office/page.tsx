import { fetchAPI } from "../../lib/api";
import type { DoctorProfile } from "../../lib/types";

export default async function OfficePage() {
  const doctor = (await fetchAPI("/profile")) as DoctorProfile | null;

  return (
    <main className="bg-neutral-0">
      <div className="container section-vertical-spacing">
        {/* Header */}
        <div className="max-w-4xl mx-auto mb-12 animate-fade-in-up">
          <p className="text-ui-label text-primary-600 font-semibold uppercase tracking-wider">
            Очный приём
          </p>
          <h1 className="mt-4 text-h1-mobile md:text-h1-desktop text-neutral-900">
            Запись на очную консультацию
          </h1>
          <p className="mt-6 text-base-large text-neutral-600 max-w-2xl">
            Запись на очный приём осуществляется через платформу ПроДокторов
          </p>
        </div>

        {/* Info Cards Grid */}
        <div className="grid gap-6 sm:grid-cols-2 mb-12 max-w-4xl mx-auto">
          {/* Address Card */}
          <div className="card-interactive border-l-4 border-primary-600">
            <div className="flex items-start gap-4">
              <div className="text-4xl">📍</div>
              <div className="flex-1">
                <p className="text-ui-label text-primary-600 font-semibold uppercase tracking-wider">
                  Адрес приёма
                </p>
                <p className="mt-3 font-bold text-neutral-900">
                  {doctor?.address || "Адрес не указан"}
                </p>
                <a
                  href={`https://maps.yandex.ru/search/${encodeURIComponent(doctor?.address || "")}/`}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-2 inline-flex items-center gap-2 text-primary-600 font-medium hover:gap-3 transition-all"
                >
                  Как добраться →
                </a>
              </div>
            </div>
          </div>

          {/* ПроДокторов Card */}
          {doctor?.prodoktorov_url ? (
            <div className="card-interactive border-l-4 border-secondary-600">
              <div className="flex items-start gap-4">
                <div className="text-4xl">🏥</div>
                <div className="flex-1">
                  <p className="text-ui-label text-secondary-600 font-semibold uppercase tracking-wider">
                    Запись
                  </p>
                  <p className="mt-3 font-bold text-neutral-900">
                    Платформа ПроДокторов
                  </p>
                  <a
                    href={doctor.prodoktorov_url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-2 inline-flex items-center gap-2 text-primary-600 font-medium hover:gap-3 transition-all"
                  >
                    Перейти →
                  </a>
                </div>
              </div>
            </div>
          ) : null}
        </div>

        {/* Map */}
        {doctor?.yandex_maps_embed_url ? (
          <div className="card shadow-xl overflow-hidden mb-12 max-w-4xl mx-auto w-full">
            <div className="px-6 py-4 border-b border-neutral-200">
              <h2 className="font-semibold text-neutral-900">Местоположение</h2>
              <p className="mt-1 text-sm text-neutral-600">
                На карте показана точка, где проходит очная консультация
              </p>
            </div>
            <div className="h-[200px] sm:h-[300px] md:h-[420px]">
              <iframe
                src={doctor.yandex_maps_embed_url}
                width="100%"
                height="100%"
                allowFullScreen
                loading="lazy"
                className="h-full w-full border-0"
                title="Карта очного приема"
              />
            </div>
          </div>
        ) : null}

        {/* How to get there section */}
        <div className="max-w-4xl mx-auto">
          <div className="card bg-gradient-card">
            <h2 className="text-h3-mobile md:text-h3-desktop text-neutral-900 mb-6">
              Как добраться?
            </h2>
            <div className="grid gap-6 sm:grid-cols-3">
              {[
                {
                  icon: "🚇",
                  title: "На метро",
                  description: "Ближайшая станция метро в 5 минутах пешком от кабинета",
                },
                {
                  icon: "🚗",
                  title: "На автомобиле",
                  description: "Рядом с кабинетом есть парковка для пациентов",
                },
                {
                  icon: "🚕",
                  title: "На такси",
                  description: "Используйте Яндекс.Такси, Uber или Gett для удобства",
                },
              ].map((item, idx) => (
                <div key={idx} className="text-center">
                  <div className="text-4xl mb-3">{item.icon}</div>
                  <h3 className="font-bold text-neutral-900 mb-2">{item.title}</h3>
                  <p className="text-sm text-neutral-600">{item.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-16 text-center max-w-4xl mx-auto">
          <p className="text-base-large text-neutral-600 mb-6">
            Готовы записаться на очный приём?
          </p>
          {doctor?.prodoktorov_url ? (
            <a href={doctor.prodoktorov_url} target="_blank" rel="noreferrer" className="btn-primary text-lg">
              Запишитесь через ПроДокторов
            </a>
          ) : (
            <a href="/booking" className="btn-primary text-lg">
              Записаться на онлайн-консультацию
            </a>
          )}
        </div>
      </div>
    </main>
  );
}