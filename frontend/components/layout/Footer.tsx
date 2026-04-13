export default function Footer() {
    return (
      <footer className="border-t border-gray-100 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-10 text-sm text-gray-500 md:flex-row md:items-center md:justify-between">
          <p>© 2026 Кабинет врача-инфекциониста</p>
  
          <div className="flex flex-wrap gap-4">
            <a href="/legal/offer" className="hover:text-sky-600">
              Оферта
            </a>
            <a href="/legal/privacy" className="hover:text-sky-600">
              Политика конфиденциальности
            </a>
            <a href="/legal/consent" className="hover:text-sky-600">
              Согласие на обработку данных
            </a>
          </div>
        </div>
      </footer>
    );
  }