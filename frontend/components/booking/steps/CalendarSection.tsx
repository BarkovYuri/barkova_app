"use client";

import { addMonths, startOfMonth } from "../hooks/useSlots";
import type { CalendarDay, Slot } from "../../../lib/types";

const WEEKDAY_LABELS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

function formatDateLong(dateString: string) {
  const date = new Date(`${dateString}T00:00:00`);
  return new Intl.DateTimeFormat("ru-RU", {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(date);
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
}: Props) {
  return (
    <section className="rounded-[1.75rem] border border-white/70 bg-white p-4 shadow-xl shadow-sky-100/40 sm:p-6">
      <div className="mb-5 flex items-center gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-sky-100 text-sm font-semibold text-sky-700">1</div>
        <div>
          <h2 className="text-lg font-semibold text-gray-900 sm:text-2xl">Выберите дату и время</h2>
          <p className="mt-1 text-sm text-gray-500">Календарь свободных онлайн-консультаций</p>
        </div>
      </div>

      <div className="rounded-[1.5rem] border border-sky-100 bg-sky-50/70 p-3 sm:p-5">
        <div className="mb-4 flex items-center justify-between gap-2">
          <button type="button" onClick={() => setCurrentMonth(addMonths(currentMonth, -1))} className="rounded-2xl border border-white bg-white px-3 py-2 text-sm font-medium text-gray-700 transition hover:border-sky-200 hover:text-sky-700">←</button>
          <p className="text-center text-sm font-semibold capitalize text-gray-900 sm:text-lg">{formatMonthTitle(currentMonth)}</p>
          <button type="button" onClick={() => setCurrentMonth(addMonths(currentMonth, 1))} className="rounded-2xl border border-white bg-white px-3 py-2 text-sm font-medium text-gray-700 transition hover:border-sky-200 hover:text-sky-700">→</button>
        </div>

        <div className="grid grid-cols-7 gap-1.5 text-center sm:gap-2">
          {WEEKDAY_LABELS.map((label) => (
            <div key={label} className="py-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-400 sm:text-xs">{label}</div>
          ))}

          {loadingDates
            ? Array.from({ length: 35 }).map((_, index) => (
                <div key={`skeleton-${index}`} className="h-12 animate-pulse rounded-2xl bg-white/70 sm:h-14" />
              ))
            : calendarDays.map((day) => {
                if (!day.date || !day.iso) {
                  return <div key={day.key} className="h-12 rounded-2xl sm:h-14" />;
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
                    className={`flex h-12 flex-col items-center justify-center rounded-2xl border text-center transition sm:h-16 ${
                      isSelected
                        ? "border-sky-600 bg-sky-600 text-white shadow-sm"
                        : isDisabled
                        ? "cursor-not-allowed border-gray-100 bg-gray-50 text-gray-300"
                        : "border-white bg-white text-gray-800 hover:border-sky-300 hover:bg-sky-100"
                    } ${isOutside ? "opacity-40" : ""}`}
                  >
                    <span className="text-sm font-semibold">{day.date.getDate()}</span>
                    <span className={`mt-0.5 text-[10px] sm:mt-1 sm:text-[11px] ${isSelected ? "text-sky-100" : "text-gray-400"}`}>
                      {day.isAvailable
                        ? typeof day.freeSlots === "number"
                          ? `${day.freeSlots} мест`
                          : "•"
                        : "—"}
                    </span>
                  </button>
                );
              })}
        </div>
      </div>

      <div ref={slotsSectionRef} className="mt-4 rounded-[1.5rem] border border-gray-100 bg-white p-4 sm:mt-6 sm:p-5">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h3 className="text-xs font-medium uppercase tracking-[0.16em] text-gray-500 sm:text-sm">Свободное время</h3>
            {selectedDate ? <p className="mt-2 text-sm font-medium capitalize text-gray-900 sm:text-base">{formatDateLong(selectedDate)}</p> : null}
          </div>
          {selectedDate ? <div className="rounded-2xl bg-sky-50 px-3 py-2 text-xs text-sky-700 sm:px-4 sm:text-sm">{slots.length} слотов</div> : null}
        </div>

        {loadingSlots ? (
          <div className="mt-4 flex gap-3 overflow-x-auto pb-1 sm:grid sm:grid-cols-3 sm:overflow-visible sm:pb-0">
            {Array.from({ length: 6 }).map((_, index) => (
              <div key={`slot-skeleton-${index}`} className="h-11 min-w-[92px] animate-pulse rounded-2xl bg-gray-100 sm:min-w-0" />
            ))}
          </div>
        ) : slots.length === 0 ? (
          <div className="mt-4 rounded-2xl bg-gray-50 px-4 py-4 text-sm text-gray-500">На выбранную дату свободного времени нет.</div>
        ) : (
          <div className="mt-4 flex gap-3 overflow-x-auto pb-1 sm:grid sm:grid-cols-3 sm:overflow-visible sm:pb-0">
            {slots.map((slot) => {
              const active = selectedSlotId === slot.id;
              return (
                <button
                  key={slot.id}
                  type="button"
                  onClick={() => {
                    setSelectedSlotId(slot.id);
                    if (typeof window !== "undefined" && window.innerWidth < 1024) {
                      setTimeout(() => {
                        formSectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
                      }, 120);
                    }
                  }}
                  className={`min-w-[96px] rounded-2xl border px-4 py-3 text-sm font-medium transition sm:min-w-0 sm:text-base ${
                    active
                      ? "border-sky-600 bg-sky-600 text-white shadow-sm"
                      : "border-gray-200 bg-white text-gray-700 hover:border-sky-300 hover:bg-sky-50"
                  }`}
                >
                  {slot.start_time.slice(0, 5)}
                </button>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}
