"use client";

import { CalendarOff, ChevronLeft, ChevronRight, Globe2 } from "lucide-react";
import Link from "next/link";
import { capitalizeFirst } from "../../../lib/format";
import { reachGoal } from "../../../lib/metrika";
import { localTimeHint } from "../hooks/useScheduleInfo";
import { addMonths, startOfMonth } from "../hooks/useSlots";
import type { CalendarDay, ScheduleInfo, Slot } from "../../../lib/types";

function plural(n: number, one: string, few: string, many: string): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return one;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return few;
  return many;
}

const WEEKDAY_LABELS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

function formatDateLong(dateString: string) {
  const date = new Date(`${dateString}T00:00:00`);
  return new Intl.DateTimeFormat("ru-RU", {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(date);
}

// «в ноябре 2026 г.»: Intl отдаёт месяц только в именительном падеже.
const MONTHS_PREPOSITIONAL = [
  "январе", "феврале", "марте", "апреле", "мае", "июне",
  "июле", "августе", "сентябре", "октябре", "ноябре", "декабре",
];

function formatMonthPrepositional(date: Date) {
  return `${MONTHS_PREPOSITIONAL[date.getMonth()]} ${date.getFullYear()} г.`;
}

function formatMonthTitle(date: Date) {
  return new Intl.DateTimeFormat("ru-RU", {
    month: "long",
    year: "numeric",
  }).format(date);
}

type Props = {
  loadingDates: boolean;
  currentMonth: Date;
  setCurrentMonth: (d: Date) => void;
  calendarDays: CalendarDay[];
  selectedDate: string;
  setSelectedDate: (value: string) => void;
  slots: Slot[];
  loadingSlots: boolean;
  selectedSlotId: number | null;
  setSelectedSlotId: (id: number) => void;
  formSectionRef: React.RefObject<HTMLDivElement | null>;
  slotsSectionRef: React.RefObject<HTMLDivElement | null>;
  scheduleInfo: ScheduleInfo | null;
  /** Есть ли свободные даты хотя бы в каком-то месяце. */
  hasAnyDates: boolean;
};

export function CalendarSection({
  loadingDates,
  currentMonth,
  setCurrentMonth,
  calendarDays,
  selectedDate,
  setSelectedDate,
  slots,
  loadingSlots,
  selectedSlotId,
  setSelectedSlotId,
  formSectionRef,
  slotsSectionRef,
  scheduleInfo,
  hasAnyDates,
}: Props) {
  return (
    <section className="animate-fade-in rounded-3xl border border-neutral-200 bg-neutral-0 p-4 shadow-card sm:p-6">
      {/* Header */}
      <div className="mb-6 flex items-center gap-4">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-primary-100 text-lg font-bold font-heading text-primary-700">
          1
        </div>
        <div className="flex-1">
          <h2 className="text-h3-mobile sm:text-h3-desktop text-neutral-900">
            Выберите дату и время
          </h2>
          <p className="mt-1 text-sm text-neutral-500">
            Календарь свободных онлайн-разборов
          </p>
        </div>
      </div>

      {/* Calendar */}
      <div className="rounded-2xl border border-neutral-200 bg-gradient-to-b from-neutral-50 to-neutral-0 p-4 sm:p-6">
        {/* Month Navigation */}
        <div className="mb-6 flex items-center justify-between gap-3">
          <button
            type="button"
            onClick={() => setCurrentMonth(addMonths(currentMonth, -1))}
            className="group relative h-11 w-11 flex items-center justify-center rounded-xl border border-neutral-300 bg-neutral-0 text-neutral-600 transition-all hover:border-primary-400 hover:bg-primary-50 hover:text-primary-700"
            aria-label="Previous month"
          >
            <ChevronLeft className="h-5 w-5" strokeWidth={2.25} />
          </button>
          <p className="flex-1 text-center text-lg font-semibold font-heading text-neutral-900 sm:text-xl">
            {capitalizeFirst(formatMonthTitle(currentMonth))}
          </p>
          <button
            type="button"
            onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
            className="group relative h-11 w-11 flex items-center justify-center rounded-xl border border-neutral-300 bg-neutral-0 text-neutral-600 transition-all hover:border-primary-400 hover:bg-primary-50 hover:text-primary-700"
            aria-label="Next month"
          >
            <ChevronRight className="h-5 w-5" strokeWidth={2.25} />
          </button>
        </div>

        {/* Weekday Labels */}
        <div className="grid grid-cols-7 gap-2 mb-3">
          {WEEKDAY_LABELS.map((label) => (
            <div
              key={label}
              className="py-2 text-center text-xs font-bold uppercase tracking-widest text-neutral-500"
            >
              {label}
            </div>
          ))}
        </div>

        {/* Empty-state: в этом месяце нет ни одного доступного дня */}
        {!loadingDates &&
          calendarDays.length > 0 &&
          calendarDays.every((d) => !d.isAvailable) ? (
          <div className="mb-3 flex flex-col items-center gap-3 rounded-2xl border border-dashed border-neutral-300 bg-neutral-50 px-4 py-6 text-center">
            <CalendarOff className="h-6 w-6 text-neutral-400" strokeWidth={1.75} />
            <p className="text-sm text-neutral-600">
              {hasAnyDates ? (
                <>
                  В&nbsp;{formatMonthPrepositional(currentMonth)} нет свободных дат
                  для&nbsp;онлайн-разбора.
                </>
              ) : (
                <>
                  Сейчас свободного времени для онлайн-разбора нет. Напишите
                  или позвоните, врач подберёт время.
                </>
              )}
            </p>
            {hasAnyDates ? (
              <button
                type="button"
                onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
                className="text-sm font-semibold text-primary-700 underline-offset-4 hover:underline"
              >
                Посмотреть следующий месяц →
              </button>
            ) : (
              <Link
                href="/contacts"
                className="text-sm font-semibold text-primary-700 underline-offset-4 hover:underline"
              >
                Контакты врача →
              </Link>
            )}
          </div>
        ) : null}

        {/* Calendar Days */}
        <div className="grid grid-cols-7 gap-2 text-center sm:gap-2.5">
          {loadingDates
            ? Array.from({ length: 35 }).map((_, index) => (
                <div
                  key={`skeleton-${index}`}
                  className="h-12 rounded-lg bg-neutral-200 animate-pulse sm:h-14"
                />
              ))
            : calendarDays.map((day) => {
                if (!day.date || !day.iso) {
                  return <div key={day.key} className="h-12 sm:h-14" />;
                }

                const isSelected = selectedDate === day.iso;
                const isDisabled = !day.isAvailable;
                const isOutside = !day.isCurrentMonth;

                return (
                  <button
                    key={day.key}
                    type="button"
                    disabled={isDisabled}
                    onClick={() => {
                      setSelectedDate(day.iso!);
                      setCurrentMonth(startOfMonth(day.date!));
                    }}
                    className={`
                      relative flex h-12 sm:h-14 flex-col items-center justify-center rounded-xl
                      border text-center font-semibold transition-all duration-200
                      ${
                        isSelected
                          ? "border-primary-600 bg-primary-600 text-white shadow-lg shadow-primary-500/30"
                          : isDisabled
                          ? "cursor-not-allowed border-neutral-200 bg-neutral-50 text-neutral-300"
                          : "border-neutral-200 bg-neutral-0 text-neutral-800 hover:border-primary-400 hover:bg-primary-50 hover:-translate-y-0.5"
                      }
                      ${isOutside ? "opacity-40" : ""}
                    `}
                  >
                    <span className="text-sm font-bold">{day.date.getDate()}</span>
                    <span
                      className={`
                        mt-0.5 text-[10px] sm:mt-1 sm:text-xs font-medium
                        ${isSelected ? "text-primary-100" : isDisabled ? "text-neutral-400" : "text-neutral-500"}
                      `}
                    >
                      {day.isAvailable
                        ? typeof day.freeSlots === "number"
                          ? `${day.freeSlots} ${plural(day.freeSlots, "место", "места", "мест")}`
                          : "•"
                        : "—"}
                    </span>
                  </button>
                );
              })}
        </div>
      </div>

      {/* Slots Section */}
      <div ref={slotsSectionRef} className="mt-6 rounded-2xl border border-neutral-200 bg-neutral-0 p-4 sm:p-6">
        <div className="flex items-center justify-between gap-3 mb-4">
          <div className="flex-1">
            <p className="text-xs font-bold uppercase tracking-widest text-neutral-500">Свободное время</p>
            {selectedDate ? (
              <p className="mt-2 text-lg font-bold text-neutral-900">
                {capitalizeFirst(formatDateLong(selectedDate))}
              </p>
            ) : null}
          </div>
          {selectedDate ? (
            <div className="rounded-full bg-primary-100 px-3 py-1.5 text-xs font-semibold text-primary-700 sm:px-4 sm:text-sm">
              {slots.length} {plural(slots.length, "слот", "слота", "слотов")}
            </div>
          ) : null}
        </div>

        {scheduleInfo?.label ? (
          <p className="mb-3 inline-flex items-center gap-1.5 text-xs font-medium text-neutral-500">
            <Globe2 className="h-3.5 w-3.5" strokeWidth={2} />
            Указано {scheduleInfo.label}
          </p>
        ) : null}

        {loadingSlots ? (
          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {Array.from({ length: 8 }).map((_, index) => (
              <div
                key={`slot-skeleton-${index}`}
                className="h-11 rounded-lg bg-neutral-200 animate-pulse"
              />
            ))}
          </div>
        ) : slots.length === 0 ? (
          <div className="mt-4 flex flex-col items-center gap-2 rounded-2xl border border-dashed border-neutral-300 bg-neutral-50 px-4 py-6 text-center">
            <CalendarOff className="h-5 w-5 text-neutral-400" strokeWidth={1.75} />
            <p className="text-sm text-neutral-600">
              На выбранную дату свободного времени нет.
            </p>
            <p className="text-xs text-neutral-500">
              Попробуйте другую дату — доступные дни выделены в календаре.
            </p>
          </div>
        ) : (
          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {slots.map((slot) => {
              const active = selectedSlotId === slot.id;
              // Слот держит другой пациент, который сейчас заполняет форму.
              const reservedByOther = Boolean(slot.is_reserved) && !active;
              const hint = localTimeHint(slot.starts_at, slot.start_time);
              return (
                <button
                  key={slot.id}
                  type="button"
                  disabled={reservedByOther}
                  title={reservedByOther ? "Это время сейчас бронирует другой пациент" : undefined}
                  onClick={() => {
                    setSelectedSlotId(slot.id);
                    reachGoal("booking_slot_selected");
                    if (typeof window !== "undefined" && window.innerWidth < 1024) {
                      setTimeout(() => {
                        formSectionRef.current?.scrollIntoView({
                          behavior: "smooth",
                          block: "start",
                        });
                      }, 120);
                    }
                  }}
                  className={`
                    relative rounded-xl border px-3 py-3 text-sm font-semibold
                    transition-all duration-200
                    ${
                      active
                        ? "border-primary-600 bg-primary-600 text-white shadow-lg shadow-primary-500/30"
                        : reservedByOther
                        ? "cursor-not-allowed border-neutral-200 bg-neutral-50 text-neutral-400"
                        : "border-neutral-300 bg-neutral-0 text-neutral-700 hover:border-primary-400 hover:bg-primary-50 hover:-translate-y-0.5"
                    }
                  `}
                >
                  <span className="block">{slot.start_time.slice(0, 5)}</span>
                  {hint ? (
                    <span className={`block text-[11px] font-medium ${active ? "text-primary-100" : "text-neutral-500"}`}>
                      у вас {hint}
                    </span>
                  ) : null}
                </button>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}
