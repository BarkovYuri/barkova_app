/**
 * Российская маска телефона: +7 (XXX) XXX-XX-XX
 *
 * Алгоритм:
 *  1. Берём из ввода только цифры.
 *  2. Если первая цифра 7 или 8 — отрезаем (т.к. префикс +7 жёсткий).
 *  3. Берём максимум 10 оставшихся цифр.
 *  4. Подставляем в шаблон.
 *
 * Примеры ввода → результат:
 *  ""              → ""
 *  "9"             → "+7 (9"
 *  "9001234567"    → "+7 (900) 123-45-67"
 *  "+7 9001234567" → "+7 (900) 123-45-67"
 *  "8 (900) 1234567" → "+7 (900) 123-45-67"
 */

export function formatPhone(value: string): string {
  // Только цифры
  let digits = value.replace(/\D/g, "");

  // Срезаем 7 / 8 если стоит впереди (это префикс страны)
  if (digits.startsWith("7") || digits.startsWith("8")) {
    digits = digits.slice(1);
  }

  digits = digits.slice(0, 10);

  if (digits.length === 0) return "";

  let out = "+7";
  if (digits.length > 0) out += ` (${digits.slice(0, 3)}`;
  if (digits.length >= 4) out += `) ${digits.slice(3, 6)}`;
  if (digits.length >= 7) out += `-${digits.slice(6, 8)}`;
  if (digits.length >= 9) out += `-${digits.slice(8, 10)}`;

  return out;
}

/**
 * Считает сколько цифр введено (без префикса +7).
 * Используется для валидации: 10 = полностью введён.
 */
export function phoneDigitsCount(value: string): number {
  let digits = value.replace(/\D/g, "");
  if (digits.startsWith("7") || digits.startsWith("8")) {
    digits = digits.slice(1);
  }
  return Math.min(digits.length, 10);
}

/**
 * Проверяет валидность: введено ровно 10 цифр.
 */
export function isPhoneValid(value: string): boolean {
  return phoneDigitsCount(value) === 10;
}
