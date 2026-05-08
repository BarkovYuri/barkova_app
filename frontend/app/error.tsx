"use client";

import { useEffect } from "react";
import Link from "next/link";
import { AlertTriangle, Home, RotateCw } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("App error boundary caught:", error);
  }, [error]);

  return (
    <main
      id="main"
      className="min-h-screen bg-neutral-0 flex items-center justify-center"
    >
      <div className="container max-w-2xl text-center py-24">
        <span className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-error-100 text-error-700">
          <AlertTriangle className="h-7 w-7" strokeWidth={2} />
        </span>

        <h1 className="mt-8 text-neutral-900">Что-то пошло не так</h1>
        <p className="mt-5 text-base-large text-neutral-600">
          Произошла временная ошибка. Попробуйте обновить страницу.
          Если проблема повторится — напишите нам, мы поможем записаться вручную.
        </p>

        {error.digest ? (
          <p className="mt-3 text-xs text-neutral-400">Код ошибки: {error.digest}</p>
        ) : null}

        <div className="mt-10 flex flex-col sm:flex-row gap-3 justify-center">
          <button
            type="button"
            onClick={reset}
            className="button button-primary inline-flex items-center justify-center gap-2"
          >
            <RotateCw className="h-4 w-4" strokeWidth={2.2} />
            Попробовать снова
          </button>
          <Link
            href="/"
            className="button button-secondary inline-flex items-center justify-center gap-2"
          >
            <Home className="h-4 w-4" strokeWidth={2.2} />
            На главную
          </Link>
        </div>
      </div>
    </main>
  );
}
