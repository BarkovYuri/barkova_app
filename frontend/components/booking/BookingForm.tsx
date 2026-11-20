"use client";

import { CalendarOff, MessageCircle, UserRound } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

import { reachGoal } from "../../lib/metrika";
import { isPhoneValid } from "../../lib/phone";
import type { ContactMethod } from "../../lib/types";
import { BookingSummary } from "./BookingSummary";
import { BookingStepper } from "./BookingStepper";
import { useDates, useSlots } from "./hooks/useSlots";
import { useSlotReservation } from "./hooks/useSlotReservation";
import { useScheduleInfo } from "./hooks/useScheduleInfo";
import { useVkId } from "./hooks/useVkId";
import { useVkMessaging } from "./hooks/useVkMessaging";
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
    dates,
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
  // Колбэк стабилен между рендерами: иначе эффект резервирования
  // перезапускался бы на каждый ввод в форме и мог сам себе вернуть 409.
  const handleReservationConflict = useCallback(async () => {
    clearSelectedSlot();
    await refreshSlots();
  }, [clearSelectedSlot, refreshSlots]);
  const { getToken: getReservationToken } = useSlotReservation({
    selectedSlotId,
    onConflict: handleReservationConflict,
  });

  // Часовой пояс расписания: «по времени Томска (МСК+4)».
  const scheduleInfo = useScheduleInfo();

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
  const [contactMethod, setContactMethodState] = useState<ContactMethod>("vk");
  const setContactMethod = useCallback((method: ContactMethod) => {
    if (method === "phone") reachGoal("booking_contact_phone");
    setContactMethodState(method);
  }, []);
  const vkId = useVkId(contactMethod === "vk");
  const vkMessaging = useVkMessaging(
    contactMethod === "vk" && vkId.authorized ? vkId.payload?.user_id : null
  );

  // Цели Метрики по шагам воронки записи.
  useEffect(() => {
    if (vkId.authorized) reachGoal("booking_vk_login");
  }, [vkId.authorized]);
  useEffect(() => {
    if (vkMessaging.allowed) reachGoal("booking_vk_messages_allowed");
  }, [vkMessaging.allowed]);

  // ── Отправка ────────────────────────────────────────────────────
  const {
    submitting,
    success,
    error,
    setError,
    submit,
  } = useBookingSubmit();

  // Объединяем ошибки: от хука submit + от VK
  const errorText = error || (contactMethod === "vk" ? vkId.loadError : "");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    reachGoal("booking_submit", { contact: contactMethod });
    const ok = await submit({
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
    reachGoal(ok ? "booking_success" : "booking_error", { contact: contactMethod });
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
    contactMethod === "phone" || (vkId.authorized && vkMessaging.allowed === true);

  // ── Success ─────────────────────────────────────────────────────
  if (success) {
    return (
      <SuccessView
        selectedDate={selectedDate}
        selectedSlot={selectedSlot}
        contactMethod={contactMethod}
        messagesAllowed={vkMessaging.allowed === true}
        dialogUrl={vkMessaging.dialogUrl}
        timezoneLabel={scheduleInfo?.label ?? ""}
      />
    );
  }

  // ── Свободного времени нет вообще ───────────────────────────────
  // Форма бесполезна: человек заполнит всё и упрётся в тупик. Показываем,
  // куда написать, чтобы не потерять пациента.
  if (!loadingDates && dates.length === 0) {
    return <NoSlotsView communityUrl={scheduleInfo?.community_url || ""} />;
  }

  // ── Main form ───────────────────────────────────────────────────
  return (
    <>
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
          scheduleInfo={scheduleInfo}
          hasAnyDates={dates.length > 0}
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
              setErrorText={setError}
              submitting={submitting}
              timezoneLabel={scheduleInfo?.label ?? ""}
            >
              <ContactMethodSection
                contactMethod={contactMethod}
                setContactMethod={setContactMethod}
                vkIdReady={vkId.ready}
                vkIdLoadError={vkId.loadError}
                vkIdAuthorized={vkId.authorized}
                vkIdContainerRef={vkId.containerRef}
                messagesAllowed={vkMessaging.allowed}
                dialogUrl={vkMessaging.dialogUrl}
              />
            </PatientForm>
          </form>
        </section>

        {/* Сводка — только третьей колонкой на широком экране. На телефоне
         * и планшете она оказывалась под кнопкой отправки и дублировала шаги. */}
        <div className="hidden xl:block">
          <BookingSummary
            selectedDate={selectedDate}
            selectedSlot={selectedSlot}
            contactMethod={contactMethod}
            contactReady={hasContactMethod}
            formReady={hasFilledForm}
            timezoneLabel={scheduleInfo?.label ?? ""}
          />
        </div>
      </div>
    </>
  );
}

function NoSlotsView({ communityUrl }: { communityUrl: string }) {
  return (
    <section className="mx-auto max-w-2xl animate-fade-in rounded-3xl border border-neutral-200 bg-neutral-0 p-6 text-center shadow-card sm:p-10">
      <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-100 text-primary-700">
        <CalendarOff className="h-7 w-7" strokeWidth={1.75} />
      </span>
      <h2 className="mt-5 text-h3-mobile sm:text-h3-desktop text-neutral-900">
        Свободного времени сейчас нет
      </h2>
      <p className="mt-3 text-base leading-relaxed text-neutral-600">
        Новые даты для онлайн-разбора скоро появятся. Напишите в сообщество
        VK, врач подберёт удобное время и ответит лично.
      </p>
      <div className="mt-7 flex flex-col justify-center gap-3 sm:flex-row">
        {communityUrl ? (
          <a href={communityUrl} target="_blank" rel="noopener noreferrer" className="btn-primary">
            <MessageCircle className="h-4 w-4" strokeWidth={2.5} />
            Написать в VK
          </a>
        ) : null}
        <Link href="/contacts" className="btn-secondary">
          Контакты врача
        </Link>
      </div>
    </section>
  );
}
