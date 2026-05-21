"use client";

import { UserRound } from "lucide-react";
import Script from "next/script";
import { useEffect, useRef, useState } from "react";

import { IS_MOCK_MODE } from "../../lib/api";
import { isPhoneValid } from "../../lib/phone";
import {
  applyTelegramTheme,
  useTelegramWebApp,
} from "../../lib/telegramWebApp";
import type { ContactMethod } from "../../lib/types";
import { BookingSummary } from "./BookingSummary";
import { BookingStepper } from "./BookingStepper";
import { useDates, useSlots } from "./hooks/useSlots";
import { useSlotReservation } from "./hooks/useSlotReservation";
import { useTelegramPrelink } from "./hooks/useTelegramPrelink";
import { useVkId } from "./hooks/useVkId";
import { useBookingSubmit } from "./hooks/useBookingSubmit";

import { CalendarSection } from "./steps/CalendarSection";
import { ContactMethodSection } from "./steps/ContactMethodSection";
import { PatientForm } from "./steps/PatientForm";
import { SuccessView } from "./steps/SuccessView";

export default function BookingForm() {
  // ── Refs ────────────────────────────────────────────────────────
  const slotsSectionRef = useRef<HTMLDivElement | null>(null);
  const formSectionRef = useRef<HTMLDivElement | null>(null);

  // ── Дата / календарь / слоты ────────────────────────────────────
  const {
    loading: loadingDates,
    selectedDate,
    setSelectedDate,
    currentMonth,
    setCurrentMonth,
    calendarDays,
  } = useDates();

  const {
    slots,
    loading: loadingSlots,
    selectedSlotId,
    setSelectedSlotId,
    selectedSlot,
    refreshSlots,
    clearSelectedSlot,
  } = useSlots(selectedDate, slotsSectionRef);

  // Soft-reservation: при выборе слота держим за пользователем 5 минут.
  // 409 от backend → слот успели забрать; сбрасываем выбор и обновляем список.
  const { getToken: getReservationToken } = useSlotReservation({
    selectedSlotId,
    onConflict: async () => {
      clearSelectedSlot();
      await refreshSlots();
    },
  });

  // ── Данные пациента ─────────────────────────────────────────────
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [reason, setReason] = useState("");
  const [files, setFiles] = useState<FileList | null>(null);

  // ── Согласия ────────────────────────────────────────────────────
  const [consentGiven, setConsentGiven] = useState(false);
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [offerAccepted, setOfferAccepted] = useState(false);

  // ── Способ связи ────────────────────────────────────────────────
  const [contactMethod, setContactMethod] = useState<ContactMethod>("telegram");

  // ── Telegram Mini App ───────────────────────────────────────────
  const { webApp, isInTelegram } = useTelegramWebApp();
  const tgInitData = webApp?.initData ?? "";

  // Применяем тему Telegram при первой возможности и фиксируем способ связи
  useEffect(() => {
    if (webApp) {
      applyTelegramTheme(webApp);
      setContactMethod("telegram");
    }
  }, [webApp]);

  const telegram = useTelegramPrelink();
  const vkId = useVkId(contactMethod === "vk" && !isInTelegram);

  function handleSetContactMethod(method: ContactMethod) {
    if (isInTelegram) return; // в Mini App канал зафиксирован
    setContactMethod(method);
    if (method === "telegram") telegram.reset();
  }

  // ── Отправка ────────────────────────────────────────────────────
  const {
    submitting,
    success,
    error,
    setError,
    createdAppointment,
    submit,
  } = useBookingSubmit();

  // Объединяем ошибки: от хука submit + от Telegram/VK
  const errorText = error || telegram.error || vkId.loadError;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const ok = await submit({
      selectedSlotId,
      selectedDate,
      selectedSlot,
      name,
      phone,
      reason,
      contactMethod,
      telegramPrelinkToken: telegram.token,
      vkIdPayload: vkId.payload as Record<string, unknown> | null,
      files,
      consentGiven,
      privacyAccepted,
      offerAccepted,
      onSlotsRefresh: refreshSlots,
      tgInitData,
      reservationToken: getReservationToken(selectedSlotId),
    });

    // Если открыто как Mini App — даём пользователю увидеть SuccessView,
    // потом закрываем Mini App и возвращаемся в чат с ботом.
    if (ok && webApp) {
      try {
        webApp.HapticFeedback?.notificationOccurred?.("success");
      } catch {
        // ignore
      }
      setTimeout(() => {
        try {
          webApp.close();
        } catch {
          // ignore
        }
      }, 2500);
    }
  }

  // ── Progress calculation ─────────────────────────────────────────
  const hasSelectedDate = !!selectedDate;
  const hasSelectedSlot = !!selectedSlotId;
  const hasFilledForm = !!(
    name.trim() &&
    isPhoneValid(phone) &&
    consentGiven &&
    privacyAccepted &&
    offerAccepted
  );
  // В Mini App канал уже подтверждён автоматически через initData
  const hasContactMethod =
    isInTelegram ||
    (contactMethod === "telegram"
      ? telegram.connected
      : contactMethod === "vk"
        ? vkId.authorized
        : true);

  // ── Success ─────────────────────────────────────────────────────
  if (success) {
    return (
      <SuccessView
        selectedDate={selectedDate}
        selectedSlot={selectedSlot}
        contactMethod={contactMethod}
      />
    );
  }

  // ── Main form ───────────────────────────────────────────────────
  return (
    <>
      {/* VK SDK — тяжёлый внешний скрипт с unpkg, в РФ может грузиться
          5–10 секунд или таймаутить. На `afterInteractive` он блокировал
          парсинг и хydration на медленных мобильных → «кнопки не
          нажимаются». Переводим на `lazyOnload` (грузится после полной
          отрисовки страницы), и только когда пользователь реально
          выбрал VK-канал — useVkId всё равно нужен только в этот момент. */}
      {!IS_MOCK_MODE && contactMethod === "vk" ? (
        <Script
          src="https://unpkg.com/@vkid/sdk/dist-sdk/umd/index.js"
          strategy="lazyOnload"
        />
      ) : null}

      <BookingStepper
        hasSelectedDate={hasSelectedDate}
        hasSelectedSlot={hasSelectedSlot}
        hasFilledForm={hasFilledForm}
        hasContactMethod={hasContactMethod}
      />

      <div className="grid gap-4 lg:gap-6 xl:gap-8 lg:grid-cols-2 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(280px,320px)]">
        {/* Calendar & Slots */}
        <CalendarSection
          loadingDates={loadingDates}
          currentMonth={currentMonth}
          setCurrentMonth={setCurrentMonth}
          calendarDays={calendarDays}
          selectedDate={selectedDate}
          setSelectedDate={setSelectedDate}
          slots={slots}
          loadingSlots={loadingSlots}
          selectedSlotId={selectedSlotId}
          setSelectedSlotId={setSelectedSlotId}
          formSectionRef={formSectionRef}
          slotsSectionRef={slotsSectionRef}
        />

        {/* Form */}
        <section
          ref={formSectionRef}
          className="rounded-3xl border border-neutral-200 bg-neutral-0 shadow-card animate-fade-in p-6 md:p-8"
        >
          <div className="mb-8 pb-6 border-b border-neutral-200">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-primary-100 text-primary-700">
                <UserRound className="h-6 w-6" strokeWidth={2} />
              </div>
              <div>
                <h2 className="text-h3-mobile sm:text-h3-desktop text-neutral-900">
                  Ваши данные
                </h2>
                <p className="mt-1 text-sm text-neutral-600">
                  Заполните форму для подтверждения записи
                </p>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <PatientForm
              selectedDate={selectedDate}
              selectedSlot={selectedSlot}
              name={name}
              setName={setName}
              phone={phone}
              setPhone={setPhone}
              reason={reason}
              setReason={setReason}
              consentGiven={consentGiven}
              setConsentGiven={setConsentGiven}
              privacyAccepted={privacyAccepted}
              setPrivacyAccepted={setPrivacyAccepted}
              offerAccepted={offerAccepted}
              setOfferAccepted={setOfferAccepted}
              files={files}
              setFiles={setFiles}
              errorText={errorText}
              submitting={submitting}
            >
              {isInTelegram ? (
                <div className="rounded-2xl border border-secondary-200 bg-secondary-50 px-4 py-3 text-sm text-secondary-800 flex items-start gap-2">
                  <span aria-hidden>✅</span>
                  <span>
                    <b>Telegram подключён автоматически.</b>
                    <span className="block text-secondary-700 mt-0.5">
                      Подтверждение и напоминания придут в этот же чат.
                    </span>
                  </span>
                </div>
              ) : (
                <ContactMethodSection
                  contactMethod={contactMethod}
                  setContactMethod={handleSetContactMethod}
                  onTelegramConnect={telegram.connect}
                  onCheckTelegram={telegram.checkStatus}
                  loadingTelegramLink={telegram.loading}
                  telegramConnected={telegram.connected}
                  telegramPrelinkToken={telegram.token}
                  vkIdReady={vkId.ready}
                  vkIdLoadError={vkId.loadError}
                  vkIdAuthorized={vkId.authorized}
                  vkIdContainerRef={vkId.containerRef}
                />
              )}
            </PatientForm>
          </form>
        </section>

        {/* Sticky Summary — на xl+ как третья колонка справа,
         * на меньших экранах опускается под форму на всю ширину */}
        <div className="lg:col-span-2 xl:col-span-1">
          <BookingSummary
            selectedDate={selectedDate}
            selectedSlot={selectedSlot}
            contactMethod={contactMethod}
            contactReady={hasContactMethod}
            formReady={hasFilledForm}
          />
        </div>
      </div>
    </>
  );
}
