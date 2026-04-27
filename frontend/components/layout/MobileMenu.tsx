"use client";

import { Menu, X } from "lucide-react";
import { useState } from "react";

type MobileMenuProps = {
  fullName?: string;
};

export default function MobileMenu({ fullName }: MobileMenuProps) {
  const [open, setOpen] = useState(false);

  const links = [
    { href: "/", label: "Главная" },
    { href: "/about", label: "О враче" },
    { href: "/booking", label: "Онлайн-консультация" },
    { href: "/office", label: "Очный приём" },
    { href: "/contacts", label: "Контакты" },
  ];

  return (
    <div className="md:hidden">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        aria-label={open ? "Закрыть меню" : "Открыть меню"}
        className="flex h-11 w-11 items-center justify-center rounded-2xl border border-neutral-200 bg-neutral-0 text-neutral-700 shadow-sm transition hover:bg-neutral-50 hover:border-primary-300"
      >
        {open ? (
          <X className="h-5 w-5" strokeWidth={2.25} />
        ) : (
          <Menu className="h-5 w-5" strokeWidth={2.25} />
        )}
      </button>

      {open ? (
        <div className="absolute left-4 right-4 top-[72px] z-40 rounded-3xl border border-primary-100 bg-neutral-0 p-5 shadow-2xl shadow-primary-200/40 animate-fade-in">
          <div className="border-b border-neutral-100 pb-4">
            <div className="text-ui-label uppercase text-neutral-500">Врач</div>
            <div className="mt-1 text-base font-semibold font-heading text-neutral-900">
              {fullName || "Врач-инфекционист"}
            </div>
          </div>

          <nav className="mt-4 flex flex-col gap-1">
            {links.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className="rounded-xl px-4 py-3 text-neutral-700 font-medium transition hover:bg-primary-50 hover:text-primary-700"
              >
                {link.label}
              </a>
            ))}
          </nav>

          <a
            href="/booking"
            onClick={() => setOpen(false)}
            className="btn-primary mt-5 w-full"
          >
            Записаться на онлайн-консультацию
          </a>
        </div>
      ) : null}
    </div>
  );
}
