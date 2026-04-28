/**
 * Dev mock: возвращает заглушки для всех GET-эндпоинтов когда
 * NEXT_PUBLIC_USE_MOCK=1 / USE_MOCK=1. Нужен только чтобы посмотреть UI
 * локально без поднятия Django.
 */

const DOCTOR = {
  id: 1,
  full_name: "Баркова Елена Игоревна",
  photo: null,
  photo_url:
    "https://doctor-barkova.ru/media/doctor/YJN0eH_n-ps.jpg",
  header_avatar: null,
  header_avatar_url:
    "https://doctor-barkova.ru/media/doctor/header/2qVGTsd9ibk.jpg",
  description:
    "Помогаю взрослым и детям с инфекционными заболеваниями: от диагностики до длительного сопровождения. Работаю с гепатитами, ВИЧ, инфекциями, передающимися клещами, и постковидными состояниями. Объясняю простым языком и составляю чёткий план действий.",
  education:
    "Инфекционные болезни\nВирусолог\nБактериолог",
  experience_years: 3,
  prodoktorov_url:
    "https://prodoctorov.ru/tomsk/vrach/1219367-barkova/",
  address: "Медика, Советская улица, 86, Томск, 634034",
  email: "dr.barkova@mail.ru",
  phone: "+7 (999) 000-00-00",
  instagram_url: "https://www.instagram.com/dr.barkova_/",
  dzen_url: "https://dzen.ru/id/685d334b3656fb268cbd2e13",
  vk_url: "https://vk.com/dr.barkova",
  yandex_maps_embed_url:
    "https://yandex.ru/map-widget/v1/org/medika/227016608651/?ll=84.954016%2C56.461370&z=14",
  updated_at: new Date().toISOString(),
};

