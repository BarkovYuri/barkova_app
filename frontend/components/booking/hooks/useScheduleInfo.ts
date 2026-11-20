"use client";

import { useEffect, useState } from "react";

import { fetchAPI } from "../../../lib/api";
import type { ScheduleInfo } from "../../../lib/types";

let cached: ScheduleInfo | null = null;

/** Часовой пояс расписания с бэкенда: подпись «по времени Томска (МСК+4)». */
export function useScheduleInfo(): ScheduleInfo | null {
  const [info, setInfo] = useState<ScheduleInfo | null>(cached);

  useEffect(() => {
    if (cached) return;
    let cancelled = false;
    fetchAPI("/schedule-info")
      .then((data) => {
        if (cancelled || !data) return;
        cached = data as ScheduleInfo;
        setInfo(cached);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  return info;
}

/**
 * Время слота в часовом поясе пациента, если он отличается от пояса
 * расписания. Иначе null — подпись «у вас …» не нужна.
 */
export function localTimeHint(startsAt: string | undefined, scheduleTime: string): string | null {
  if (!startsAt) return null;
  const date = new Date(startsAt);
  if (Number.isNaN(date.getTime())) return null;
  const local = new Intl.DateTimeFormat("ru-RU", { hour: "2-digit", minute: "2-digit" }).format(date);
  return local === scheduleTime.slice(0, 5) ? null : local;
}
