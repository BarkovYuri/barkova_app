/** Пункты меню — один источник для шапки, мобильного меню и подвала. */
export const NAV_LINKS = [
  { href: "/", label: "Главная" },
  { href: "/about", label: "О враче" },
  { href: "/booking", label: "Онлайн-разбор" },
  { href: "/office", label: "Очный приём" },
  { href: "/blog", label: "Блог" },
  { href: "/contacts", label: "Контакты" },
] as const;

export function isActivePath(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}
