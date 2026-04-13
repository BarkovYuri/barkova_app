import BookingForm from "../../components/booking/BookingForm";

export default function BookingPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-white px-6 py-12">
      <div className="mx-auto max-w-6xl">
        <div className="mb-10 max-w-3xl">
          <p className="inline-flex rounded-full border border-sky-200 bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-sky-700 shadow-sm">
            онлайн-консультация
          </p>

          <h1 className="mt-5 text-4xl font-semibold text-gray-900 md:text-5xl">
            Запись на онлайн-консультацию
          </h1>

          <p className="mt-4 text-lg leading-8 text-gray-600">
            Выберите удобную дату и время, затем оставьте свои данные для
            онлайн-консультации.
          </p>
        </div>

        <BookingForm />
      </div>
    </main>
  );
}