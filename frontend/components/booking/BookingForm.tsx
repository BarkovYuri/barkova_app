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
  const formSectionRef  = useRef<HTMLDivElement | null>(null);

  // ── Дата / календарь / слоты ────────────────────────────────────
  const {
    loading: loadingDates,
    selectedDate, setSelectedDate,
    currentMonth, setCurrentMonth,
    calendarDays,
  } = useDates();

  const {
    slots, loading: loadingSlots,
    selectedSlotId, setSelectedSlotId,
    selectedSlot, refreshSlots,
  } = useSlots(selectedDate, slotsSectionRef);

  // ── Данные пациента ─────────────────────────────────────────────
  const [name, setName]     = useState("");
  const [phone, setPhone]   = useState("");
  const [reason, setReason] = useState("");
  const [files, setFiles]   = useState<FileList | null>(null);

  // ── Согласия ────────────────────────────────────────────────────
  const [consentGiven,    setConsentGiven]    = useState(false);
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [offerAccepted,   setOfferAccepted]   = useState(false);

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
    submitting, success, error, setError, createdAppointment, submit,
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
      name, phone, reason,
      contactMethod,
      telegramPrelinkToken: telegram.token,
      vkIdPayload: vkId.payload as Record<string, unknown> | null,
      files,
      consentGiven, privacyAccepted, offerAccepted,
      onSlotsRefresh: refreshSlots,
    });
  }

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
      <Script src="https://unpkg.com/@vkid/sdk/dist-sdk/umd/index.js" strategy="afterInteractive" />

      <div className="grid gap-4 lg:grid-cols-[1.02fr_0.98fr] lg:gap-8">

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

        <section
          ref={formSectionRef}
          className="rounded-[1.75rem] border border-white/70 bg-white p-4 shadow-xl shadow-sky-100/40 sm:p-6"
        >
          <div className="mb-5 flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-sky-100 text-sm font-semibold text-sky-700">2</div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 sm:text-2xl">Оставьте данные</h2>
              <p className="mt-1 text-sm text-gray-500">Заполните форму, чтобы отправить заявку на консультацию</p>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <PatientForm
              selectedDate={selectedDate}
              selectedSlot={selectedSlot}
              name={name} setName={setName}
              phone={phone} setPhone={setPhone}
              reason={reason} setReason={setReason}
              consentGiven={consentGiven} setConsentGiven={setConsentGiven}
              privacyAccepted={privacyAccepted} setPrivacyAccepted={setPrivacyAccepted}
              offerAccepted={offerAccepted} setOfferAccepted={setOfferAccepted}
              files={files} setFiles={setFiles}
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
