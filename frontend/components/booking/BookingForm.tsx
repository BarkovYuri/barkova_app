"use client";

import { UserRound } from "lucide-react";
import Script from "next/script";
import { useRef, useState } from "react";

import { IS_MOCK_MODE } from "../../lib/api";
import { isPhoneValid } from "../../lib/phone";
import type { ContactMethod } from "../../lib/types";
import { BookingSummary } from "./BookingSummary";
import { BookingStepper } from "./BookingStepper";
import { useDates, useSlots } from "./hooks/useSlots";
import { useSlotReservation } from "./hooks/useSlotReservation";
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
  const contactMethod: ContactMethod = "vk";
  const vkId = useVkId(true);

  // ── Отправка ────────────────────────────────────────────────────
  const {
    submitting,
    success,
    error,
    setError,
    submit,
  } = useBookingSubmit();

  // Объединяем ошибки: от хука submit + от VK
  const errorText = error || vkId.loadError;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    await submit({
      selectedSlotId,
      selectedDate,
      selectedSlot,
      name,
      phone,
      reason,
      contactMethod,
      vkIdPayload: vkId.payload as Record<string, unknown> | null,
      files,
      consentGiven,
      privacyAccepted,
      offerAccepted,
      onSlotsRefresh: refreshSlots,
      reservationToken: getReservationToken(selectedSlotId),
    });
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
  const hasContactMethod = vkId.authorized;

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
          отрисовки страницы). */}
      {!IS_MOCK_MODE ? (
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
              <ContactMethodSection
                vkIdReady={vkId.ready}
                vkIdLoadError={vkId.loadError}
                vkIdAuthorized={vkId.authorized}
                vkIdContainerRef={vkId.containerRef}
              />
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
