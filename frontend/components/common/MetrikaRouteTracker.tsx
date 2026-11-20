"use client";

import { usePathname, useSearchParams } from "next/navigation";
import { useEffect, useRef } from "react";

import { trackPageView } from "../../lib/metrika";

/**
 * Next.js меняет страницы без перезагрузки, а тег Метрики сам такие
 * переходы не считает: по документации Яндекса для SPA нужно вызывать
 * hit при каждой смене адреса. Первый просмотр отправляет init.
 */
export function MetrikaRouteTracker() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const previousUrl = useRef<string | null>(null);

  useEffect(() => {
    const url = window.location.href;
    if (previousUrl.current === null) {
      previousUrl.current = url;
      return;
    }
    if (previousUrl.current === url) return;
    trackPageView(url, previousUrl.current);
    previousUrl.current = url;
  }, [pathname, searchParams]);

  return null;
}
