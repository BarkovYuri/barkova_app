/** Утилиты для текста статей: оглавление и время чтения. */

export type ArticleHeading = { id: string; text: string };

function plainHeading(raw: string): string {
  return raw
    .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1") // ссылки → текст
    .replace(/[*_`~]/g, "")
    .trim();
}

function slugify(text: string): string {
  const slug = text
    .toLowerCase()
    .replace(/ё/g, "е")
    .replace(/[^a-zа-я0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return slug || "section";
}

/** Заголовки второго уровня (## …) в порядке появления, с уникальными id. */
export function extractHeadings(markdown: string): ArticleHeading[] {
  const used = new Map<string, number>();
  const headings: ArticleHeading[] = [];
  let inCode = false;
  for (const line of markdown.split("\n")) {
    if (line.trim().startsWith("```")) inCode = !inCode;
    if (inCode) continue;
    const match = /^##\s+(.+?)\s*#*\s*$/.exec(line);
    if (!match) continue;
    const text = plainHeading(match[1]);
    const base = slugify(text);
    const count = used.get(base) ?? 0;
    used.set(base, count + 1);
    headings.push({ id: count ? `${base}-${count + 1}` : base, text });
  }
  return headings;
}

/** Минуты чтения при ~180 словах в минуту, не меньше одной. */
export function readingMinutes(markdown: string): number {
  const words = markdown.trim().split(/\s+/).filter(Boolean).length;
  return Math.max(1, Math.round(words / 180));
}
