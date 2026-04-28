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
  telegramPrelinkToken: string;
  vkIdPayload: Record<string, unknown> | null;
  files: FileList | null;
  consentGiven: boolean;
  privacyAccepted: boolean;
  offerAccepted: boolean;
  onSlotsRefresh: () => Promise<void>;
  /** Если открыто как Telegram Mini App — initData передаём на бэкенд
   *  для авто-привязки без prelink-flow. */
  tgInitData?: string;
};

export function useBookingSubmit() {
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");
  const [createdAppointment, setCreatedAppointment] =
    useState<CreatedAppointment | null>(null);

  async function submit(params: SubmitParams): Promise<boolean> {
    const {
      selectedSlotId,
      selectedDate,
      name,
      phone,
      reason,
      contactMethod,
      telegramPrelinkToken,
      vkIdPayload,
      files,
      consentGiven,
      privacyAccepted,
      offerAccepted,
      onSlotsRefresh,
      tgInitData,
    } = params;

    setError("");

    if (!selectedSlotId) {
      setError("Выберите время консультации.");
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
    // В Mini App Telegram уже подтверждён через initData — prelink не требуется.
    if (
      contactMethod === "telegram" &&
      !telegramPrelinkToken &&
      !tgInitData
    ) {
      setError("Сначала подключите Telegram.");
      return false;
    }
    if (contactMethod === "vk" && !vkIdPayload?.user_id) {
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

      if (contactMethod === "telegram") {
        if (tgInitData) {
          formData.append("tg_init_data", tgInitData);
        } else if (telegramPrelinkToken) {
          formData.append("telegram_prelink_token", telegramPrelinkToken);
        }
      }

      if (contactMethod === "vk" && vkIdPayload) {
        if (vkIdPayload.user_id)  formData.append("vk_user_id",     String(vkIdPayload.user_id));
        if (vkIdPayload.code)     formData.append("vk_id_code",     String(vkIdPayload.code));
        if (vkIdPayload.device_id) formData.append("vk_id_device_id", String(vkIdPayload.device_id));
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
