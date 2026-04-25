"use client";

import type { Slot, ContactMethod } from "../../../lib/types";

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
  const inputCls = "w-full rounded-xl border-2 border-neutral-200 px-4 py-3 text-base text-neutral-900 outline-none transition-all duration-300 placeholder:text-neutral-400 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 focus:shadow-lg hover:border-neutral-300";
  const inputErrorCls = "border-red-500 focus:border-red-600 focus:ring-red-100";
  const inputSuccessCls = "border-green-500 focus:border-green-600 focus:ring-green-100";

  return (
    <>
      {selectedSlot ? (
        <div className="mb-6 animate-fade-in rounded-xl border-2 border-green-200 bg-gradient-to-r from-green-50 to-emerald-50 p-4 shadow-sm">
          <div className="flex items-start gap-3">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-green-500 text-white text-sm font-bold flex-shrink-0 mt-0.5">
              ✓
            </div>
            <div className="flex-1">
              <p className="font-semibold text-green-900">Вы выбрали:</p>
              <p className="mt-1 text-sm text-green-800">
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
            Ваше имя <span className="text-red-500">*</span>
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
            <p className="mt-1.5 text-xs text-green-600 flex items-center gap-1">
              <span>✓</span> Имя принято
            </p>
          )}
        </div>

        {/* Phone Input */}
        <div className="animate-fade-in" style={{ animationDelay: '0.15s' }}>
          <label className="mb-2.5 block text-sm font-semibold text-neutral-900">
            Телефон <span className="text-red-500">*</span>
          </label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+7 (___) ___-__-__"
            required
            className={`${inputCls} ${phone && !phone.trim() ? inputErrorCls : phone && phone.trim() ? inputSuccessCls : ""}`}
          />
          {phone && phone.trim() && (
            <p className="mt-1.5 text-xs text-green-600 flex items-center gap-1">
              <span>✓</span> Телефон принят
            </p>
          )}
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
            className={`w-full rounded-xl border-2 border-neutral-200 px-4 py-3 text-base text-neutral-900 outline-none transition-all duration-300 placeholder:text-neutral-400 focus:border-primary-600 focus:ring-2 focus:ring-primary-100 focus:shadow-lg hover:border-neutral-300 resize-none`}
          />
          {reason && reason.trim() && (
            <p className="mt-1.5 text-xs text-green-600 flex items-center gap-1">
              <span>✓</span> Описание добавлено ({reason.length} символов)
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
            className="block w-full rounded-xl border-2 border-dashed border-neutral-300 bg-white px-4 py-6 text-sm text-neutral-600 transition-colors hover:border-primary-400 hover:bg-primary-50 focus:border-primary-600 focus:outline-none file:mr-4 file:rounded-lg file:border-0 file:bg-primary-100 file:px-3 file:py-2 file:text-sm file:font-medium file:text-primary-700 file:cursor-pointer hover:file:bg-primary-200"
          />
          {files && files.length > 0 && (
            <p className="mt-2 text-xs text-green-600 flex items-center gap-1">
              <span>✓</span> Загружено файлов: {files.length}
            </p>
          )}
        </div>

        {/* Consents Section */}
        <div className="animate-fade-in rounded-xl bg-neutral-50 p-5 border border-neutral-200" style={{ animationDelay: '0.3s' }}>
          <p className="mb-4 text-sm font-semibold text-neutral-900">Согласия <span className="text-red-500">*</span></p>
          <div className="space-y-3">
            {[
              { checked: consentGiven, setter: setConsentGiven, label: "Согласен(на) на обработку персональных данных", icon: "📋" },
              { checked: privacyAccepted, setter: setPrivacyAccepted, label: "Принимаю политику конфиденциальности", icon: "🔒" },
              { checked: offerAccepted, setter: setOfferAccepted, label: "Принимаю условия оферты", icon: "📜" },
            ].map(({ checked, setter, label, icon }) => (
              <label key={label} className="flex items-start gap-3 cursor-pointer group">
                <div className="relative flex h-5 w-5 items-center justify-center flex-shrink-0 mt-0.5">
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={(e) => setter(e.target.checked)}
                    className="h-5 w-5 rounded border-2 border-neutral-300 text-primary-600 transition-all duration-200 focus:ring-2 focus:ring-primary-200 cursor-pointer accent-primary-600"
                  />
                  {checked && (
                    <div className="absolute inset-0 flex items-center justify-center animate-pulse">
                      <span className="text-xs text-white">✓</span>
                    </div>
                  )}
                </div>
                <span className={`text-sm transition-colors ${checked ? "text-neutral-900 font-medium" : "text-neutral-700"}`}>
                  {label}
                </span>
              </label>
            ))}
          </div>
        </div>

        {errorText ? (
          <div className="animate-fade-in rounded-xl border-l-4 border-red-500 bg-red-50 px-4 py-3 text-sm text-red-800 shadow-sm">
            <div className="flex items-start gap-3">
              <span className="text-lg">⚠️</span>
              <div>
                <p className="font-semibold text-red-900">Ошибка при отправке</p>
                <p className="mt-1 text-red-700">{errorText}</p>
              </div>
            </div>
          </div>
        ) : null}

        <button
          type="submit"
          disabled={submitting}
          className={`
            group relative w-full min-h-14 px-6 py-4 font-semibold text-base rounded-xl
            transition-all duration-300 transform
            ${submitting
              ? "bg-neutral-300 text-neutral-600 cursor-not-allowed"
              : "bg-gradient-to-r from-primary-600 to-secondary-600 text-white shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
            }
            flex items-center justify-center gap-2
          `}
        >
          {submitting ? (
            <>
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
              <span>Отправляем...</span>
            </>
          ) : (
            <>
              <span>✓</span>
              <span>Записаться на консультацию</span>
            </>
          )}
        </button>
      </div>
    </>
  );
}
