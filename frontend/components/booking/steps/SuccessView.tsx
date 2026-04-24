"use client";

import type { Slot, ContactMethod } from "../../../lib/types";

function formatDateLong(dateString: string) {
  const date = new Date(`${dateString}T00:00:00`);
  return new Intl.DateTimeFormat("ru-RU", {
    weekday: "long", day: "numeric", month: "long",
  }).format(date);
}

type Props = {
  selectedDate: string;
  selectedSlot: Slot | null;
  contactMethod: ContactMethod;
};

export function SuccessView({ selectedDate, selectedSlot, contactMethod }: Props) {
  return (
    <div className="mx-auto max-w-3xl rounded-[2rem] border border-sky-100 bg-white p-5 shadow-xl shadow-sky-100/50 sm:p-8">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-sky-100 text-sky-700">✓</div>

      <h2 className="mt-5 text-2xl font-semibold text-gray-900 sm:text-3xl">
        Заявка на онлайн-консультацию отправлена
      </h2>
      <p className="mt-4 leading-7 text-gray-600">
        Мы получили вашу заявку. Врач или администратор свяжется с вами для подтверждения записи выбранным способом.
      </p>

      {selectedDate && selectedSlot ? (
        <div className="mt-6 rounded-3xl border border-gray-100 bg-sky-50 p-4 sm:p-6">
          <p className="text-sm uppercase tracking-[0.16em] text-sky-700">Детали записи</p>
          <p className="mt-3 text-base text-gray-800 sm:text-lg">
            <span className="font-medium">Дата:</span> {formatDateLong(selectedDate)}
          </p>
          <p className="mt-2 text-base text-gray-800 sm:text-lg">
            <span className="font-medium">Время:</span>{" "}
            {selectedSlot.start_time.slice(0, 5)} – {selectedSlot.end_time.slice(0, 5)}
          </p>
          <p className="mt-2 text-base text-gray-800 sm:text-lg">
            <span className="font-medium">Подтверждение:</span>{" "}
            {contactMethod === "telegram" ? "Telegram" : "VK"}
          </p>
        </div>
      ) : null}

      <a
        href="/"
        className="mt-7 inline-flex rounded-2xl bg-sky-600 px-6 py-3 text-white transition hover:bg-sky-700"
      >
        Вернуться на главную
      </a>
    </div>
  );
}
