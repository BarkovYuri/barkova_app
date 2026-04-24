import { fetchAPI } from "../lib/api";
import type { DoctorProfile } from "../lib/types";

export default async function Home() {
  const doctor = (await fetchAPI("/profile")) as DoctorProfile | null;

  if (!doctor) {
    return (
      <main className="min-h-screen bg-white px-4 py-12 sm:px-6 sm:py-16">
        <div className="mx-auto max-w-4xl rounded-3xl border border-gray-100 bg-white p-8 shadow-sm sm:p-10">
          <h1 className="text-3xl font-semibold text-gray-900">
            Профиль врача не найден
          </h1>
          <p className="mt-4 text-gray-600">
            Добавь профиль врача в админке Django.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="bg-white text-gray-900">
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-sky-50 via-white to-white" />

        <div className="relative mx-auto grid max-w-6xl gap-10 px-4 py-12 sm:px-6 sm:py-16 md:grid-cols-[1.1fr_0.9fr] md:items-center md:py-24">
          <div>
            <p className="inline-flex rounded-full border border-sky-200 bg-white px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.2em] text-sky-700 shadow-sm sm:text-xs">
              врач-инфекционист
            </p>

            <h1 className="mt-5 text-3xl font-semibold leading-tight sm:text-4xl md:text-6xl">
              {doctor.full_name}
            </h1>

            <p className="mt-5 max-w-2xl text-base leading-8 text-gray-600 sm:text-lg">
              {doctor.description || "Описание пока не заполнено."}
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:gap-4">
              <a
                href="/booking"
                className="rounded-2xl bg-sky-600 px-6 py-3.5 text-center text-white shadow-sm transition hover:bg-sky-700"
              >
                Записаться на онлайн-консультацию
              </a>

              <a
                href="/office"
                className="rounded-2xl border border-sky-200 bg-white px-6 py-3.5 text-center text-sky-700 transition hover:bg-sky-50"
              >
                Записаться на очный прием
              </a>
            </div>

            <div className="mt-10 grid gap-4 sm:grid-cols-3">
              <div className="rounded-3xl border border-white/70 bg-white/80 p-5 shadow-sm">
                <div className="text-sm text-gray-500">Стаж</div>
                <div className="mt-2 text-2xl font-semibold text-gray-900">
                  {doctor.experience_years ?? 0} года
                </div>
              </div>

              <div className="rounded-3xl border border-white/70 bg-white/80 p-5 shadow-sm">
                <div className="text-sm text-gray-500">Формат</div>
                <div className="mt-2 text-2xl font-semibold text-gray-900">
                  онлайн
                </div>
              </div>

              <div className="rounded-3xl border border-white/70 bg-white/80 p-5 shadow-sm">
                <div className="text-sm text-gray-500">Очный прием</div>
                <div className="mt-2 text-2xl font-semibold text-gray-900">
                  да
                </div>
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="absolute -left-4 -top-4 h-24 w-24 rounded-full bg-sky-100 blur-2xl sm:h-32 sm:w-32" />
            <div className="absolute -bottom-6 -right-4 h-28 w-28 rounded-full bg-sky-50 blur-2xl sm:h-40 sm:w-40" />

            <div className="relative rounded-[2rem] border border-sky-100 bg-white p-3 shadow-xl shadow-sky-100/50 sm:p-4">
              {doctor.photo_url ? (
                <img
                  src={doctor.photo_url}
                  alt={doctor.full_name}
                  className="h-[360px] w-full rounded-[1.5rem] object-cover sm:h-[420px] md:h-[520px]"
                />
              ) : (
                <div className="flex h-[360px] w-full items-center justify-center rounded-[1.5rem] bg-gray-100 text-gray-400 sm:h-[420px] md:h-[520px]">
                  Фото пока не загружено
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="border-t border-gray-100 bg-white">
        <div className="mx-auto grid max-w-6xl gap-6 px-4 py-12 sm:px-6 sm:py-16 md:grid-cols-3">
          <div className="rounded-3xl border border-gray-100 bg-white p-7 shadow-sm">
            <div className="text-sm font-medium uppercase tracking-[0.16em] text-sky-600">
              Онлайн-консультация
            </div>
            <h2 className="mt-4 text-2xl font-semibold text-gray-900">
              Быстрая запись через сайт
            </h2>
            <p className="mt-4 leading-7 text-gray-600">
              Онлайн-консультация оформляется через форму записи на сайте:
              выберите дату, время и оставьте данные.
            </p>
          </div>

          <div className="rounded-3xl border border-gray-100 bg-white p-7 shadow-sm">
            <div className="text-sm font-medium uppercase tracking-[0.16em] text-sky-600">
              Очный прием
            </div>
            <h2 className="mt-4 text-2xl font-semibold text-gray-900">
              Запись через ПроДокторов
            </h2>
            <p className="mt-4 leading-7 text-gray-600">
              Для очного приема используется отдельная запись через платформу
              ПроДокторов.
            </p>
          </div>

          <div className="rounded-3xl border border-gray-100 bg-white p-7 shadow-sm">
            <div className="text-sm font-medium uppercase tracking-[0.16em] text-sky-600">
              Адрес приема
            </div>
            <h2 className="mt-4 text-2xl font-semibold text-gray-900">
              Очная консультация
            </h2>
            <p className="mt-4 leading-7 text-gray-600">
              {doctor.address || "Адрес пока не указан."}
            </p>

            {doctor.prodoktorov_url ? (
              <a
                href={doctor.prodoktorov_url}
                target="_blank"
                rel="noreferrer"
                className="mt-5 inline-flex text-sm font-medium text-sky-600 transition hover:text-sky-700"
              >
                Перейти на ПроДокторов
              </a>
            ) : null}
          </div>
        </div>
      </section>
    </main>
  );
}