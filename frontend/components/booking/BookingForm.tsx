"use client";

import Script from "next/script";
import { useEffect, useMemo, useRef, useState } from "react";
import { fetchAPI, postFormData } from "../../lib/api";

type AvailableDateItem =
  | string
  | {
      date: string;
      free_slots?: number;
    };

type Slot = {
  id: number;
  date: string;
  start_time: string;
  end_time: string;
  is_booked: boolean;
  is_active: boolean;
};

type CalendarDay = {
  key: string;
  date: Date | null;
  iso: string | null;
  isCurrentMonth: boolean;
  isAvailable: boolean;
  freeSlots?: number;
};

declare global {
  interface Window {
    VKIDSDK?: any;
  }
}

const WEEKDAY_LABELS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

function normalizeDates(input: AvailableDateItem[]): { date: string; free_slots?: number }[] {
  return input.map((item) => (typeof item === "string" ? { date: item } : item));
}

function extractErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    try {
      const parsed = JSON.parse(error.message);
      if (typeof parsed === "object" && parsed !== null) {
        const firstValue = Object.values(parsed)[0];
        if (Array.isArray(firstValue)) {
          return String(firstValue[0]);
        }
        if (typeof firstValue === "string") {
          return firstValue;
        }
      }
    } catch {
      return error.message;
    }
    return error.message;
  }

  return "Не удалось отправить запись.";
}

function formatDateLong(dateString: string) {
  const date = new Date(`${dateString}T00:00:00`);
  return new Intl.DateTimeFormat("ru-RU", {
    weekday: "long",
    day: "numeric",
    month: "long",
  }).format(date);
}

function formatMonthTitle(date: Date) {
  return new Intl.DateTimeFormat("ru-RU", {
    month: "long",
    year: "numeric",
  }).format(date);
}

