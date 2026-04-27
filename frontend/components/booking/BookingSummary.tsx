"use client";

import {
  Calendar,
  CheckCircle2,
  Circle,
  Clock,
  MessageSquare,
  Send,
  Users,
} from "lucide-react";

import type { ContactMethod, Slot } from "../../lib/types";

type Props = {
  selectedDate: string;
  selectedSlot: Slot | null;
  contactMethod: ContactMethod;
  contactReady: boolean;
  formReady: boolean;
};

function formatDateLong(dateString: string) {
  if (!dateString) return null;
  const date = new Date(`${dateString}T00:00:00`);
  return new Intl.DateTimeFormat("ru-RU", {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(date);
}

const ContactIcon = {
  telegram: Send,
  vk: Users,
} as const;

export function BookingSummary({
  selectedDate,
  selectedSlot,
  contactMethod,
  contactReady,
  formReady,
}: Props) {
  const dateLabel = formatDateLong(selectedDate);
  const ContactIconCmp =
    ContactIcon[contactMethod as keyof typeof ContactIcon] ?? MessageSquare;
  const contactLabel =
    contactMethod === "telegram"
      ? "Telegram"
      : contactMethod === "vk"
      ? "VK"
      : "Способ связи";

  const checklist = [
    { label: "Дата выбрана", done: !!selectedDate },
    { label: "Время выбрано", done: !!selectedSlot },
    { label: "Данные заполнены", done: formReady },
    { label: "Канал подтверждён", done: contactReady },
  ];
  const completedCount = checklist.filter((i) => i.done).length;
  const allReady = completedCount === checklist.length;

  return (
    <aside className="lg:sticky lg:top-24">
      <div className="rounded-3xl border border-neutral-200 bg-neutral-0 shadow-card overflow-hidden">
        {/* Header */}
        <div className="px-6 py-5 bg-gradient-to-br from-primary-600 to-primary-700 text-neutral-0">
          <p className="text-xs font-semibold uppercase tracking-wider text-primary-100">
            Ваша запись
          </p>
          <p className="mt-1 text-lg font-semibold font-heading">
            {allReady ? "Готово к отправке" : "Заполняется"}
          </p>
          <p className="mt-1 text-xs text-primary-100">
            {completedCount} из {checklist.length} шагов
          </p>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-5">
          {/* Date */}
          <SummaryRow
            icon={Calendar}
            label="Дата"
            value={dateLabel}
            placeholder="Выберите дату слева"
          />

          {/* Time */}
          <SummaryRow
            icon={Clock}
            label="Время"
            value={
              selectedSlot
                ? `${selectedSlot.start_time.slice(
                    0,
                    5
                  )} – ${selectedSlot.end_time.slice(0, 5)}`
                : null
            }
            placeholder="Выберите слот"
          />

          {/* Contact */}
          <SummaryRow
            icon={ContactIconCmp}
            label="Подтверждение"
            value={contactReady ? `${contactLabel} подключён` : null}
            placeholder={`${contactLabel}: ожидание подключения`}
          />

          {/* Checklist */}
          <div className="pt-3 border-t border-neutral-100">
            <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-3">
              Чек-лист
            </p>
            <ul className="space-y-2">
              {checklist.map(({ label, done }) => (
                <li
                  key={label}
                  className="flex items-center gap-2 text-sm transition-colors"
                >
                  {done ? (
                    <CheckCircle2
                      className="h-4 w-4 text-secondary-600 flex-shrink-0"
                      strokeWidth={2.5}
                    />
                  ) : (
                    <Circle
                      className="h-4 w-4 text-neutral-300 flex-shrink-0"
                      strokeWidth={2}
                    />
                  )}
                  <span
                    className={
                      done
                        ? "text-neutral-700 font-medium"
                        : "text-neutral-500"
                    }
                  >
                    {label}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </aside>
  );
}

function SummaryRow({
  icon: Icon,
  label,
  value,
  placeholder,
}: {
  icon: React.ComponentType<{ className?: string; strokeWidth?: number }>;
  label: string;
  value: string | null;
  placeholder: string;
}) {
  const filled = !!value;
  return (
    <div className="flex items-start gap-3">
      <span
        className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl transition-colors ${
          filled
            ? "bg-primary-100 text-primary-700"
            : "bg-neutral-100 text-neutral-400"
        }`}
      >
        <Icon className="h-4 w-4" strokeWidth={2} />
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
          {label}
        </p>
        <p
          className={`mt-0.5 text-sm font-semibold capitalize leading-snug ${
            filled ? "text-neutral-900" : "text-neutral-400"
          }`}
        >
          {value || placeholder}
        </p>
      </div>
    </div>
  );
}