function todayPlus(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

const AVAILABLE_DATES = Array.from({ length: 14 }, (_, i) => ({
  date: todayPlus(i + 1),
  free_slots: ((i * 3 + 2) % 8) + 1,
})).filter((_, idx) => idx % 2 !== 0);

const SLOTS_BY_DATE: Record<string, Array<{
  id: number;
  date: string;
  start_time: string;
  end_time: string;
  is_active: boolean;
  is_booked: boolean;
}>> = {};

AVAILABLE_DATES.forEach((d, i) => {
  SLOTS_BY_DATE[d.date] = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
    .slice(0, d.free_slots)
    .map((time, j) => {
      const [h, m] = time.split(":").map(Number);
      const endH = h + 1;
      return {
        id: i * 100 + j + 1,
        date: d.date,
        start_time: `${time}:00`,
        end_time: `${String(endH).padStart(2, "0")}:${String(m).padStart(
          2,
          "0"
        )}:00`,
        is_active: true,
        is_booked: false,
      };
    });
});

const LEGAL = [
  {
    id: 1,
    doc_type: "offer",
    title: "Публичная оферта",
    content:
      "1. Общие положения\n\nНастоящая оферта определяет условия оказания услуг онлайн-консультации.\n\n2. Предмет договора\n\nИсполнитель оказывает услуги медицинской консультации в формате онлайн.\n\n(Это демо-текст для локального просмотра.)",
    version: "1.0",
    is_active: true,
  },
  {
    id: 2,
    doc_type: "privacy",
    title: "Политика конфиденциальности",
    content:
      "Мы обрабатываем персональные данные в соответствии с 152-ФЗ.\n\n(Это демо-текст для локального просмотра.)",
    version: "1.0",
    is_active: true,
  },
  {
    id: 3,
    doc_type: "consent",
    title: "Согласие на обработку персональных данных",
    content:
      "Я даю согласие на обработку моих персональных данных в целях оказания медицинских услуг.\n\n(Это демо-текст для локального просмотра.)",
    version: "1.0",
    is_active: true,
  },
];

export function tryMockResponse(
  endpoint: string,
  method: string = "GET"
): unknown | undefined {
  // ----- POST endpoints -----
  if (method === "POST") {
    // Создание заявки
    if (endpoint.startsWith("/appointments/") && !endpoint.includes("/")) {
      // редко попадаем сюда, ниже общий matcher
    }

    // Telegram prelink: создаёт токен и bot_url
    if (endpoint.startsWith("/appointments/telegram/prelink")) {
      return {
        token: "mock-telegram-token-" + Math.random().toString(36).slice(2),
        bot_url: "#",
      };
    }

    // VK prelink-ы / actions
    if (endpoint.startsWith("/appointments/vk/")) {
      return { ok: true };
    }

    // Создание заявки (POST /appointments/, /appointments/quick/)
    if (
      endpoint === "/appointments/" ||
      endpoint === "/appointments/quick/"
    ) {
      return {
        id: 1,
        status: "new",
        slot: { id: 1, date: todayPlus(1), start_time: "10:00:00" },
        name: "Тестовая запись",
      };
    }

    // По умолчанию возвращаем «ок» чтобы клиент не падал
    return { ok: true };
  }

  // ----- GET endpoints -----

  // /profile/
  if (endpoint.startsWith("/profile")) return DOCTOR;

  // /blocks/
  if (endpoint.startsWith("/blocks")) {
    return [
      { id: 1, key: "hero.subtitle", title: "Подзаголовок hero", content: "Помогаю взрослым и детям с инфекционными заболеваниями: от диагностики до длительного сопровождения.", updated_at: "" },
      { id: 2, key: "hero.specialty_chip", title: "", content: "Врач-инфекционист", updated_at: "" },
      { id: 3, key: "services.section_chip", title: "", content: "Услуги", updated_at: "" },
      { id: 4, key: "services.section_title", title: "", content: "Как я помогаю", updated_at: "" },
      { id: 5, key: "how_it_works.section_chip", title: "", content: "Процесс", updated_at: "" },
      { id: 6, key: "how_it_works.section_title", title: "", content: "Как это работает", updated_at: "" },
      { id: 7, key: "how_it_works.section_subtitle", title: "", content: "От первой записи до получения рекомендаций — всё прозрачно и предсказуемо", updated_at: "" },
      { id: 8, key: "faq.section_chip", title: "", content: "Частые вопросы", updated_at: "" },
      { id: 9, key: "faq.section_title", title: "", content: "Что обычно спрашивают", updated_at: "" },
      { id: 10, key: "faq.section_subtitle", title: "", content: "Если ваш вопрос не нашёлся ниже — напишите в Telegram или VK, отвечу лично.", updated_at: "" },
      { id: 11, key: "cta.home.title", title: "", content: "Готовы начать?", updated_at: "" },
      { id: 12, key: "cta.home.text", title: "", content: "Запишитесь на консультацию уже сегодня и получите профессиональную помощь", updated_at: "" },
      { id: 13, key: "cta.home.button", title: "", content: "Записаться сейчас", updated_at: "" },
      { id: 14, key: "cta.about.title", title: "", content: "Готовы получить помощь?", updated_at: "" },
      { id: 15, key: "cta.about.text", title: "", content: "Запишитесь на консультацию и начните путь к выздоровлению", updated_at: "" },
      { id: 16, key: "approach.section_chip", title: "", content: "Подход к работе", updated_at: "" },
      { id: 17, key: "approach.section_title", title: "", content: "Спокойно, понятно и по делу", updated_at: "" },
    ];
  }

  // /services/
  if (endpoint.startsWith("/services")) {
    return [
      { id: 1, icon: "clipboard_list", title: "Онлайн-консультация", description: "Быстрая запись через сайт. Выберите дату, время — и приходите на удобный вам формат.", cta_text: "Записаться", cta_link: "/booking", order: 0 },
      { id: 2, icon: "hospital", title: "Очный приём", description: "Личный приём в кабинете. Полная диагностика и индивидуально подобранное лечение.", cta_text: "Записаться", cta_link: "/booking", order: 1 },
      { id: 3, icon: "pill", title: "Рекомендации", description: "Профессиональные советы и назначения, основанные на актуальных клинических протоколах.", cta_text: "Записаться", cta_link: "/booking", order: 2 },
    ];
  }

  // /how-it-works/
  if (endpoint.startsWith("/how-it-works")) {
    return [
      { id: 1, icon: "calendar_days", title: "Выбор даты", description: "Откройте календарь и выберите удобный день и время. Все свободные слоты подсвечены.", order: 0 },
      { id: 2, icon: "message_square", title: "Контактные данные", description: "Оставьте имя и телефон, опишите вопрос. Подключите Telegram или VK для уведомлений.", order: 1 },
      { id: 3, icon: "check_check", title: "Подтверждение", description: "В мессенджер придёт сообщение с подтверждением и ссылкой на видеоконсультацию.", order: 2 },
      { id: 4, icon: "stethoscope", title: "Приём", description: "В назначенное время — выходите на связь. Получаете план обследований и рекомендации.", order: 3 },
    ];
  }

  // /faq/
  if (endpoint.startsWith("/faq")) {
    return [
      { id: 1, question: "Сколько длится онлайн-консультация?", answer: "Базовый приём — 30 минут.", order: 0 },
      { id: 2, question: "Как проходит видеоконсультация?", answer: "За 10–15 минут до приёма в Telegram или VK придёт ссылка на видеовстречу.", order: 1 },
      { id: 3, question: "Что подготовить к приёму?", answer: "Свежие анализы, список текущих лекарств, краткую хронологию симптомов.", order: 2 },
      { id: 4, question: "Можно ли получить рецепт после онлайн-приёма?", answer: "После онлайн-консультации врач может оформить рекомендации и направления.", order: 3 },
      { id: 5, question: "Сохраняются ли мои данные в тайне?", answer: "Да. Все ваши данные обрабатываются в соответствии с 152-ФЗ.", order: 4 },
      { id: 6, question: "Что делать, если стало хуже после консультации?", answer: "Если состояние ухудшилось — напишите в тот же мессенджер, где подтверждали запись.", order: 5 },
    ];
  }

  // /approach/
  if (endpoint.startsWith("/approach")) {
    return [
      { id: 1, icon: "clipboard_list", title: "Разбор жалоб", description: "Детальный анализ симптомов, анализов и уже проведённых обследований", order: 0 },
      { id: 2, icon: "list_checks", title: "Структурированный план", description: "Пациент получает ясный план: что делать, что наблюдать, какие обследования нужны", order: 1 },
      { id: 3, icon: "check_circle", title: "Удобный формат", description: "Онлайн-консультация через сайт или очный приём через ПроДокторов", order: 2 },
    ];
  }

  // /trust-badges/
  if (endpoint.startsWith("/trust-badges")) {
    return [
      { id: 1, icon: "shield_check", label: "Безопасность данных", order: 0 },
      { id: 2, icon: "award", label: "Подтверждённый стаж", order: 1 },
      { id: 3, icon: "message_circle_heart", label: "Поддержка в Telegram / VK", order: 2 },
      { id: 4, icon: "calendar_check", label: "Запись 24/7", order: 3 },
    ];
  }

  // /transport/
  if (endpoint.startsWith("/transport")) {
    return [
      { id: 1, icon: "train", title: "На метро", description: "Ближайшая станция метро в 5 минутах пешком от кабинета", order: 0 },
      { id: 2, icon: "car", title: "На автомобиле", description: "Рядом с кабинетом есть парковка для пациентов", order: 1 },
      { id: 3, icon: "car_taxi_front", title: "На такси", description: "Яндекс.Такси, Uber или Gett — удобно и быстро", order: 2 },
    ];
  }

  // /legal/
  if (endpoint.startsWith("/legal")) return LEGAL;

  // /available-dates/
  if (endpoint.startsWith("/available-dates")) return AVAILABLE_DATES;

  // /available-slots/?date=YYYY-MM-DD
  if (endpoint.startsWith("/available-slots")) {
    const [, query = ""] = endpoint.split("?");
    const params = new URLSearchParams(query);
    const date = params.get("date") || "";
    return SLOTS_BY_DATE[date] || [];
  }

  // /nearest-slot/
  if (endpoint.startsWith("/nearest-slot")) {
    const first = AVAILABLE_DATES[0];
    if (!first) return null;
    return SLOTS_BY_DATE[first.date]?.[0] ?? null;
  }

  // /date-summary/
  if (endpoint.startsWith("/date-summary")) {
    return {
      dates: AVAILABLE_DATES.reduce<Record<string, number>>((acc, d) => {
        acc[d.date] = d.free_slots;
        return acc;
      }, {}),
    };
  }

  // Telegram/VK prelink GET-status'ы
  if (endpoint.startsWith("/appointments/telegram/prelink/status")) {
    return { linked: false };
  }
  if (endpoint.startsWith("/appointments/vk/prelink/status")) {
    return { linked: false };
  }
  if (endpoint.startsWith("/appointments/vk/messaging-status")) {
    return { allowed: false };
  }

  return undefined;
}
