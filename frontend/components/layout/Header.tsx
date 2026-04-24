import { fetchAPI } from "../../lib/api";
import type { DoctorProfile } from "../../lib/types";
import MobileMenu from "./MobileMenu";

export default async function Header() {
  const doctor = (await fetchAPI("/profile")) as DoctorProfile | null;

  const links = [
    { href: "/", label: "Главная" },
    { href: "/about", label: "О враче" },
    { href: "/booking", label: "Онлайн-консультация" },
    { href: "/office", label: "Очный прием" },
    { href: "/contacts", label: "Контакты" },
  ];

  const avatarSrc = doctor?.header_avatar_url || doctor?.photo_url || null;

  return (
    <header className="sticky top-0 z-30 border-b border-sky-100/80 bg-white/90 backdrop-blur">
      <div className="relative mx-auto flex max-w-6xl items-center justify-between px-4 py-4 md:px-6">
        <a href="/" className="flex min-w-0 items-center gap-3">
          {avatarSrc ? (
            <img
              src={avatarSrc}
              alt={doctor?.full_name || "Врач"}
              className="h-10 w-10 shrink-0 rounded-2xl object-cover shadow-sm"
            />
          ) : (
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-sky-100 text-sky-700 shadow-sm">
              <span className="text-sm font-semibold">ЕИ</span>
            </div>
          )}

          <div className="min-w-0">
            <div className="truncate text-sm font-semibold text-gray-900 md:text-base">
              {doctor?.full_name || "Врач"}
            </div>
            <div className="text-xs text-gray-500">врач-инфекционист</div>
          </div>
        </a>

        <nav className="hidden items-center gap-6 md:flex">
          {links.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-gray-600 transition hover:text-sky-600"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="hidden md:block">
          <a
            href="/booking"
            className="rounded-2xl bg-sky-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-sky-700"
          >
            Онлайн-консультация
          </a>
        </div>

        <MobileMenu fullName={doctor?.full_name} />
      </div>
    </header>
  );
}