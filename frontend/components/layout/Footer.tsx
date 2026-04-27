import { Stethoscope, Heart } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-neutral-200 bg-neutral-50">
      <div className="container py-16">
        <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-4">
          {/* Column 1: Branding */}
          <div>
            <div className="flex items-center gap-2 text-neutral-900">
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-100 text-primary-700">
                <Stethoscope className="h-5 w-5" strokeWidth={2} />
              </span>
              <h3 className="text-sm font-bold tracking-tight">
                Кабинет врача
              </h3>
            </div>
            <p className="mt-4 text-sm text-neutral-600 leading-relaxed">
              Профессиональная медицинская помощь врача-инфекциониста.
              Очный приём и телемедицина.
            </p>
          </div>

          {/* Column 2: Quick Links */}
          <div>
            <h4 className="text-ui-label text-neutral-500 uppercase">Меню</h4>
            <ul className="mt-5 space-y-3 text-sm">
              <li>
                <a
                  href="/"
                  className="text-neutral-700 hover:text-primary-700 transition-colors"
                >
                  Главная
                </a>
              </li>
              <li>
                <a
                  href="/about"
                  className="text-neutral-700 hover:text-primary-700 transition-colors"
                >
                  О враче
                </a>
              </li>
              <li>
                <a
                  href="/booking"
                  className="text-neutral-700 hover:text-primary-700 transition-colors"
                >
                  Запись
                </a>
              </li>
              <li>
                <a
                  href="/contacts"
                  className="text-neutral-700 hover:text-primary-700 transition-colors"
                >
                  Контакты
                </a>
              </li>
            </ul>
          </div>

          {/* Column 3: Legal */}
          <div>
            <h4 className="text-ui-label text-neutral-500 uppercase">
              Информация
            </h4>
            <ul className="mt-5 space-y-3 text-sm">
              <li>
                <a
                  href="/legal/offer"
                  className="text-neutral-700 hover:text-primary-700 transition-colors"
                >
                  Оферта
                </a>
              </li>
              <li>
                <a
                  href="/legal/privacy"
                  className="text-neutral-700 hover:text-primary-700 transition-colors"
                >
                  Политика конфиденциальности
                </a>
              </li>
              <li>
                <a
                  href="/legal/consent"
                  className="text-neutral-700 hover:text-primary-700 transition-colors"
                >
                  Согласие на обработку
                </a>
              </li>
            </ul>
          </div>

          {/* Column 4: Contact */}
          <div>
            <h4 className="text-ui-label text-neutral-500 uppercase">Контакт</h4>
            <div className="mt-5 space-y-4 text-sm">
              <p className="text-neutral-700 leading-relaxed">
                Готовы начать? Запишитесь на консультацию уже сегодня.
              </p>
              <a href="/booking" className="btn-primary text-sm py-3 px-5">
                Записаться
              </a>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-neutral-200 mt-12 pt-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 text-xs text-neutral-500">
            <p>© 2026 Кабинет врача-инфекциониста. Все права защищены.</p>
            <p className="inline-flex items-center gap-1.5">
              Сделано с
              <Heart
                className="h-3.5 w-3.5 text-accent-500 fill-accent-500"
                strokeWidth={2}
              />
              для вашего здоровья
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
