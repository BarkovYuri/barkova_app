import type { Metadata } from "next";
import {
  ArrowRight,
  Building2,
  Car,
  CarTaxiFront,
  ExternalLink,
  MapPin,
  Train,
} from "lucide-react";
import { fetchAPI } from "../../lib/api";
import type { DoctorProfile } from "../../lib/types";

export const metadata: Metadata = {
  title: "Очный приём",
  description:
    "Очный приём у врача-инфекциониста. Адрес кабинета, как добраться, запись через ПроДокторов.",
  openGraph: {
    title: "Очный приём · Кабинет врача-инфекциониста",
    description:
      "Запись на очную консультацию через платформу ПроДокторов. Адрес и схема проезда.",
  },
  alternates: { canonical: "/office" },
};

export default async function OfficePage() {
  const doctor = (await fetchAPI("/profile")) as DoctorProfile | null;

  const transports = [
    {
      icon: Train,
      title: "На метро",
      description: "Ближайшая станция метро в 5 минутах пешком от кабинета",
    },
    {
      icon: Car,
      title: "На автомобиле",
      description: "Рядом с кабинетом есть парковка для пациентов",
    },
    {
      icon: CarTaxiFront,
      title: "На такси",
      description: "Яндекс.Такси, Uber или Gett — удобно и быстро",
    },
  ];

  return (
    <main className="bg-neutral-0">
      <div className="container section-vertical-spacing">
        {/* Header */}
        <div className="max-w-4xl mx-auto mb-12 animate-fade-in-up">
          <p className="chip">Очный приём</p>
          <h1 className="mt-5 text-neutral-900">
            Запись на очную консультацию
          </h1>
          <p className="mt-6 text-base-large text-neutral-600 max-w-2xl">
            Запись на очный приём осуществляется через платформу ПроДокторов
          </p>
        </div>

        {/* Info Cards Grid */}
        <div className="grid gap-6 sm:grid-cols-2 mb-12 max-w-4xl mx-auto">
          {/* Address Card */}
          <div className="card-interactive">
            <div className="flex items-start gap-4">
              <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-primary-100 text-primary-700">
                <MapPin className="h-6 w-6" strokeWidth={2} />
              </span>
              <div className="flex-1">
                <p className="text-ui-label text-neutral-500 uppercase">
                  Адрес приёма
                </p>
                <p className="mt-3 font-bold text-neutral-900">
                  {doctor?.address || "Адрес не указан"}
                </p>
                <a
                  href={`https://maps.yandex.ru/search/${encodeURIComponent(
                    doctor?.address || ""
                  )}/`}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-3 inline-flex items-center gap-2 text-primary-700 font-semibold hover:gap-3 transition-all"
                >
                  Как добраться
                  <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
                </a>
              </div>
            </div>
          </div>

          {/* ПроДокторов Card */}
          {doctor?.prodoktorov_url ? (
            <div className="card-interactive">
              <div className="flex items-start gap-4">
                <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-secondary-100 text-secondary-700">
                  <Building2 className="h-6 w-6" strokeWidth={2} />
                </span>
                <div className="flex-1">
                  <p className="text-ui-label text-neutral-500 uppercase">
                    Запись
                  </p>
                  <p className="mt-3 font-bold text-neutral-900">
                    Платформа ПроДокторов
                  </p>
                  <a
                    href={doctor.prodoktorov_url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-3 inline-flex items-center gap-2 text-primary-700 font-semibold hover:gap-3 transition-all"
                  >
                    Перейти
                    <ExternalLink className="h-4 w-4" strokeWidth={2.5} />
                  </a>
                </div>
              </div>
            </div>
          ) : null}
        </div>

        {/* Map */}
        {doctor?.yandex_maps_embed_url ? (
          <div className="card shadow-xl overflow-hidden mb-12 max-w-4xl mx-auto w-full p-0">
            <div className="px-6 py-5 border-b border-neutral-200">
              <h2 className="text-h3-mobile font-semibold text-neutral-900">
                Местоположение
              </h2>
              <p className="mt-1 text-sm text-neutral-600">
                На карте показана точка, где проходит очная консультация
              </p>
            </div>
            <div className="h-[220px] sm:h-[320px] md:h-[440px]">
              <iframe
                src={doctor.yandex_maps_embed_url}
                width="100%"
                height="100%"
                allowFullScreen
                loading="lazy"
                className="h-full w-full border-0"
                title="Карта очного приёма"
              />
            </div>
          </div>
        ) : null}

        {/* How to get there section */}
        <div className="max-w-4xl mx-auto">
          <div className="rounded-2xl border border-neutral-200 bg-gradient-to-br from-neutral-0 to-primary-50 p-6 md:p-10">
            <h2 className="text-h3-mobile md:text-h3-desktop text-neutral-900 mb-8">
              Как добраться?
            </h2>
            <div className="grid gap-8 sm:grid-cols-3">
              {transports.map(({ icon: Icon, title, description }, idx) => (
                <div key={idx} className="text-center">
                  <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-100 text-primary-700 mb-4">
                    <Icon className="h-7 w-7" strokeWidth={1.75} />
                  </span>
                  <h3 className="text-base font-bold text-neutral-900 mb-2">
                    {title}
                  </h3>
                  <p className="text-sm text-neutral-600 leading-relaxed">
                    {description}
                  </p>
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
            <a
              href={doctor.prodoktorov_url}
              target="_blank"
              rel="noreferrer"
              className="btn-primary"
            >
              Запишитесь через ПроДокторов
              <ExternalLink className="h-4 w-4" strokeWidth={2.5} />
            </a>
          ) : (
            <a href="/booking" className="btn-primary">
              Записаться на онлайн-консультацию
              <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
            </a>
          )}
        </div>
      </div>
    </main>
  );
}
