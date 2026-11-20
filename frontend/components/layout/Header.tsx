import { Stethoscope, ArrowRight } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

import { fetchAPI } from "../../lib/api";
import type { DoctorProfile } from "../../lib/types";
import { absoluteMediaUrl } from "../../lib/url";
import DesktopNav from "./DesktopNav";
import MobileMenu from "./MobileMenu";

export default async function Header() {
  // Шапка есть на каждой странице: сбой API не должен ронять весь сайт.
  const doctor = (await fetchAPI("/profile").catch(() => null)) as DoctorProfile | null;

  const avatarSrc = absoluteMediaUrl(
    doctor?.header_avatar_url || doctor?.photo_url || null
  );

  return (
    <header className="sticky top-0 z-30 border-b border-neutral-100 bg-neutral-0/95 backdrop-blur-sm transition-all duration-300 shadow-sm">
      <div className="container flex items-center justify-between gap-4 py-4">
        {/* Logo/Brand */}
        <Link href="/" className="flex min-w-0 items-center gap-3 hover:opacity-80 transition-opacity">
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
        </Link>

        <DesktopNav />

        <div className="flex shrink-0 items-center gap-3">
          {/* Кнопка записи — с 640px. На телефоне её заменяет закреплённая
              кнопка внизу экрана. */}
          <Link href="/booking" className="btn-primary hidden text-sm py-2 px-5 sm:inline-flex">
            Записаться
            <ArrowRight className="h-4 w-4" strokeWidth={2.5} />
          </Link>

          <MobileMenu fullName={doctor?.full_name} />
        </div>
      </div>
    </header>
  );
}