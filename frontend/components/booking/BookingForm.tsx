"use client";

import Script from "next/script";
import { useRef, useState } from "react";

import type { ContactMethod } from "../../lib/types";
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
  const hasFilledForm =
    name.trim() && phone.trim() && consentGiven && privacyAccepted;
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
      <Script
        src="https://unpkg.com/@vkid/sdk/dist-sdk/umd/index.js"
        strategy="afterInteractive"
      />

      {/* Progress Bar - Modern with animation */}
      <div className="mb-8 animate-fade-in">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-primary-600 to-secondary-600 text-sm font-bold text-white">
              {Math.min(Math.floor(progressPercentage / 25) + 1, 4)}
            </div>
            <div>
              <p className="text-sm font-semibold text-neutral-900">Ваш прогресс</p>
              <p className="text-xs text-neutral-500">
                {progressPercentage === 100 
                  ? "Готово к отправке!" 
                  : `Заполнено ${progressPercentage}%`}
              </p>
            </div>
          </div>
          <p className="text-sm font-bold text-primary-600">{progressPercentage}%</p>
        </div>
        <div className="relative h-3 w-full overflow-hidden rounded-full bg-neutral-100 shadow-inner">
          <div
            className="h-full bg-gradient-to-r from-primary-600 via-secondary-500 to-green-500 rounded-full transition-all duration-700 ease-out shadow-lg"
            style={{ 
              width: `${progressPercentage}%`,
              boxShadow: `0 0 20px rgba(0, 102, 204, ${progressPercentage / 100})`
            }}
          >
            {/* Shimmer effect */}
            <div className="absolute inset-0 animate-pulse bg-gradient-to-r from-transparent via-white to-transparent opacity-30" />
          </div>
        </div>
        {/* Step indicators */}
        <div className="mt-4 flex justify-between gap-2 px-2">
          {[
            { step: 1, label: "Дата", complete: hasSelectedDate },
            { step: 2, label: "Форма", complete: hasFilledForm },
            { step: 3, label: "Контакт", complete: hasContactMethod },
            { step: 4, label: "Отправка", complete: progressPercentage === 100 },
          ].map(({ step, label, complete }) => (
            <div key={step} className="flex flex-1 flex-col items-center gap-1">
              <div
                className={`h-2 w-full rounded-full transition-all duration-500 ${
                  complete ? "bg-gradient-to-r from-green-400 to-green-500" : "bg-neutral-200"
                }`}
              />
              <p className={`text-xs font-medium transition-colors ${
                complete ? "text-green-600" : "text-neutral-500"
              }`}>
                {label}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.02fr_0.98fr] lg:gap-8">
        {/* Left: Calendar & Slots */}
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

        {/* Right: Form */}
        <section
          ref={formSectionRef}
          className="card shadow-xl animate-fade-in"
        >
          {/* Header */}
          <div className="mb-8 pb-6 border-b border-neutral-200">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary-100 text-lg font-bold text-primary-600">
                ✓
              </div>
              <div>
                <h2 className="text-xl font-bold text-neutral-900">
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
      </div>
    </>
  );
}
