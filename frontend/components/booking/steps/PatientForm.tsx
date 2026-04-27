"use client";

import {
  AlertTriangle,
  CheckCircle2,
  FileText,
  Loader2,
  ScrollText,
  ShieldCheck,
} from "lucide-react";
import { useState } from "react";

import { formatPhone, isPhoneValid } from "../../../lib/phone";
import type { Slot } from "../../../lib/types";
import { LegalModal } from "../LegalModal";

type LegalDocType = "offer" | "privacy" | "consent";

function formatDateLong(dateString: string) {
  const date = new Date(`${dateString}T00:00:00`);
  return new Intl.DateTimeFormat("ru-RU", {
    weekday: "long", day: "numeric", month: "long",
  }).format(date);
}

type Props = {
  selectedDate: string;
  selectedSlot: Slot | null;
  name: string; setName: (v: string) => void;
  phone: string; setPhone: (v: string) => void;
  reason: string; setReason: (v: string) => void;
  consentGiven: boolean; setConsentGiven: (v: boolean) => void;
  privacyAccepted: boolean; setPrivacyAccepted: (v: boolean) => void;
  offerAccepted: boolean; setOfferAccepted: (v: boolean) => void;
  files: FileList | null; setFiles: (f: FileList | null) => void;
  children: React.ReactNode;
  errorText: string;
  submitting: boolean;
};

