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
    <div className="mx-auto max-w-2xl animate-fade-in">
      {/* Success Card */}
      <div className="relative rounded-xl border border-neutral-200 bg-gradient-to-b from-white to-neutral-50 p-6 shadow-lg sm:p-10">
        {/* Decorative background */}
        <div className="absolute inset-0 -z-10 opacity-10">
          <div className="absolute top-0 right-0 w-40 h-40 bg-green-500 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-40 h-40 bg-primary-500 rounded-full blur-3xl" />
        </div>

        {/* Success Icon */}
        <div className="flex justify-center mb-6">
          <div className="relative h-24 w-24 animate-bounce" style={{ animationDuration: "1.5s" }}>
            <div className="absolute inset-0 flex items-center justify-center rounded-full bg-gradient-to-br from-green-400 to-green-500 text-5xl text-white shadow-lg">
              ✓
            </div>
            {/* Pulse rings */}
            <div className="absolute inset-0 rounded-full border-2 border-green-400 animate-pulse" />
          </div>
        </div>

        {/* Main content */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-neutral-900 sm:text-3xl">
            Отлично! Заявка отправлена
          </h2>
          <p className="mt-3 text-neutral-600 sm:text-lg">
            Мы получили вашу заявку на онлайн-консультацию. Врач или администратор свяжется с вами в ближайшее время для подтверждения через{" "}
            <span className="font-semibold text-primary-600">
              {contactMethod === "telegram"
                ? "Telegram"
                : contactMethod === "vk"
                ? "VK"
                : "выбранный способ связи"}
            </span>
            .
          </p>
        </div>

        {/* Booking Details */}
        {selectedDate && selectedSlot ? (
          <div className="mt-8 rounded-lg border border-green-200 bg-green-50 p-5 sm:p-6">
            <p className="mb-4 text-xs font-bold uppercase tracking-widest text-green-700">
              📋 Детали записи
            </p>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="text-2xl">📅</span>
                <div>
                  <p className="text-xs text-green-600 uppercase tracking-wide">Дата приема</p>
                  <p className="text-lg font-semibold text-neutral-900 capitalize">
                    {formatDateLong(selectedDate)}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-2xl">🕐</span>
                <div>
                  <p className="text-xs text-green-600 uppercase tracking-wide">Время приема</p>
                  <p className="text-lg font-semibold text-neutral-900">
                    {selectedSlot.start_time.slice(0, 5)} –{" "}
                    {selectedSlot.end_time.slice(0, 5)}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-2xl">
                  {contactMethod === "telegram"
                    ? "💬"
                    : contactMethod === "vk"
                    ? "👥"
                    : "📱"}
                </span>
                <div>
                  <p className="text-xs text-green-600 uppercase tracking-wide">Подтверждение</p>
                  <p className="text-lg font-semibold text-neutral-900">
                    {contactMethod === "telegram"
                      ? "Telegram"
                      : contactMethod === "vk"
                      ? "VK"
                      : "Способ связи"}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : null}

        {/* Next Steps */}
        <div className="mt-8 space-y-3 rounded-lg bg-neutral-100 p-5 sm:p-6">
          <p className="text-sm font-semibold text-neutral-900">📍 Что дальше?</p>
          <ul className="space-y-2 text-sm text-neutral-700">
            <li className="flex items-start gap-2">
              <span className="flex-shrink-0 text-primary-600">✓</span>
              <span>
                Вы получите сообщение в {contactMethod === "telegram" ? "Telegram" : "VK"} для
                подтверждения записи
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="flex-shrink-0 text-primary-600">✓</span>
              <span>Ссылка на видеоконференцию будет отправлена перед консультацией</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="flex-shrink-0 text-primary-600">✓</span>
              <span>Убедитесь, что у вас есть доступ в интернет и рабочая веб-камера</span>
            </li>
          </ul>
        </div>

        {/* Action Buttons */}
        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <a
            href="/"
            className="flex items-center justify-center rounded-lg bg-gradient-to-r from-primary-600 to-secondary-600 px-6 py-3 font-semibold text-white transition-all hover:shadow-lg hover:scale-105 active:scale-95"
          >
            ← Вернуться на главную
          </a>
          <a
            href="tel:+7"
            className="flex items-center justify-center rounded-lg border-2 border-neutral-300 bg-white px-6 py-3 font-semibold text-neutral-900 transition-all hover:border-primary-400 hover:bg-primary-50"
          >
            ☎️ Связаться с нами
          </a>
        </div>
      </div>

      {/* Floating confetti-like elements */}
      <div className="mt-6 flex justify-center gap-4 text-4xl animate-pulse">
        <span>🎉</span>
        <span>✨</span>
        <span>🎊</span>
      </div>
    </div>
  );
