import Image from "next/image";

import type { Credential } from "../../lib/types";
import { absoluteMediaUrl } from "../../lib/url";

/** Дипломы и сертификаты. Секция не выводится, пока документы не добавлены. */
export function Credentials({ items }: { items: Credential[] }) {
  if (items.length === 0) return null;
  return (
    <section className="py-16 md:py-20">
      <div className="container">
        <p className="chip">Документы</p>
        <h2 className="mt-5 text-neutral-900">Образование и сертификаты</h2>
        <div className="mt-10 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {items.map((item) => {
            const full = absoluteMediaUrl(item.image_url);
            const thumb = absoluteMediaUrl(item.thumb_url || item.image_url);
            return (
              <a
                key={item.id}
                href={full || "#"}
                target="_blank"
                rel="noopener noreferrer"
                className="group overflow-hidden rounded-2xl border border-neutral-200 bg-neutral-0 transition-all hover:-translate-y-0.5 hover:border-primary-300 hover:shadow-card-hover"
              >
                <div className="relative aspect-[4/3] bg-neutral-100">
                  {thumb ? (
                    <Image src={thumb} alt={item.title} fill sizes="(max-width: 640px) 50vw, 25vw" className="object-cover" />
                  ) : null}
                </div>
                <div className="p-4">
                  <p className="text-sm font-semibold leading-snug text-neutral-900">{item.title}</p>
                  {item.year ? <p className="mt-1 text-xs text-neutral-500">{item.year}</p> : null}
                </div>
              </a>
            );
          })}
        </div>
      </div>
    </section>
  );
}
