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
  if (endpoint.startsWith("/blocks")) return [];

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
