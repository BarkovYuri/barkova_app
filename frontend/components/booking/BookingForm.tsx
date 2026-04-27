"use client";

import { UserRound } from "lucide-react";
import Script from "next/script";
import { useRef, useState } from "react";

import { IS_MOCK_MODE } from "../../lib/api";
import { isPhoneValid } from "../../lib/phone";
import type { ContactMethod } from "../../lib/types";
import { BookingSummary } from "./BookingSummary";
import { useDates, useSlots } from "./hooks/useSlots";
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
  } = useSlots(selectedDate, slotsSectionRef);

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

  const telegram = useTelegramPrelink();
  const vkId = useVkId(contactMethod === "vk");

  function handleSetContactMethod(method: ContactMethod) {
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
    await submit({
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
  const hasContactMethod =
    contactMethod === "telegram"
      ? telegram.connected
      : contactMethod === "vk"
        ? vkId.authorized
        : true;

  const progressPercentage = Math.round(
    ((hasSelectedDate ? 1 : 0) +
      (hasSelectedSlot ? 1 : 0) +
      (hasFilledForm ? 1 : 0) +
      (hasContactMethod ? 1 : 0)) /
      4 *
      100
  );

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
      {/* В mock-режиме VK SDK не нужен — он только дёргает unpkg и валит unhandledRejection */}
      {!IS_MOCK_MODE ? (
        <Script
          src="https://unpkg.com/@vkid/sdk/dist-sdk/umd/index.js"
          strategy="afterInteractive"
        />
      ) : null}

      {/* Progress Bar */}
      <div className="mb-8 animate-fade-in">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary-600 text-sm font-bold font-heading text-neutral-0 shadow-md shadow-primary-500/30">
              {Math.min(Math.floor(progressPercentage / 25) + 1, 4)}
            </div>
            <div>
              <p className="text-sm font-semibold text-neutral-900">
                Ваш прогресс
              </p>
              <p className="text-xs text-neutral-500">
                {progressPercentage === 100
                  ? "Готово к отправке!"
                  : `Заполнено ${progressPercentage}%`}
              </p>
            </div>
          </div>
          <p className="text-sm font-bold text-primary-700 font-heading">
            {progressPercentage}%
          </p>
        </div>
        <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-neutral-100">
          <div
            className="h-full rounded-full transition-all duration-700 ease-out"
            style={{
              width: `${progressPercentage}%`,
              background:
                "linear-gradient(90deg, var(--color-primary-600), var(--color-primary-400) 60%, var(--color-secondary-500))",
            }}
          />
        </div>
        {/* Step indicators */}
        <div className="mt-4 flex justify-between gap-2 px-1">
          {[
            { label: "Дата", complete: hasSelectedDate },
            { label: "Время", complete: hasSelectedSlot },
            { label: "Данные", complete: hasFilledForm },
            { label: "Канал", complete: hasContactMethod },
          ].map(({ label, complete }, step) => (
            <div
              key={step}
              className="flex flex-1 flex-col items-center gap-1.5"
            >
              <div
                className={`h-1.5 w-full rounded-full transition-all duration-500 ${
                  complete ? "bg-secondary-500" : "bg-neutral-200"
                }`}
              />
              <p
                className={`text-xs font-medium transition-colors ${
                  complete ? "text-secondary-700" : "text-neutral-500"
                }`}
              >
                {label}
              </p>
            </div>
          ))}
        </div>
      </div>

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
