"use client";

import { Menu, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { NAV_LINKS, isActivePath } from "./navLinks";

type MobileMenuProps = {
  fullName?: string;
};

export default function MobileMenu({ fullName }: MobileMenuProps) {
  const [open, setOpen] = useState(false);
  const [openedAt, setOpenedAt] = useState<string | null>(null);
  const pathname = usePathname() || "/";
  const rootRef = useRef<HTMLDivElement | null>(null);

  // Меню закрывается при переходе на другую страницу.
  const isOpen = open && openedAt === pathname;

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    const onPointer = (e: PointerEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("keydown", onKey);
    document.addEventListener("pointerdown", onPointer);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("pointerdown", onPointer);
    };
  }, [isOpen]);

  return (
    <div ref={rootRef} className="lg:hidden">
      <button
        type="button"
        onClick={() => {
          setOpenedAt(pathname);
          setOpen((prev) => !(prev && openedAt === pathname));
        }}
        aria-label={isOpen ? "Закрыть меню" : "Открыть меню"}
        aria-expanded={isOpen}
        aria-controls="mobile-menu"
        className="flex h-11 w-11 items-center justify-center rounded-2xl border border-neutral-200 bg-neutral-0 text-neutral-700 shadow-sm transition hover:bg-neutral-50 hover:border-primary-300"
      >
        {isOpen ? <X className="h-5 w-5" strokeWidth={2.25} /> : <Menu className="h-5 w-5" strokeWidth={2.25} />}
      </button>

      {isOpen ? (
        <div
          id="mobile-menu"
          className="absolute left-4 right-4 top-[72px] z-40 rounded-3xl border border-primary-100 bg-neutral-0 p-5 shadow-2xl shadow-primary-200/40 animate-fade-in sm:left-auto sm:w-80"
        >
          <div className="border-b border-neutral-100 pb-4">
            <div className="text-ui-label uppercase text-neutral-500">Врач-инфекционист</div>
            <div className="mt-1 text-base font-semibold font-heading text-neutral-900">
              {fullName || "Врач-инфекционист"}
            </div>
          </div>

          <nav aria-label="Мобильное меню" className="mt-4 flex flex-col gap-1">
            {NAV_LINKS.map((link) => {
              const active = isActivePath(pathname, link.href);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setOpen(false)}
                  aria-current={active ? "page" : undefined}
                  className={`rounded-xl px-4 py-3 font-medium transition hover:bg-primary-50 hover:text-primary-700 ${
                    active ? "bg-primary-50 text-primary-700" : "text-neutral-700"
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </nav>

          <Link href="/booking" onClick={() => setOpen(false)} className="btn-primary mt-5 w-full">
            Записаться на онлайн-разбор
          </Link>
        </div>
      ) : null}
    </div>
  );
}
