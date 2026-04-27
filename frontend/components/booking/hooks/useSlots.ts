"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { fetchAPI } from "../../../lib/api";
import type { NormalizedDate, Slot, CalendarDay } from "../../../lib/types";

function normalizeDates(
  input: (string | { date: string; free_slots?: number })[]
): NormalizedDate[] {
  return input.map((item) =>
    typeof item === "string" ? { date: item } : item
  );
}

export function isoDate(date: Date): string {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, "0");
  const day = `${date.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function startOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

export function addMonths(date: Date, amount: number): Date {
  return new Date(date.getFullYear(), date.getMonth() + amount, 1);
}

export function getCalendarDays(
  monthDate: Date,
  availableMap: Map<string, { free_slots?: number }>
): CalendarDay[] {
  const firstDay = startOfMonth(monthDate);
  const jsWeekday = firstDay.getDay();
  const mondayBased = jsWeekday === 0 ? 6 : jsWeekday - 1;
  const gridStart = new Date(firstDay);
  gridStart.setDate(firstDay.getDate() - mondayBased);

  const days: CalendarDay[] = [];
  for (let i = 0; i < 42; i++) {
    const current = new Date(gridStart);
    current.setDate(gridStart.getDate() + i);
    const currentIso = isoDate(current);
    const available = availableMap.get(currentIso);
    days.push({
      key: `${currentIso}-${i}`,
      date: current,
      iso: currentIso,
      isCurrentMonth: current.getMonth() === monthDate.getMonth(),
      isAvailable: Boolean(available),
      freeSlots: available?.free_slots,
    });
  }
  return days;
}

export function useDates() {
  const [dates, setDates] = useState<NormalizedDate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedDate, setSelectedDate] = useState("");
  const [currentMonth, setCurrentMonth] = useState<Date>(
    startOfMonth(new Date())
  );

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError("");
        const data = await fetchAPI("/available-dates");
        const normalized = Array.isArray(data)
          ? normalizeDates(data as (string | { date: string; free_slots?: number })[])
          : normalizeDates(
              (data as { dates?: (string | { date: string; free_slots?: number })[] })?.dates ?? []
            );
        setDates(normalized);
        if (normalized.length > 0) {
          setSelectedDate(normalized[0].date);
          setCurrentMonth(
            startOfMonth(new Date(`${normalized[0].date}T00:00:00`))
          );
        }
      } catch {
        setError("Не удалось загрузить доступные даты.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const availableDatesMap = useMemo(() => {
    const map = new Map<string, { free_slots?: number }>();
    dates.forEach((item) => map.set(item.date, { free_slots: item.free_slots }));
    return map;
  }, [dates]);

  const calendarDays = useMemo(
    () => getCalendarDays(currentMonth, availableDatesMap),
    [currentMonth, availableDatesMap]
  );

  return {
    dates,
    loading,
    error,
    selectedDate,
    setSelectedDate,
    currentMonth,
    setCurrentMonth,
    availableDatesMap,
    calendarDays,
  };
}

export function useSlots(
  selectedDate: string,
  slotsSectionRef: React.RefObject<HTMLDivElement | null>
) {
  const [slots, setSlots] = useState<Slot[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedSlotId, setSelectedSlotId] = useState<number | null>(null);

  // На мобильном автоскроллим к секции слотов при ВЫБОРЕ даты пользователем,
  // но НЕ при первой загрузке (когда useDates выставляет первую доступную
  // дату автоматически — иначе пользователь сразу проматывается мимо календаря).
  const isFirstDateLoad = useRef(true);

  useEffect(() => {
    if (!selectedDate) {
      setSlots([]);
      setSelectedSlotId(null);
      return;
    }

    const shouldScroll = !isFirstDateLoad.current;
    isFirstDateLoad.current = false;

    async function load() {
      try {
        setLoading(true);
        setSelectedSlotId(null);
        const data = await fetchAPI(`/available-slots?date=${selectedDate}`);
        setSlots(Array.isArray(data) ? (data as Slot[]) : []);

        if (
          shouldScroll &&
          typeof window !== "undefined" &&
          window.innerWidth < 1024
        ) {
          setTimeout(() => {
            slotsSectionRef.current?.scrollIntoView({
              behavior: "smooth",
              block: "start",
            });
          }, 120);
        }
      } catch {
        setSlots([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [selectedDate, slotsSectionRef]);

  const selectedSlot = useMemo(
    () => slots.find((s) => s.id === selectedSlotId) ?? null,
    [slots, selectedSlotId]
  );

  async function refreshSlots() {
    if (!selectedDate) return;
    try {
      const data = await fetchAPI(`/available-slots?date=${selectedDate}`);
      setSlots(Array.isArray(data) ? (data as Slot[]) : []);
    } catch {
      // silent
    }
  }

  return { slots, loading, selectedSlotId, setSelectedSlotId, selectedSlot, refreshSlots };
}
