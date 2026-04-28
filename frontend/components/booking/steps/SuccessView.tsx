"use client";

import {
  ArrowLeft,
  Calendar,
  CheckCircle2,
  Clock,
  MessageCircle,
  Send,
  Sparkles,
  Users,
} from "lucide-react";
import type { Slot, ContactMethod } from "../../../lib/types";

function formatDateLong(dateString: string) {
  const date = new Date(`${dateString}T00:00:00`);
  return new Intl.DateTimeFormat("ru-RU", {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(date);
}

type Props = {
  selectedDate: string;
  selectedSlot: Slot | null;
  contactMethod: ContactMethod;
};

const ContactIcon = {
  telegram: Send,
  vk: Users,
} as const;

export function SuccessView({
  selectedDate,
  selectedSlot,
  contactMethod,
}: Props) {
  const ContactIconCmp =
    ContactIcon[contactMethod as keyof typeof ContactIcon] ?? MessageCircle;
  const contactLabel =
    contactMethod === "telegram"
      ? "Telegram"
      : contactMethod === "vk"
      ? "VK"
      : "Способ связи";

  return (
    <div className="mx-auto max-w-2xl animate-fade-in">
      {/* Success Card */}
      <div className="relative overflow-hidden rounded-3xl border border-neutral-200 bg-gradient-to-b from-neutral-0 to-neutral-50 p-6 shadow-xl sm:p-10">
        {/* Decorative background */}
        <div className="absolute inset-0 -z-10 opacity-30">
          <div className="absolute -top-20 -right-20 h-56 w-56 bg-secondary-200 rounded-full blur-3xl" />
          <div className="absolute -bottom-20 -left-20 h-56 w-56 bg-primary-200 rounded-full blur-3xl" />
        </div>

        {/* Success Icon */}
        <div className="flex justify-center mb-6">
          <div className="relative h-24 w-24">
            <div className="absolute inset-0 flex items-center justify-center rounded-full bg-secondary-500 text-neutral-0 shadow-lg shadow-secondary-500/40">
              <CheckCircle2 className="h-12 w-12" strokeWidth={2.25} />
            </div>
            <div className="absolute inset-0 rounded-full border-2 border-secondary-300 animate-pulse-gentle" />
          </div>
        </div>

        {/* Main content */}
        <div className="text-center">
          <h2 className="text-neutral-900">Отлично! Заявка отправлена</h2>
          <p className="mt-4 text-neutral-600 text-base-large leading-relaxed">
            Мы получили вашу заявку на онлайн-консультацию. Врач или
            администратор свяжется с вами в ближайшее время для подтверждения
            через{" "}
            <span className="font-semibold text-primary-700">
              {contactLabel}
            </span>
            .
          </p>
        </div>

        {/* Booking Details */}
        {selectedDate && selectedSlot ? (
          <div className="mt-8 rounded-2xl border border-secondary-200 bg-secondary-50 p-5 sm:p-6">
            <p className="mb-4 text-ui-label uppercase text-secondary-700">
              Детали записи
            </p>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-neutral-0 text-secondary-700 shadow-sm">
                  <Calendar className="h-5 w-5" strokeWidth={2} />
                </span>
                <div>
                  <p className="text-xs text-secondary-700 uppercase tracking-wide font-medium">
                    Дата приёма
                  </p>
                  <p className="text-base font-semibold text-neutral-900 capitalize">
                    {formatDateLong(selectedDate)}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-neutral-0 text-secondary-700 shadow-sm">
                  <Clock className="h-5 w-5" strokeWidth={2} />
                </span>
                <div>
                  <p className="text-xs text-secondary-700 uppercase tracking-wide font-medium">
                    Время приёма
                  </p>
                  <p className="text-base font-semibold text-neutral-900">
                    {selectedSlot.start_time.slice(0, 5)} –{" "}
                    {selectedSlot.end_time.slice(0, 5)}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-neutral-0 text-secondary-700 shadow-sm">
                  <ContactIconCmp className="h-5 w-5" strokeWidth={2} />
                </span>
                <div>
                  <p className="text-xs text-secondary-700 uppercase tracking-wide font-medium">
                    Подтверждение
                  </p>
                  <p className="text-base font-semibold text-neutral-900">
                    {contactLabel}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : null}

        {/* Next Steps */}
        <div className="mt-8 space-y-3 rounded-2xl bg-neutral-100 p-5 sm:p-6">
          <p className="text-sm font-semibold text-neutral-900 inline-flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary-600" strokeWidth={2.5} />
            Что дальше?
          </p>
          <ul className="space-y-3 text-sm text-neutral-700">
            <li className="flex items-start gap-2">
              <CheckCircle2
                className="h-4 w-4 flex-shrink-0 text-primary-600 mt-0.5"
                strokeWidth={2.5}
              />
              <span>
                Вы получите сообщение в{" "}
                {contactMethod === "telegram" ? "Telegram" : "VK"} для
                подтверждения записи
              </span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2
                className="h-4 w-4 flex-shrink-0 text-primary-600 mt-0.5"
                strokeWidth={2.5}
              />
              <span>
                Все детали приёма врач уточнит дополнительно в этом же чате
              </span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2
                className="h-4 w-4 flex-shrink-0 text-primary-600 mt-0.5"
                strokeWidth={2.5}
              />
              <span>
                Если планы изменятся — вы сможете отменить запись прямо в чате
              </span>
            </li>
          </ul>
        </div>

        {/* Action Button */}
        <div className="mt-8 flex justify-center">
          <a href="/" className="btn-primary">
            <ArrowLeft className="h-4 w-4" strokeWidth={2.5} />
            Вернуться на главную
          </a>
        </div>
      </div>
    </div>
  );
}
