"use client";

import { Map as MapIcon } from "lucide-react";
import { useState } from "react";

type Props = {
  src: string;
  title?: string;
  /** Опциональный адрес — рендерится в плейсхолдере под иконкой. */
  address?: string;
};

/**
 * Lazy-load Yandex Maps iframe.
 * До клика рендерим только лёгкий плейсхолдер с иконкой и текстом —
 * iframe не подгружается, не делает сетевые запросы, не съедает LCP.
 * После клика iframe монтируется в DOM, и пользователь видит карту.
 */
export function LazyYandexMap({ src, title = "Карта", address }: Props) {
  const [loaded, setLoaded] = useState(false);

  if (loaded) {
    return (
      <iframe
        src={src}
        title={title}
        loading="lazy"
        allowFullScreen
        className="w-full aspect-[16/10] sm:aspect-[16/9] rounded-2xl border border-neutral-200"
      />
    );
  }

  return (
    <button
      type="button"
      onClick={() => setLoaded(true)}
      className="group relative flex w-full aspect-[16/10] sm:aspect-[16/9] items-center justify-center rounded-2xl border border-neutral-200 bg-gradient-to-br from-primary-50 via-neutral-50 to-secondary-50 overflow-hidden hover:border-primary-300 transition-colors"
      aria-label="Загрузить карту"
    >
      {/* Декоративная сетка имитирующая карту */}
      <div
        aria-hidden
        className="absolute inset-0 opacity-30"
        style={{
          backgroundImage:
            "linear-gradient(var(--color-neutral-300) 1px, transparent 1px), linear-gradient(90deg, var(--color-neutral-300) 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
      />

      <div className="relative z-10 flex flex-col items-center gap-3 text-center px-4">
        <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-600 text-neutral-0 shadow-lg group-hover:scale-105 transition-transform">
          <MapIcon className="h-7 w-7" strokeWidth={2} />
        </span>
        <p className="text-sm font-semibold text-neutral-900">
          Показать карту
        </p>
        {address ? (
          <p className="max-w-md text-xs text-neutral-600">{address}</p>
        ) : null}
        <p className="text-xs text-neutral-500">Карта подгрузится по клику</p>
      </div>
    </button>
  );
}
