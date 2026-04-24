import { fetchAPI } from "../../lib/api";
import type { DoctorProfile } from "../../lib/types";

export default async function OfficePage() {
  const doctor = (await fetchAPI("/profile")) as DoctorProfile | null;

  return (
    <main className="min-h-screen bg-white px-6 py-12">
      <div className="mx-auto max-w-5xl space-y-8">
        <div className="rounded-3xl border border-gray-100 bg-white p-8 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-sky-600">
            Очный прием
          </p>

          <h1 className="mt-3 text-4xl font-semibold text-gray-900">
            Запись на очную консультацию
          </h1>

          <p className="mt-6 max-w-2xl text-lg leading-8 text-gray-600">
            Запись на очный прием осуществляется через платформу ПроДокторов.
          </p>

          <div className="mt-8 rounded-3xl bg-sky-50 p-6">
            <p className="text-sm uppercase tracking-[0.16em] text-sky-700">
              Адрес приема
            </p>
            <p className="mt-3 text-lg font-medium text-gray-900">
              {doctor?.address || "Адрес пока не указан"}
            </p>
          </div>

          {doctor?.prodoktorov_url ? (
            <div className="mt-8">
              <a
                href={doctor.prodoktorov_url}
                target="_blank"
                rel="noreferrer"
                className="rounded-2xl bg-sky-600 px-6 py-3 text-white transition hover:bg-sky-700"
              >
                Перейти на ПроДокторов
              </a>
            </div>
          ) : null}
        </div>

        {doctor?.yandex_maps_embed_url ? (
          <div className="overflow-hidden rounded-3xl border border-gray-100 bg-white shadow-sm">
            <div className="border-b border-gray-100 px-6 py-5">
              <h2 className="text-xl font-semibold text-gray-900">
                Место очного приема
              </h2>
              <p className="mt-2 text-gray-600">
                На карте показана точка, где проходит очная консультация.
              </p>
            </div>

            <div className="h-[420px] w-full">
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
      </div>
    </main>
  );
}