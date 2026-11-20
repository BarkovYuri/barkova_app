/**
 * Заглавная только первая буква: «Пятница, 20 ноября».
 * CSS `capitalize` делает заглавной каждое слово («20 Ноября», «2026 Г.»),
 * а в русском так не пишут.
 */
export function capitalizeFirst(value: string | null | undefined): string {
  if (!value) return "";
  return value.charAt(0).toLocaleUpperCase("ru-RU") + value.slice(1);
}
