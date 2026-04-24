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
  const inputCls = "w-full rounded-2xl border border-gray-200 px-4 py-3.5 text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-sky-500 focus:ring-4 focus:ring-sky-100";

  return (
    <>
      {selectedSlot ? (
        <div className="mb-5 rounded-3xl border border-sky-100 bg-sky-50 p-4 text-sm text-gray-700">
          <p className="font-medium text-gray-900">Вы выбрали:</p>
          <p className="mt-2">
            {formatDateLong(selectedDate)} в {selectedSlot.start_time.slice(0, 5)}
          </p>
        </div>
      ) : null}

      <div className="space-y-4 sm:space-y-5">
        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">Ваше имя</label>
          <input
            type="text" value={name} onChange={(e) => setName(e.target.value)}
            placeholder="Например, Елена" required className={inputCls}
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">Телефон</label>
          <input
            type="tel" value={phone} onChange={(e) => setPhone(e.target.value)}
            placeholder="+7 (___) ___-__-__" required className={inputCls}
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">Причина обращения</label>
          <textarea
            value={reason} onChange={(e) => setReason(e.target.value)}
            placeholder="Кратко опишите вопрос" rows={4}
            className="w-full rounded-2xl border border-gray-200 px-4 py-3 text-gray-900 outline-none transition placeholder:text-gray-400 focus:border-sky-500 focus:ring-4 focus:ring-sky-100"
          />
        </div>

        {/* Способ связи — слот для ContactMethodSection */}
        {children}

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">Файлы (по желанию)</label>
          <input
            type="file" multiple
            onChange={(e) => setFiles(e.target.files)}
            className="block w-full rounded-2xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-600 file:mr-4 file:rounded-xl file:border-0 file:bg-sky-100 file:px-4 file:py-2 file:text-sm file:font-medium file:text-sky-700 hover:file:bg-sky-200"
          />
        </div>

        <div className="space-y-3 rounded-3xl bg-gray-50 p-4">
          {[
            { checked: consentGiven,     setter: setConsentGiven,     label: "Согласен(на) на обработку персональных данных" },
            { checked: privacyAccepted,  setter: setPrivacyAccepted,  label: "Принимаю политику конфиденциальности" },
            { checked: offerAccepted,    setter: setOfferAccepted,    label: "Принимаю условия оферты" },
          ].map(({ checked, setter, label }) => (
            <label key={label} className="flex items-start gap-3 text-sm text-gray-600">
              <input
                type="checkbox" checked={checked}
                onChange={(e) => setter(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-gray-300 text-sky-600 focus:ring-sky-500"
              />
              <span>{label}</span>
            </label>
          ))}
        </div>

        {errorText ? (
          <div className="rounded-2xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
            {errorText}
          </div>
        ) : null}

        <button
          type="submit" disabled={submitting}
          className="inline-flex min-h-[56px] w-full items-center justify-center rounded-2xl bg-sky-600 px-6 py-4 text-base font-medium text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-sky-300"
        >
          {submitting ? "Отправляем..." : "Записаться на консультацию"}
        </button>
      </div>
    </>
  );
}
