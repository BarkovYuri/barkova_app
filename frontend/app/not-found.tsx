import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight, Home, Stethoscope } from "lucide-react";

export const metadata: Metadata = {
  title: "Страница не найдена",
  description:
    "Запрашиваемая страница не существует или была перемещена. Вернитесь на главную или запишитесь на консультацию.",
  robots: { index: false, follow: false },
};

export default function NotFound() {
  return (
    <main
      id="main"
      className="min-h-screen bg-neutral-0 flex items-center justify-center"
    >
      <div className="container max-w-2xl text-center py-24">
        <span className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-100 text-primary-700">
          <Stethoscope className="h-7 w-7" strokeWidth={2} />
        </span>

        <p className="mt-8 text-sm font-semibold uppercase tracking-wider text-primary-700">
          404
        </p>
        <h1 className="mt-3 text-neutral-900">Такой страницы нет</h1>
        <p className="mt-5 text-base-large text-neutral-600">
          Возможно, вы перешли по устаревшей ссылке или страница была
          перемещена. Вы можете вернуться на главную или сразу записаться
          на консультацию.
        </p>

        <div className="mt-10 flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            href="/"
            className="button button-primary inline-flex items-center justify-center gap-2"
          >
            <Home className="h-4 w-4" strokeWidth={2.2} />
            На главную
          </Link>
          <Link
            href="/booking"
            className="button button-secondary inline-flex items-center justify-center gap-2"
          >
            Записаться
            <ArrowRight className="h-4 w-4" strokeWidth={2.2} />
          </Link>
        </div>
      </div>
    </main>
  );
}
