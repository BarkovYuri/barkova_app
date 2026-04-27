/**
 * Тонкая декоративная горизонтальная черта с маленькой точкой по центру.
 * Используется между секциями на белом фоне — чтобы они визуально не сливались,
 * но при этом сайт оставался воздушным и спокойным.
 */
export function SectionDivider() {
  return (
    <div
      aria-hidden="true"
      className="container flex items-center justify-center gap-3"
    >
      <span className="h-px flex-1 bg-gradient-to-r from-transparent via-neutral-200 to-neutral-200" />
      <span className="flex h-2 w-2 rounded-full bg-primary-300" />
      <span className="h-px flex-1 bg-gradient-to-r from-neutral-200 via-neutral-200 to-transparent" />
    </div>
  );
}
