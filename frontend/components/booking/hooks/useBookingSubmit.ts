"use client";

import { useState } from "react";
import { postFormData } from "../../../lib/api";
import { extractErrorMessage } from "../../../lib/errors";
import type { ContactMethod, CreatedAppointment, Slot } from "../../../lib/types";

type SubmitParams = {
  selectedSlotId: number | null;
  selectedDate: string;
  selectedSlot: Slot | null;
  name: string;
  phone: string;
  reason: string;
  contactMethod: ContactMethod;
  vkIdPayload: Record<string, unknown> | null;
  files: FileList | null;
  consentGiven: boolean;
  privacyAccepted: boolean;
  offerAccepted: boolean;
  onSlotsRefresh: () => Promise<void>;
  /** Soft-reservation токен. Если есть — backend освободит лок после
   *  успешного create. Если нет — старый flow, защита через DB-constraint. */
  reservationToken?: string;
};

export function useBookingSubmit() {
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");
  const [createdAppointment, setCreatedAppointment] =
    useState<CreatedAppointment | null>(null);

  async function submit(params: SubmitParams): Promise<boolean> {
    // selectedDate и selectedSlot есть в SubmitParams для совместимости
    // с вызывающими компонентами, но внутри submit не используются — в
    // запрос на бэкенд уходит только selectedSlotId. Не destructure их
    // (иначе ESLint справедливо ругается на unused).
    const {
      selectedSlotId,
      name,
      phone,
      reason,
      contactMethod,
      vkIdPayload,
      files,
      consentGiven,
      privacyAccepted,
      offerAccepted,
      onSlotsRefresh,
      reservationToken,
    } = params;

    setError("");

    if (!selectedSlotId) {
      setError("Выберите время онлайн-разбора.");
      return false;
    }
    if (!name.trim()) {
      setError("Введите ваше имя.");
      return false;
    }
    if (!phone.trim()) {
      setError("Введите номер телефона.");
      return false;
    }
    if (
      contactMethod === "vk" &&
      (!vkIdPayload?.access_token || !vkIdPayload?.user_id)
    ) {
      setError("Сначала войдите через VK ID.");
      return false;
    }
    if (!consentGiven || !privacyAccepted || !offerAccepted) {
      setError("Необходимо принять все согласия.");
      return false;
    }

    try {
      setSubmitting(true);

      const formData = new FormData();
      formData.append("slot_id", String(selectedSlotId));
      formData.append("name", name);
      formData.append("phone", phone);
      formData.append("reason", reason);
      formData.append("preferred_contact_method", contactMethod);
      formData.append("consent_given", String(consentGiven));
      formData.append("privacy_accepted", String(privacyAccepted));
      formData.append("offer_accepted", String(offerAccepted));

      if (contactMethod === "vk" && vkIdPayload) {
        if (vkIdPayload.user_id)
          formData.append("vk_user_id", String(vkIdPayload.user_id));
        if (vkIdPayload.access_token)
          formData.append("vk_id_access_token", String(vkIdPayload.access_token));
      }

      if (reservationToken) {
        formData.append("reservation_token", reservationToken);
      }

      if (files) {
        Array.from(files).forEach((file) => formData.append("files", file));
      }

      const response = await postFormData("/appointments", formData);
      setCreatedAppointment(response as CreatedAppointment);
      setSuccess(true);
      return true;
    } catch (err) {
      const message = extractErrorMessage(err);
      setError(message);

      if (message.toLowerCase().includes("слот")) {
        await onSlotsRefresh();
      }
      return false;
    } finally {
      setSubmitting(false);
    }
  }

  return { submitting, success, error, setError, createdAppointment, submit };
}
