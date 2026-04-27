import { Stethoscope, ArrowRight } from "lucide-react";
import Image from "next/image";

import { fetchAPI } from "../../lib/api";
import type { DoctorProfile } from "../../lib/types";
import { absoluteMediaUrl } from "../../lib/url";
import MobileMenu from "./MobileMenu";

export default async function Header() {
  const doctor = (await fetchAPI("/profile")) as DoctorProfile | null;

  const links = [
    { href: "/", label: "Главная" },
    { href: "/about", label: "О враче" },
    { href: "/booking", label: "Онлайн-запись" },
    { href: "/office", label: "Очный приём" },
    { href: "/contacts", label: "Контакты" },
  ];

  const avatarSrc = absoluteMediaUrl(
    doctor?.header_avatar_url || doctor?.photo_url || null
  );

  return (
    <header className="sticky top-0 z-30 border-b border-neutral-100 bg-neutral-0/95 backdrop-blur-sm transition-all duration-300 shadow-sm">
      <div className="container flex items-center justify-between py-4">
        {/* Logo/Brand */}
        <a href="/" className="flex min-w-0 items-center gap-3 hover:opacity-80 transition-opacity">
          {avatarSrc ? (
            <Image
              src={avatarSrc}
              alt={doctor?.full_name || "Врач"}
              width={40}
              height={40}
              className="h-10 w-10 shrink-0 rounded-lg object-cover shadow-sm"
            />
          ) : (
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary-100 text-primary-600 shadow-sm">
              <Stethoscope className="h-5 w-5" strokeWidth={2} />
            </div>
          )}

          <div className="min-w-0 hidden sm:block">
            <div className="truncate text-sm font-bold text-neutral-900">
              {doctor?.full_name || "Врач"}
            </div>
            <div className="text-xs text-neutral-500">врач-инфекционист</div>
          </div>
        </a>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-5 lg:gap-7">
          {links.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-neutral-600 transition-colors hover:text-primary-700"
            >
              {link.label}
            </a>
          ))}
        </nav>

        {/* Desktop CTA Button — на lg+, чтобы не давить ссылки на md */}
        <div className="hidden lg:block">
          <a href="/booking" className="btn-primary text-sm py-2 px-5">
            Записаться
            <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
          </a>
        </div>

        {/* Mobile Menu */}
        <MobileMenu fullName={doctor?.full_name} />
      </div>
    </header>
  );
}