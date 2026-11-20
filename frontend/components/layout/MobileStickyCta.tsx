"use client";

import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

/**
 * Кнопка записи, закреплённая внизу экрана на телефонах. На самой странице
 * записи не нужна. В подвале под неё оставлен отступ, чтобы она ничего
 * не перекрывала.
 */
export default function MobileStickyCta() {
  const pathname = usePathname() || "/";
  if (pathname.startsWith("/booking")) return null;
  return (
    <div className="fixed inset-x-0 bottom-0 z-30 border-t border-neutral-200 bg-neutral-0/95 px-4 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] backdrop-blur-sm sm:hidden">
      <Link href="/booking" className="btn-primary w-full justify-center">
        Записаться на онлайн-разбор
        <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
      </Link>
    </div>
  );
}