function isoDate(date: Date) {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, "0");
  const day = `${date.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function startOfMonth(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

function addMonths(date: Date, amount: number) {
  return new Date(date.getFullYear(), date.getMonth() + amount, 1);
}

function getCalendarDays(
  monthDate: Date,
  availableMap: Map<string, { free_slots?: number }>
): CalendarDay[] {
  const firstDay = startOfMonth(monthDate);
  const jsWeekday = firstDay.getDay();
  const mondayBased = jsWeekday === 0 ? 6 : jsWeekday - 1;

  const gridStart = new Date(firstDay);
  gridStart.setDate(firstDay.getDate() - mondayBased);

  const days: CalendarDay[] = [];

  for (let i = 0; i < 42; i += 1) {
    const current = new Date(gridStart);
    current.setDate(gridStart.getDate() + i);

    const currentIso = isoDate(current);
    const available = availableMap.get(currentIso);

    days.push({
      key: `${currentIso}-${i}`,
      date: current,
      iso: currentIso,
      isCurrentMonth: current.getMonth() === monthDate.getMonth(),
      isAvailable: Boolean(available),
      freeSlots: available?.free_slots,
    });
  }

  return days;
}

export default function BookingForm() {
  const [dates, setDates] = useState<{ date: string; free_slots?: number }[]>([]);
  const [slots, setSlots] = useState<Slot[]>([]);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedSlotId, setSelectedSlotId] = useState<number | null>(null);

  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [reason, setReason] = useState("");
  const [contactMethod, setContactMethod] = useState<"telegram" | "vk">("telegram");
  const [vkConnected, setVkConnected] = useState(false);
  const [vkPrelinkToken, setVkPrelinkToken] = useState("");
  const [loadingVkLink, setLoadingVkLink] = useState(false);
  const [vkIdReady, setVkIdReady] = useState(false);
  const vkIdContainerRef = useRef<HTMLDivElement | null>(null);
  const [vkIdAuthorized, setVkIdAuthorized] = useState(false);
  const [vkIdPayload, setVkIdPayload] = useState<any>(null);
  const [files, setFiles] = useState<FileList | null>(null);

  const [consentGiven, setConsentGiven] = useState(false);
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [offerAccepted, setOfferAccepted] = useState(false);

  const [loadingDates, setLoadingDates] = useState(true);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [createdAppointment, setCreatedAppointment] = useState<any>(null);
  const [errorText, setErrorText] = useState("");

  const [telegramConnected, setTelegramConnected] = useState(false);
  const [telegramPrelinkToken, setTelegramPrelinkToken] = useState("");
  const [loadingTelegramLink, setLoadingTelegramLink] = useState(false);

  const [currentMonth, setCurrentMonth] = useState<Date>(startOfMonth(new Date()));

  const slotsSectionRef = useRef<HTMLDivElement | null>(null);
  const formSectionRef = useRef<HTMLDivElement | null>(null);

  const availableDatesMap = useMemo(() => {
    const map = new Map<string, { free_slots?: number }>();
    dates.forEach((item) => {
      map.set(item.date, { free_slots: item.free_slots });
    });
    return map;
  }, [dates]);

  useEffect(() => {
    async function loadDates() {
      try {
        setLoadingDates(true);
        setErrorText("");

        const data = await fetchAPI("/available-dates");
        const normalized = Array.isArray(data)
          ? normalizeDates(data)
          : normalizeDates(data?.dates || []);

        setDates(normalized);

        if (normalized.length > 0) {
          setSelectedDate(normalized[0].date);
          setCurrentMonth(startOfMonth(new Date(`${normalized[0].date}T00:00:00`)));
        }
      } catch {
        setErrorText("Не удалось загрузить доступные даты.");
      } finally {
        setLoadingDates(false);
      }
    }

    loadDates();
  }, []);

  useEffect(() => {
    async function loadSlots() {
      if (!selectedDate) {
        setSlots([]);
        return;
      }

      try {
        setLoadingSlots(true);
        setErrorText("");
        setSelectedSlotId(null);

        const data = await fetchAPI(`/available-slots?date=${selectedDate}`);
        setSlots(Array.isArray(data) ? data : []);

        if (typeof window !== "undefined" && window.innerWidth < 1024) {
          setTimeout(() => {
            slotsSectionRef.current?.scrollIntoView({
              behavior: "smooth",
              block: "start",
            });
          }, 120);
        }
      } catch {
        setErrorText("Не удалось загрузить свободное время.");
      } finally {
        setLoadingSlots(false);
      }
    }

    loadSlots();
  }, [selectedDate]);

  const selectedSlot = useMemo(
    () => slots.find((slot) => slot.id === selectedSlotId) || null,
    [slots, selectedSlotId]
  );

  const calendarDays = useMemo(
    () => getCalendarDays(currentMonth, availableDatesMap),
    [currentMonth, availableDatesMap]
  );

  useEffect(() => {
    function initVkIdWidget() {
      const appId = process.env.NEXT_PUBLIC_VK_APP_ID;
      const container = vkIdContainerRef.current;
      const VKID = window.VKIDSDK;
  
      if (contactMethod !== "vk") {
        return;
      }
  
      if (!appId || !container || !VKID) {
        return;
      }
  
      if (container.childNodes.length > 0) {
        return;
      }
  
      try {
        VKID.Config.init({
          app: Number(appId),
          redirectUrl: "https://doctor-barkova.ru/auth/vk/callback",
          responseMode: VKID.ConfigResponseMode.Callback,
          source: VKID.ConfigSource.LOWCODE,
          scope: "",
        });
  
        const oneTap = new VKID.OneTap();
  
        oneTap
          .render({
            container,
            fastAuthEnabled: false,
            showAlternativeLogin: true,
            styles: {
              borderRadius: 15,
              height: 50,
            },
          })
          .on(VKID.WidgetEvents.ERROR, (error: unknown) => {
            console.error("VK ID widget error", error);
          })
          .on(VKID.OneTapInternalEvents.LOGIN_SUCCESS, (payload: any) => {
            const code = payload?.code;
            const deviceId = payload?.device_id;
  
            if (!code || !deviceId) {
              setErrorText("VK ID не вернул code или device_id.");
              return;
            }
  
            VKID.Auth.exchangeCode(code, deviceId)
              .then((data: any) => {
                console.log("VK ID exchange success", data);
                setVkIdAuthorized(true);
                setVkIdPayload(data);
                setVkConnected(true);
                setErrorText("");
              })
              .catch((error: unknown) => {
                console.error("VK ID exchange error", error);
                setVkIdAuthorized(false);
                setVkIdPayload(null);
                setVkConnected(false);
                setErrorText("Не удалось завершить вход через VK ID.");
              });
          });
  
        setVkIdReady(true);
      } catch (error) {
        console.error("VK ID init error", error);
      }
    }
  
    if (contactMethod !== "vk") {
      if (vkIdContainerRef.current) {
        vkIdContainerRef.current.innerHTML = "";
      }
      setVkIdReady(false);
      setVkIdAuthorized(false);
      setVkIdPayload(null);
      return;
    }
  
    initVkIdWidget();
  
    const timer = setInterval(() => {
      if (window.VKIDSDK) {
        initVkIdWidget();
      }
    }, 500);
  
    return () => clearInterval(timer);
  }, [contactMethod]);

  async function handleVkConnect() {
    const popup = window.open("", "_blank");

    try {
      setLoadingVkLink(true);
      setErrorText("");

      const data = await fetchAPI("/appointments/vk/prelink", {
        method: "POST",
      });

      setVkPrelinkToken(data.token);

      if (popup) {
        popup.location.href = data.vk_url;
      } else {
        window.location.href = data.vk_url;
      }
    } catch {
      if (popup) {
        popup.close();
      }
      setErrorText("Не удалось создать ссылку для подключения VK.");
    } finally {
      setLoadingVkLink(false);
    }
  }
  
  async function checkVkConnection() {
    if (!vkPrelinkToken) {
      setErrorText("Сначала нажмите «Подключить VK».");
      return;
    }
  
    try {
      setErrorText("");
  
      const data = await fetchAPI(
        `/appointments/vk/prelink/status?token=${vkPrelinkToken}`
      );
  
      if (data?.linked) {
        setVkConnected(true);
      } else {
        setVkConnected(false);
        setErrorText("VK ещё не подтверждён. Напишите боту сообщества, затем проверьте снова.");
      }
    } catch {
      setErrorText("Не удалось проверить подключение VK.");
    }
  }

  function switchToTelegram() {
    setContactMethod("telegram");

    if (vkIdContainerRef.current) {
      vkIdContainerRef.current.innerHTML = "";
    }

    setVkIdReady(false);
    setVkIdAuthorized(false);
    setVkIdPayload(null);
    setVkConnected(false);
    setErrorText("");
  }

  function switchToVk() {
    setContactMethod("vk");
    setErrorText("");
  }

  async function handleTelegramConnect() {
    const popup = window.open("", "_blank");

    try {
      setLoadingTelegramLink(true);
      setErrorText("");

      const data = await fetchAPI("/appointments/telegram/prelink", {
        method: "POST",
      });

      setTelegramPrelinkToken(data.token);

      if (popup) {
        popup.location.href = data.bot_url;
      } else {
        window.location.href = data.bot_url;
      }
    } catch {
      if (popup) {
        popup.close();
      }
      setErrorText("Не удалось создать ссылку для подключения Telegram.");
    } finally {
      setLoadingTelegramLink(false);
    }
  }

  async function checkTelegramConnection() {
    if (!telegramPrelinkToken) {
      setErrorText("Сначала нажмите «Подключить Telegram».");
      return;
    }

    try {
      setErrorText("");

      const data = await fetchAPI(
        `/appointments/telegram/prelink/status?token=${telegramPrelinkToken}`
      );

      if (data?.linked) {
        setTelegramConnected(true);
      } else {
        setTelegramConnected(false);
        setErrorText("Telegram ещё не подтверждён. Нажмите Start в боте, затем проверьте снова.");
      }
    } catch {
      setErrorText("Не удалось проверить подключение Telegram.");
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrorText("");

    if (contactMethod === "telegram" && !telegramPrelinkToken) {
      setErrorText("Сначала подключите Telegram.");
      return;
    }

    if (!selectedSlotId) {
      setErrorText("Выберите время консультации.");
      return;
    }

    if (contactMethod === "vk" && !vkIdAuthorized) {
      setErrorText("Сначала войдите через VK ID.");
      return;
    }

    try {
      setSubmitting(true);

      const formData = new FormData();
      if (contactMethod === "vk" && vkIdPayload?.user_id) {
        formData.append("vk_user_id", String(vkIdPayload.user_id));
      }
      formData.append("slot_id", String(selectedSlotId));
      formData.append("name", name);
      formData.append("phone", phone);
      formData.append("reason", reason);
      formData.append("preferred_contact_method", contactMethod);
      formData.append("telegram_prelink_token", telegramPrelinkToken);
      formData.append("consent_given", String(consentGiven));
      formData.append("privacy_accepted", String(privacyAccepted));
      formData.append("offer_accepted", String(offerAccepted));

      if (contactMethod === "vk" && vkIdPayload?.code) {
        formData.append("vk_id_code", String(vkIdPayload.code));
      }

      if (contactMethod === "vk" && vkIdPayload?.device_id) {
        formData.append("vk_id_device_id", String(vkIdPayload.device_id));
      }

      if (files) {
        Array.from(files).forEach((file) => {
          formData.append("files", file);
        });
      }

      const response = await postFormData("/appointments", formData);
      setCreatedAppointment(response);
      setSuccess(true);
    } catch (error) {
      const message = extractErrorMessage(error);
      setErrorText(message);

      if (message.toLowerCase().includes("слот")) {
        setSelectedSlotId(null);
        try {
          const refreshed = await fetchAPI(`/available-slots?date=${selectedDate}`);
          setSlots(Array.isArray(refreshed) ? refreshed : []);
        } catch {
          // ignore
        }
      }
    } finally {
      setSubmitting(false);
    }
  }

  if (success) {
    return (
      <div className="mx-auto max-w-3xl rounded-[2rem] border border-sky-100 bg-white p-5 shadow-xl shadow-sky-100/50 sm:p-8">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-sky-100 text-sky-700">
          ✓
        </div>

        <h2 className="mt-5 text-2xl font-semibold text-gray-900 sm:text-3xl">
          Заявка на онлайн-консультацию отправлена
        </h2>

        <p className="mt-4 leading-7 text-gray-600">
          Мы получили вашу заявку. Врач или администратор свяжется с вами для
          подтверждения записи выбранным способом.
        </p>

        {selectedDate && selectedSlot ? (
          <div className="mt-6 rounded-3xl border border-gray-100 bg-sky-50 p-4 sm:p-6">
            <p className="text-sm uppercase tracking-[0.16em] text-sky-700">
              Детали записи
            </p>
            <p className="mt-3 text-base text-gray-800 sm:text-lg">
              <span className="font-medium">Дата:</span> {formatDateLong(selectedDate)}
            </p>
            <p className="mt-2 text-base text-gray-800 sm:text-lg">
              <span className="font-medium">Время:</span>{" "}
              {selectedSlot.start_time.slice(0, 5)} – {selectedSlot.end_time.slice(0, 5)}
            </p>
            <p className="mt-2 text-base text-gray-800 sm:text-lg">
              <span className="font-medium">Подтверждение:</span>{" "}
              {contactMethod === "telegram" ? "Telegram" : "VK"}
            </p>
          </div>
        ) : null}

        <a
          href="/"
          className="mt-7 inline-flex rounded-2xl bg-sky-600 px-6 py-3 text-white transition hover:bg-sky-700"
        >
          Вернуться на главную
        </a>
      </div>
    );
  }

  return (
    <>
      <Script
        src="https://unpkg.com/@vkid/sdk/dist-sdk/umd/index.js"
        strategy="afterInteractive"
      />
      <div className="grid gap-4 lg:grid-cols-[1.02fr_0.98fr] lg:gap-8">
      <section className="rounded-[1.75rem] border border-white/70 bg-white p-4 shadow-xl shadow-sky-100/40 sm:p-6">
        <div className="mb-5 flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-sky-100 text-sm font-semibold text-sky-700">
            1
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900 sm:text-2xl">
              Выберите дату и время
            </h2>
            <p className="mt-1 text-sm text-gray-500">
              Календарь свободных онлайн-консультаций
            </p>
          </div>
        </div>

        <div className="rounded-[1.5rem] border border-sky-100 bg-sky-50/70 p-3 sm:p-5">
          <div className="mb-4 flex items-center justify-between gap-2">
            <button
              type="button"
              onClick={() => setCurrentMonth(addMonths(currentMonth, -1))}
              className="rounded-2xl border border-white bg-white px-3 py-2 text-sm font-medium text-gray-700 transition hover:border-sky-200 hover:text-sky-700"
            >
              ←
            </button>

            <p className="text-center text-sm font-semibold capitalize text-gray-900 sm:text-lg">
              {formatMonthTitle(currentMonth)}
            </p>

            <button
              type="button"
              onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
              className="rounded-2xl border border-white bg-white px-3 py-2 text-sm font-medium text-gray-700 transition hover:border-sky-200 hover:text-sky-700"
            >
              →
            </button>
          </div>

          <div className="grid grid-cols-7 gap-1.5 text-center sm:gap-2">
            {WEEKDAY_LABELS.map((label) => (
              <div key={label} className="py-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-400 sm:text-xs">
                {label}
              </div>
            ))}

            {loadingDates
              ? Array.from({ length: 35 }).map((_, index) => (
                  <div
                    key={`skeleton-${index}`}
                    className="h-12 animate-pulse rounded-2xl bg-white/70 sm:h-14"
                  />
                ))
              : calendarDays.map((day) => {
                  if (!day.date || !day.iso) {
                    return <div key={day.key} className="h-12 rounded-2xl sm:h-14" />;
                  }

                  const isSelected = selectedDate === day.iso;
                  const isDisabled = !day.isAvailable;
                  const isOutside = !day.isCurrentMonth;

                  return (
                    <button
                      key={day.key}
                      type="button"
                      disabled={isDisabled}
                      onClick={() => {
                        setSelectedDate(day.iso!);
                        setCurrentMonth(startOfMonth(day.date!));
                      }}
                      className={`flex h-12 flex-col items-center justify-center rounded-2xl border text-center transition sm:h-16 ${
                        isSelected
                          ? "border-sky-600 bg-sky-600 text-white shadow-sm"
                          : isDisabled
                          ? "cursor-not-allowed border-gray-100 bg-gray-50 text-gray-300"
                          : "border-white bg-white text-gray-800 hover:border-sky-300 hover:bg-sky-100"
                      } ${isOutside ? "opacity-40" : ""}`}
                    >
                      <span className="text-sm font-semibold">{day.date.getDate()}</span>
                      <span className={`mt-0.5 text-[10px] sm:mt-1 sm:text-[11px] ${isSelected ? "text-sky-100" : "text-gray-400"}`}>
                        {day.isAvailable
                          ? typeof day.freeSlots === "number"
                            ? `${day.freeSlots} мест`
                            : "•"
                          : "—"}
                      </span>
                    </button>
                  );
                })}
          </div>
        </div>

        <div ref={slotsSectionRef} className="mt-4 rounded-[1.5rem] border border-gray-100 bg-white p-4 sm:mt-6 sm:p-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h3 className="text-xs font-medium uppercase tracking-[0.16em] text-gray-500 sm:text-sm">
                Свободное время
              </h3>
              {selectedDate ? (
                <p className="mt-2 text-sm font-medium capitalize text-gray-900 sm:text-base">
                  {formatDateLong(selectedDate)}
                </p>
              ) : null}
            </div>

            {selectedDate ? (
              <div className="rounded-2xl bg-sky-50 px-3 py-2 text-xs text-sky-700 sm:px-4 sm:text-sm">
                {slots.length} слотов
              </div>
            ) : null}
          </div>

          {loadingSlots ? (
            <div className="mt-4 flex gap-3 overflow-x-auto pb-1 sm:grid sm:grid-cols-3 sm:overflow-visible sm:pb-0">
              {Array.from({ length: 6 }).map((_, index) => (
                <div
                  key={`slot-skeleton-${index}`}
                  className="h-11 min-w-[92px] animate-pulse rounded-2xl bg-gray-100 sm:min-w-0"
                />
              ))}
            </div>
          ) : slots.length === 0 ? (
            <div className="mt-4 rounded-2xl bg-gray-50 px-4 py-4 text-sm text-gray-500">
              На выбранную дату свободного времени нет.
            </div>
          ) : (
            <div className="mt-4 flex gap-3 overflow-x-auto pb-1 sm:grid sm:grid-cols-3 sm:overflow-visible sm:pb-0">
              {slots.map((slot) => {
                const active = selectedSlotId === slot.id;

                return (
                  <button
                    key={slot.id}
                    type="button"
                    onClick={() => {
                      setSelectedSlotId(slot.id);
                      if (typeof window !== "undefined" && window.innerWidth < 1024) {
                        setTimeout(() => {
                          formSectionRef.current?.scrollIntoView({
                            behavior: "smooth",
                            block: "start",
                          });
                        }, 120);
                      }
                    }}
                    className={`min-w-[96px] rounded-2xl border px-4 py-3 text-sm font-medium transition sm:min-w-0 sm:text-base ${
                      active
                        ? "border-sky-600 bg-sky-600 text-white shadow-sm"
                        : "border-gray-200 bg-white text-gray-700 hover:border-sky-300 hover:bg-sky-50"
                    }`}
                  >
                    {slot.start_time.slice(0, 5)}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </section>

      <section
        ref={formSectionRef}
        className="rounded-[1.75rem] border border-white/70 bg-white p-4 shadow-xl shadow-sky-100/40 sm:p-6"
      >
        <div className="mb-5 flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-sky-100 text-sm font-semibold text-sky-700">
            2
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900 sm:text-2xl">
              Оставьте данные
            </h2>
            <p className="mt-1 text-sm text-gray-500">
              Заполните форму, чтобы отправить заявку на консультацию
            </p>
          </div>
        </div>

        {selectedSlot ? (
          <div className="mb-5 rounded-3xl border border-sky-100 bg-sky-50 p-4 text-sm text-gray-700">
            <p className="font-medium text-gray-900">Вы выбрали:</p>
            <p className="mt-2">
              {formatDateLong(selectedDate)} в {selectedSlot.start_time.slice(0, 5)}
            </p>
          </div>
        ) : null}

        <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Ваше имя
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Например, Елена"
              className="w-full rounded-2xl border border-gray-200 px-4 py-3.5 text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-sky-500 focus:ring-4 focus:ring-sky-100"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Телефон
            </label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+7 (___) ___-__-__"
              className="w-full rounded-2xl border border-gray-200 px-4 py-3.5 text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-sky-500 focus:ring-4 focus:ring-sky-100"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Причина обращения
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Кратко опишите вопрос"
              rows={4}
              className="w-full rounded-2xl border border-gray-200 px-4 py-3 text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-sky-500 focus:ring-4 focus:ring-sky-100"
            />
          </div>

          <div className="rounded-3xl border border-sky-100 bg-sky-50/70 p-4 sm:p-5">
            <p className="text-sm font-semibold uppercase tracking-[0.16em] text-sky-700">
              Подтверждение / отмена записи
            </p>
            <p className="mt-2 text-sm leading-6 text-gray-600">
              Выберите удобный способ связи, чтобы врач или администратор могли
              подтвердить или при необходимости отменить запись.
            </p>

            <div className="mt-4 grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setContactMethod("telegram")}
                className={`rounded-2xl border px-4 py-3 text-sm font-medium transition ${
                  contactMethod === "telegram"
                    ? "border-sky-600 bg-sky-600 text-white"
                    : "border-gray-200 bg-white text-gray-700 hover:border-sky-300 hover:bg-sky-50"
                }`}
              >
                Telegram
              </button>

              <button
                type="button"
                onClick={() => setContactMethod("vk")}
                className={`rounded-2xl border px-4 py-3 text-sm font-medium transition ${
                  contactMethod === "vk"
                    ? "border-sky-600 bg-sky-600 text-white"
                    : "border-gray-200 bg-white text-gray-700 hover:border-sky-300 hover:bg-sky-50"
                }`}
              >
                VK
              </button>
            </div>

            {contactMethod === "telegram" ? (
              <div className="mt-4 rounded-2xl border border-blue-100 bg-blue-50 px-4 py-4">
                <p className="text-sm leading-6 text-gray-700">
                  Сначала подключите Telegram, чтобы получать уведомления о записи,
                  подтверждении и отмене консультации.
                </p>

                <div className="mt-4 flex flex-col gap-3">
                  <button
                    type="button"
                    onClick={handleTelegramConnect}
                    disabled={loadingTelegramLink}
                    className="inline-flex items-center justify-center rounded-2xl bg-blue-500 px-5 py-3.5 text-sm font-medium text-white transition hover:bg-blue-600 disabled:cursor-not-allowed disabled:bg-blue-300"
                  >
                    {loadingTelegramLink ? "Создаём ссылку..." : "Подключить Telegram"}
                  </button>

                  <button
                    type="button"
                    onClick={checkTelegramConnection}
                    disabled={!telegramPrelinkToken}
                    className="inline-flex items-center justify-center rounded-2xl border border-gray-200 bg-white px-5 py-3.5 text-sm font-medium text-gray-700 transition hover:border-sky-300 hover:bg-sky-50 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Проверить подключение
                  </button>

                  <div
                    className={`inline-flex items-center justify-center rounded-2xl px-4 py-3 text-sm font-medium ${
                      telegramConnected
                        ? "bg-green-100 text-green-700"
                        : "border border-gray-200 bg-white text-gray-500"
                    }`}
                  >
                    {telegramConnected ? "Telegram подключён" : "Telegram ещё не подключён"}
                  </div>
                </div>
              </div>
            ) : (
              <div className="mt-4 rounded-2xl border border-blue-100 bg-blue-50 px-5 py-5">
                <p className="text-sm leading-6 text-gray-700">
                  Войдите через VK ID, чтобы получать уведомления и управлять записью
                  прямо во ВКонтакте.
                </p>

                <div className="mt-4 min-h-[50px]" ref={vkIdContainerRef} />

                {!vkIdReady ? (
                  <p className="mt-3 text-sm text-gray-500">
                    Загружаем VK...
                  </p>
                ) : null}

                {vkIdAuthorized ? (
                  <div className="mt-4 rounded-xl bg-green-100 px-4 py-3 text-sm font-medium text-green-700">
                    Вы успешно вошли через VK ID
                  </div>
                ) : (
                  <div className="mt-4 rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-500">
                    Авторизуйтесь через VK ID, чтобы продолжить запись через ВКонтакте
                  </div>
                )}
              </div>
            )}
           <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Файлы (по желанию)
            </label>
            <input
              type="file"
              multiple
              onChange={(e) => setFiles(e.target.files)}
              className="block w-full rounded-2xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-600 file:mr-4 file:rounded-xl file:border-0 file:bg-sky-100 file:px-4 file:py-2 file:text-sm file:font-medium file:text-sky-700 hover:file:bg-sky-200"
            />
            </div>
          </div>

          <div className="space-y-3 rounded-3xl bg-gray-50 p-4">
            <label className="flex items-start gap-3 text-sm text-gray-600">
              <input
                type="checkbox"
                checked={consentGiven}
                onChange={(e) => setConsentGiven(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-gray-300 text-sky-600 focus:ring-sky-500"
              />
              <span>Согласен(на) на обработку персональных данных</span>
            </label>

            <label className="flex items-start gap-3 text-sm text-gray-600">
              <input
                type="checkbox"
                checked={privacyAccepted}
                onChange={(e) => setPrivacyAccepted(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-gray-300 text-sky-600 focus:ring-sky-500"
              />
              <span>Принимаю политику конфиденциальности</span>
            </label>

            <label className="flex items-start gap-3 text-sm text-gray-600">
              <input
                type="checkbox"
                checked={offerAccepted}
                onChange={(e) => setOfferAccepted(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-gray-300 text-sky-600 focus:ring-sky-500"
              />
              <span>Принимаю условия оферты</span>
            </label>
          </div>

          {errorText ? (
            <div className="rounded-2xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
              {errorText}
            </div>
          ) : null}

          <button
            type="submit"
            disabled={submitting}
            className="inline-flex min-h-[56px] w-full items-center justify-center rounded-2xl bg-sky-600 px-6 py-4 text-base font-medium text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-sky-300"
          >
            {submitting ? "Отправляем..." : "Записаться на консультацию"}
          </button>
        </form>
      </section>
      </div>
    </>
  );
}
