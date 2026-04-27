/**
 * Безопасная вставка JSON-LD скрипта в head.
 * Используется для structured data (schema.org).
 *
 * Применение:
 *   <JsonLd data={{ "@context": "https://schema.org", "@type": "Physician", ... }} />
 */
export function JsonLd({ data }: { data: Record<string, unknown> }) {
  return (
    <script
      type="application/ld+json"
      // safe: данные у нас контролируемые, без user input
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(data).replace(/</g, "\\u003c"),
      }}
    />
  );
}