export function PatientForm({
  selectedDate, selectedSlot,
  name, setName, phone, setPhone, reason, setReason,
  consentGiven, setConsentGiven,
  privacyAccepted, setPrivacyAccepted,
  offerAccepted, setOfferAccepted,
  files, setFiles,
  children,
  errorText,
  submitting,
}: Props) {
  // ── Модалка legal ────────────────────────────────────────────
  const [legalModal, setLegalModal] = useState<LegalDocType | null>(null);

  // ── Маска телефона ──────────────────────────────────────────
  function handlePhoneChange(e: React.ChangeEvent<HTMLInputElement>) {
    const formatted = formatPhone(e.target.value);
    setPhone(formatted);
  }

  const phoneValid = isPhoneValid(phone);
  const phoneInvalid = phone.length > 0 && !phoneValid;
  const inputCls =
    "w-full rounded-2xl border border-neutral-300 bg-neutral-0 px-4 py-3.5 text-base text-neutral-900 outline-none transition-all duration-200 placeholder:text-neutral-400 focus:border-primary-500 focus:ring-4 focus:ring-primary-100 hover:border-neutral-400";
  const inputErrorCls =
    "border-error-600 focus:border-error-700 focus:ring-error-100";
  const inputSuccessCls =
    "border-secondary-500 focus:border-secondary-600 focus:ring-secondary-100";

  return (
    <>
      {selectedSlot ? (
        <div className="mb-6 animate-fade-in rounded-2xl border border-secondary-200 bg-secondary-50 p-4 shadow-sm">
          <div className="flex items-start gap-3">
            <CheckCircle2
              className="h-5 w-5 text-secondary-600 flex-shrink-0 mt-0.5"
              strokeWidth={2.25}
            />
            <div className="flex-1">
              <p className="font-semibold text-secondary-800">Вы выбрали:</p>
              <p className="mt-1 text-sm text-secondary-700">
                {formatDateLong(selectedDate)} в {selectedSlot.start_time.slice(0, 5)}
              </p>
            </div>
          </div>
        </div>
      ) : null}

      <div className="space-y-5">
        {/* Name Input */}
        <div className="animate-fade-in" style={{ animationDelay: '0.1s' }}>
          <label className="mb-2.5 block text-sm font-semibold text-neutral-900">
            Ваше имя <span className="text-accent-600">*</span>
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Например, Елена Сергеевна"
            required
            className={`${inputCls} ${name && !name.trim() ? inputErrorCls : name && name.trim() ? inputSuccessCls : ""}`}
          />
          {name && name.trim() && (
            <p className="mt-1.5 text-xs text-secondary-700 flex items-center gap-1">
              <CheckCircle2 className="h-3.5 w-3.5" strokeWidth={2.5} />
              Имя принято
            </p>
          )}
        </div>

        {/* Phone Input — с маской и валидацией */}
        <div className="animate-fade-in" style={{ animationDelay: "0.15s" }}>
          <label className="mb-2.5 block text-sm font-semibold text-neutral-900">
            Телефон <span className="text-accent-600">*</span>
          </label>
          <input
            type="tel"
            inputMode="numeric"
            autoComplete="tel"
            value={phone}
            onChange={handlePhoneChange}
            placeholder="+7 (___) ___-__-__"
            required
            className={`${inputCls} ${
              phoneInvalid
                ? inputErrorCls
                : phoneValid
                ? inputSuccessCls
                : ""
            }`}
          />
          {phoneValid ? (
            <p className="mt-1.5 text-xs text-secondary-700 flex items-center gap-1">
              <CheckCircle2 className="h-3.5 w-3.5" strokeWidth={2.5} />
              Телефон принят
            </p>
          ) : phoneInvalid ? (
            <p className="mt-1.5 text-xs text-error-600 flex items-center gap-1">
              <AlertTriangle className="h-3.5 w-3.5" strokeWidth={2.5} />
              Введите 10 цифр номера
            </p>
          ) : null}
        </div>

        {/* Reason Input */}
        <div className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
          <label className="mb-2.5 block text-sm font-semibold text-neutral-900">
            Причина обращения <span className="text-neutral-400">(опционально)</span>
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Кратко опишите вопрос или симптомы..."
            rows={4}
            className={`${inputCls} resize-none`}
          />
          {reason && reason.trim() && (
            <p className="mt-1.5 text-xs text-secondary-700 flex items-center gap-1">
              <CheckCircle2 className="h-3.5 w-3.5" strokeWidth={2.5} />
              Описание добавлено ({reason.length} символов)
            </p>
          )}
        </div>

        {/* File Upload */}
        <div className="animate-fade-in" style={{ animationDelay: '0.25s' }}>
          <label className="mb-2.5 block text-sm font-semibold text-neutral-900">
            Приложить файлы <span className="text-neutral-400">(опционально)</span>
          </label>
          <input
            type="file"
            multiple
            onChange={(e) => setFiles(e.target.files)}
            className="block w-full rounded-2xl border border-dashed border-neutral-300 bg-neutral-0 px-4 py-6 text-sm text-neutral-600 transition-colors hover:border-primary-400 hover:bg-primary-50 focus:border-primary-500 focus:outline-none file:mr-4 file:rounded-lg file:border-0 file:bg-primary-100 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-primary-700 file:cursor-pointer hover:file:bg-primary-200"
          />
          {files && files.length > 0 && (
            <p className="mt-2 text-xs text-secondary-700 flex items-center gap-1">
              <CheckCircle2 className="h-3.5 w-3.5" strokeWidth={2.5} />
              Загружено файлов: {files.length}
            </p>
          )}
        </div>

        {/* Consents Section */}
        <div className="animate-fade-in rounded-2xl bg-neutral-50 p-5 border border-neutral-200" style={{ animationDelay: '0.3s' }}>
          <p className="mb-4 text-sm font-semibold text-neutral-900">
            Согласия <span className="text-accent-600">*</span>
          </p>
          <div className="space-y-3">
            {(
              [
                {
                  checked: consentGiven,
                  setter: setConsentGiven,
                  label: "Согласен(на) на обработку персональных данных",
                  Icon: FileText,
                  doc: "consent" as LegalDocType,
                },
                {
                  checked: privacyAccepted,
                  setter: setPrivacyAccepted,
                  label: "Принимаю политику конфиденциальности",
                  Icon: ShieldCheck,
                  doc: "privacy" as LegalDocType,
                },
                {
                  checked: offerAccepted,
                  setter: setOfferAccepted,
                  label: "Принимаю условия оферты",
                  Icon: ScrollText,
                  doc: "offer" as LegalDocType,
                },
              ]
            ).map(({ checked, setter, label, Icon, doc }) => (
              <div
                key={label}
                className="flex items-start gap-3"
              >
                <input
                  id={`consent-${doc}`}
                  type="checkbox"
                  checked={checked}
                  onChange={(e) => setter(e.target.checked)}
                  className="mt-0.5 h-5 w-5 rounded border-2 border-neutral-300 text-primary-600 transition-all duration-200 focus:ring-2 focus:ring-primary-200 cursor-pointer accent-primary-600 flex-shrink-0"
                />
                <label
                  htmlFor={`consent-${doc}`}
                  className="flex flex-1 flex-wrap items-center gap-x-2 gap-y-1 text-sm cursor-pointer"
                >
                  <span
                    className={`flex items-center gap-2 transition-colors ${
                      checked
                        ? "text-neutral-900 font-medium"
                        : "text-neutral-700"
                    }`}
                  >
                    <Icon
                      className={`h-4 w-4 ${
                        checked ? "text-primary-700" : "text-neutral-400"
                      }`}
                      strokeWidth={2}
                    />
                    {label}
                  </span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.preventDefault();
                      setLegalModal(doc);
                    }}
                    className="text-xs font-semibold text-primary-700 hover:text-primary-800 underline decoration-primary-300 underline-offset-2"
                  >
                    Прочитать
                  </button>
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Способ подтверждения (Telegram / VK) — рендерится из родителя */}
        <div className="animate-fade-in" style={{ animationDelay: "0.35s" }}>
          {children}
        </div>

        {errorText ? (
          <div className="animate-fade-in rounded-2xl border border-error-100 bg-error-50 px-4 py-3 text-sm text-error-700 shadow-sm">
            <div className="flex items-start gap-3">
              <AlertTriangle
                className="h-5 w-5 text-error-600 flex-shrink-0 mt-0.5"
                strokeWidth={2.25}
              />
              <div>
                <p className="font-semibold text-error-700">
                  Ошибка при отправке
                </p>
                <p className="mt-1 text-error-600">{errorText}</p>
              </div>
            </div>
          </div>
        ) : null}

        <button
          type="submit"
          disabled={submitting}
          className={`
            group relative w-full min-h-14 px-6 py-4 font-semibold text-base rounded-2xl
            transition-all duration-300 transform
            ${submitting
              ? "bg-neutral-300 text-neutral-600 cursor-not-allowed"
              : "bg-primary-600 hover:bg-primary-700 text-neutral-0 shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0"
            }
            flex items-center justify-center gap-2
          `}
        >
          {submitting ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" strokeWidth={2.5} />
              <span>Отправляем...</span>
            </>
          ) : (
            <>
              <CheckCircle2 className="h-5 w-5" strokeWidth={2.5} />
              <span>Записаться на консультацию</span>
            </>
          )}
        </button>
      </div>

      {/* Legal modal */}
      <LegalModal
        open={legalModal !== null}
        docType={legalModal}
        onClose={() => setLegalModal(null)}
      />
    </>
  );
}
