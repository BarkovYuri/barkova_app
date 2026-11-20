/**
 * Файл .ics «Добавить в календарь» для записи на онлайн-разбор.
 * Работает в календарях iPhone, Android, Google и Outlook без сторонних сервисов.
 */

function toIcsUtc(date: Date): string {
  return date.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z");
}

function escapeIcs(text: string): string {
  return text.replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\n/g, "\\n");
}

export type CalendarEvent = {
  startsAt: string;
  durationMinutes: number;
  title: string;
  description: string;
  url: string;
};

export function buildIcs(event: CalendarEvent): string | null {
  const start = new Date(event.startsAt);
  if (Number.isNaN(start.getTime())) return null;
  const end = new Date(start.getTime() + event.durationMinutes * 60_000);
  const uid = `${toIcsUtc(start)}-${Math.random().toString(36).slice(2)}@doctor-barkova.ru`;

  return [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//doctor-barkova.ru//booking//RU",
    "CALSCALE:GREGORIAN",
    "BEGIN:VEVENT",
    `UID:${uid}`,
    `DTSTAMP:${toIcsUtc(new Date())}`,
    `DTSTART:${toIcsUtc(start)}`,
    `DTEND:${toIcsUtc(end)}`,
    `SUMMARY:${escapeIcs(event.title)}`,
    `DESCRIPTION:${escapeIcs(event.description)}`,
    `URL:${event.url}`,
    "BEGIN:VALARM",
    "TRIGGER:-PT1H",
    "ACTION:DISPLAY",
    `DESCRIPTION:${escapeIcs(event.title)}`,
    "END:VALARM",
    "END:VEVENT",
    "END:VCALENDAR",
    "",
  ].join("\r\n");
}

/** Минуты между началом и концом слота («10:00:00», «10:30:00»). */
export function slotDurationMinutes(startTime: string, endTime: string): number {
  const toMinutes = (value: string) => {
    const [h, m] = value.split(":").map(Number);
    return h * 60 + m;
  };
  const diff = toMinutes(endTime) - toMinutes(startTime);
  return diff > 0 ? diff : 30;
}

export function downloadIcs(content: string, filename: string): void {
  const blob = new Blob([content], { type: "text/calendar;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
