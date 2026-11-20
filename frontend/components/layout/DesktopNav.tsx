"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { NAV_LINKS, isActivePath } from "./navLinks";

export default function DesktopNav() {
  const pathname = usePathname() || "/";
  return (
    <nav aria-label="Основное меню" className="hidden lg:flex items-center gap-6 xl:gap-7">
      {NAV_LINKS.map((link) => {
        const active = isActivePath(pathname, link.href);
        return (
          <Link
            key={link.href}
            href={link.href}
            aria-current={active ? "page" : undefined}
            className={`whitespace-nowrap text-sm font-medium transition-colors hover:text-primary-700 ${
              active ? "text-primary-700" : "text-neutral-600"
            }`}
          >
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
