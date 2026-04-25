export default function Footer() {
  return (
    <footer className="border-t border-neutral-200 bg-neutral-50">
      <div className="container section-vertical-spacing py-12">
        <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-4">
          {/* Column 1: Branding */}
          <div>
            <h3 className="text-sm font-bold text-neutral-900">
              🏥 Кабинет врача
            </h3>
            <p className="mt-3 text-sm text-neutral-600">
              Профессиональная медицинская помощь врача-инфекциониста
            </p>
          </div>

          {/* Column 2: Quick Links */}
          <div>
            <h4 className="text-sm font-bold text-neutral-900 uppercase tracking-wider">
              Меню
            </h4>
            <ul className="mt-4 space-y-2 text-sm">
              <li>
                <a
                  href="/"
                  className="text-neutral-600 hover:text-primary-600 transition"
                >
                  Главная
                </a>
              </li>
              <li>
                <a
                  href="/about"
                  className="text-neutral-600 hover:text-primary-600 transition"
                >
                  О враче
                </a>
              </li>
              <li>
                <a
                  href="/booking"
                  className="text-neutral-600 hover:text-primary-600 transition"
                >
                  Запись
                </a>
              </li>
              <li>
                <a
                  href="/contacts"
                  className="text-neutral-600 hover:text-primary-600 transition"
                >
                  Контакты
                </a>
              </li>
            </ul>
          </div>

          {/* Column 3: Legal */}
          <div>
            <h4 className="text-sm font-bold text-neutral-900 uppercase tracking-wider">
              Информация
            </h4>
            <ul className="mt-4 space-y-2 text-sm">
              <li>
                <a
                  href="/legal/offer"
                  className="text-neutral-600 hover:text-primary-600 transition"
                >
                  Оферта
                </a>
              </li>
              <li>
                <a
                  href="/legal/privacy"
                  className="text-neutral-600 hover:text-primary-600 transition"
                >
                  Политика конфиденциальности
                </a>
              </li>
              <li>
                <a
                  href="/legal/consent"
                  className="text-neutral-600 hover:text-primary-600 transition"
                >
                  Согласие на обработку
                </a>
              </li>
            </ul>
          </div>

          {/* Column 4: Contact */}
          <div>
            <h4 className="text-sm font-bold text-neutral-900 uppercase tracking-wider">
              Контакт
            </h4>
            <div className="mt-4 space-y-3 text-sm">
              <p className="text-neutral-600">
                Готовы начать? Запишитесь на консультацию уже сегодня.
              </p>
              <a href="/booking" className="btn-primary text-xs py-2 px-4 inline-block">
                Записаться
              </a>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-neutral-200 mt-8 pt-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 text-sm text-neutral-600">
            <p>© 2026 Кабинет врача-инфекциониста. Все права защищены.</p>
            <p>Разработано с ❤️ для вашего здоровья</p>
          </div>
        </div>
      </div>
    </footer>
  );
}