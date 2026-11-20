/**
 * Яндекс Метрика: номер счётчика и безопасные обёртки над ym().
 *
 * ID счётчика не секретный. Он задан значением по умолчанию, потому что
 * NEXT_PUBLIC_* переменные встраиваются при сборке, а CI их не передаёт.
 */
export const METRIKA_ID = Number(process.env.NEXT_PUBLIC_YANDEX_METRIKA_ID || 104693717);

/** Цели воронки записи. В Метрике заводятся как «JavaScript-событие» с этими идентификаторами. */
export type MetrikaGoal =
  | "booking_slot_selected"
  | "booking_vk_login"
  | "booking_vk_messages_allowed"
  | "booking_contact_phone"
  | "booking_submit"
  | "booking_success"
  | "booking_error"
  | "booking_open_vk_dialog";

type Ym = (id: number, method: string, ...args: unknown[]) => void;

function ym(): Ym | null {
  if (typeof window === "undefined" || !METRIKA_ID) return null;
  const fn = (window as unknown as { ym?: Ym }).ym;
  return typeof fn === "function" ? fn : null;
}

export function reachGoal(goal: MetrikaGoal, params?: Record<string, unknown>): void {
  try {
    ym()?.(METRIKA_ID, "reachGoal", goal, params);
  } catch {
    // Аналитика не должна ломать запись.
  }
}

export function trackPageView(url: string, referer: string): void {
  try {
    ym()?.(METRIKA_ID, "hit", url, { referer });
  } catch {
    // ignore
  }
}
