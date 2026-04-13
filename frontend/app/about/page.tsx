import { fetchAPI } from "../../lib/api";

type DoctorProfile = {
  full_name: string;
  description: string;
  education?: string;
  experience_years?: number;
  address?: string;
  prodoktorov_url?: string;
  photo_url?: string | null;
  instagram_url?: string;
  vk_url?: string;
  dzen_url?: string;
};

export default async function AboutPage() {
  const doctor: DoctorProfile | null = await fetchAPI("/profile");

  if (!doctor) {
    return (
      <main className="min-h-screen bg-white px-6 py-12">
        <div className="mx-auto max-w-5xl rounded-3xl border border-gray-100 bg-white p-10 shadow-sm">
          <h1 className="text-4xl font-semibold text-gray-900">О враче</h1>
          <p className="mt-4 text-gray-600">Профиль врача пока не заполнен.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="bg-white text-gray-900">
      <section className="bg-gradient-to-br from-sky-50 via-white to-white px-6 py-12">
        <div className="mx-auto grid max-w-6xl gap-10 md:grid-cols-[380px_1fr] md:items-center">
          <div className="relative">
            <div className="absolute -left-4 -top-4 h-24 w-24 rounded-full bg-sky-100 blur-2xl" />
            <div className="relative rounded-[2rem] border border-sky-100 bg-white p-4 shadow-xl shadow-sky-100/40">
              {doctor.photo_url ? (
                <img
                  src={doctor.photo_url}
                  alt={doctor.full_name}
                  className="h-[500px] w-full rounded-[1.5rem] object-cover"
                />
              ) : (
                <div className="flex h-[500px] w-full items-center justify-center rounded-[1.5rem] bg-gray-100 text-gray-400">
                  Фото не загружено
                </div>
              )}
            </div>
          </div>

          <div>
            <p className="inline-flex rounded-full border border-sky-200 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-sky-700 shadow-sm">
              о враче
            </p>

            <h1 className="mt-5 text-4xl font-semibold leading-tight md:text-5xl">
              {doctor.full_name}
            </h1>

            <p className="mt-6 max-w-3xl text-lg leading-8 text-gray-600">
              {doctor.description || "Описание пока не заполнено."}
            </p>

            <div className="mt-8 flex flex-wrap gap-4">
              <a
                href="/booking"
                className="rounded-2xl bg-sky-600 px-6 py-3 text-white transition hover:bg-sky-700"
              >
                Записаться на онлайн-консультацию
              </a>

              {doctor.prodoktorov_url ? (
                <a
                  href={doctor.prodoktorov_url}
                  target="_blank"
                  rel="noreferrer"
                  className="rounded-2xl border border-sky-200 bg-white px-6 py-3 text-sky-700 transition hover:bg-sky-50"
                >
                  ПроДокторов
                </a>
              ) : null}
            </div>
          </div>
        </div>
      </section>

      <section className="border-t border-gray-100 bg-white px-6 py-12">
        <div className="mx-auto grid max-w-6xl gap-6 md:grid-cols-3">
          <div className="rounded-3xl border border-gray-100 bg-white p-8 shadow-sm">
            <div className="text-sm font-medium uppercase tracking-[0.16em] text-sky-600">
              Стаж
            </div>
            <div className="mt-4 text-3xl font-semibold text-gray-900">
              {doctor.experience_years ?? 0} лет
            </div>
            <p className="mt-3 leading-7 text-gray-600">
              Практический опыт консультирования и сопровождения пациентов.
            </p>
          </div>

          <div className="rounded-3xl border border-gray-100 bg-white p-8 shadow-sm">
            <div className="text-sm font-medium uppercase tracking-[0.16em] text-sky-600">
              Образование
            </div>
            <p className="mt-4 leading-8 text-gray-600">
              {doctor.education || "Информация об образовании пока не добавлена."}
            </p>
          </div>

          <div className="rounded-3xl border border-gray-100 bg-white p-8 shadow-sm">
            <div className="text-sm font-medium uppercase tracking-[0.16em] text-sky-600">
              Очный прием
            </div>
            <p className="mt-4 leading-8 text-gray-600">
              {doctor.address || "Адрес приема пока не указан."}
            </p>
            <a
              href="/office"
              className="mt-5 inline-flex text-sm font-medium text-sky-600 transition hover:text-sky-700"
            >
              Подробнее об очном приеме
            </a>
          </div>
        </div>
      </section>

      <section className="border-t border-gray-100 bg-gray-50 px-6 py-12">
        <div className="mx-auto max-w-6xl">
          <div className="rounded-[2rem] border border-gray-100 bg-white p-8 shadow-sm">
            <p className="text-sm font-medium uppercase tracking-[0.16em] text-sky-600">
              Подход к консультации
            </p>

            <h2 className="mt-4 text-3xl font-semibold text-gray-900">
              Спокойно, понятно и по делу
            </h2>

            <div className="mt-6 grid gap-6 md:grid-cols-3">
              <div className="rounded-3xl bg-sky-50 p-6">
                <div className="text-lg font-semibold text-gray-900">
                  Разбор жалоб и анализов
                </div>
                <p className="mt-3 leading-7 text-gray-600">
                  Консультация строится на понятном разборе симптомов, анализов и
                  уже проведенных обследований.
                </p>
              </div>

              <div className="rounded-3xl bg-sky-50 p-6">
                <div className="text-lg font-semibold text-gray-900">
                  Пошаговые рекомендации
                </div>
                <p className="mt-3 leading-7 text-gray-600">
                  Пациент получает структурированный план: что делать сейчас, что
                  наблюдать и какие обследования нужны дальше.
                </p>
              </div>

              <div className="rounded-3xl bg-sky-50 p-6">
                <div className="text-lg font-semibold text-gray-900">
                  Удобный формат
                </div>
                <p className="mt-3 leading-7 text-gray-600">
                  Можно выбрать онлайн-консультацию через сайт или очный прием
                  через ПроДокторов.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}