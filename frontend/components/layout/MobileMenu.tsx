"use client";

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
    { href: "/office", label: "Очный прием" },
    { href: "/contacts", label: "Контакты" },
  ];

  return (
    <div className="md:hidden">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        aria-label="Открыть меню"
        className="flex h-11 w-11 items-center justify-center rounded-2xl border border-gray-200 bg-white text-gray-700 shadow-sm transition hover:bg-gray-50"
      >
        <svg
          viewBox="0 0 24 24"
          className="h-5 w-5"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        >
          {open ? (
            <path d="M6 6l12 12M18 6L6 18" />
          ) : (
            <>
              <path d="M4 7h16" />
              <path d="M4 12h16" />
              <path d="M4 17h16" />
            </>
          )}
        </svg>
      </button>

      {open ? (
        <div className="absolute left-4 right-4 top-[72px] z-40 rounded-3xl border border-sky-100 bg-white p-5 shadow-2xl shadow-sky-100/60">
          <div className="border-b border-gray-100 pb-4">
            <div className="text-sm text-gray-500">Врач</div>
            <div className="mt-1 text-base font-semibold text-gray-900">
              {fullName || "Врач-инфекционист"}
            </div>
          </div>

          <nav className="mt-4 flex flex-col">
            {links.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className="rounded-2xl px-4 py-3 text-gray-700 transition hover:bg-sky-50 hover:text-sky-700"
              >
                {link.label}
              </a>
            ))}
          </nav>

          <a
            href="/booking"
            onClick={() => setOpen(false)}
            className="mt-4 flex justify-center rounded-2xl bg-sky-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-sky-700"
          >
            Записаться на онлайн-консультацию
          </a>
        </div>
      ) : null}
    </div>
  );
}