"use client";

import type { ContactMethod } from "../../../lib/types";

type Props = {
  contactMethod: ContactMethod;
  setContactMethod: (v: ContactMethod) => void;
  onTelegramConnect: () => void;
  onCheckTelegram: () => void;
  loadingTelegramLink: boolean;
  telegramConnected: boolean;
  telegramPrelinkToken: string;
  vkIdReady: boolean;
  vkIdLoadError: string;
  vkIdAuthorized: boolean;
  vkIdContainerRef: React.RefObject<HTMLDivElement | null>;
};

export function ContactMethodSection({
  contactMethod,
  setContactMethod,
  onTelegramConnect,
  onCheckTelegram,
  loadingTelegramLink,
  telegramConnected,
  telegramPrelinkToken,
  vkIdReady,
  vkIdLoadError,
  vkIdAuthorized,
  vkIdContainerRef,
}: Props) {
  return (
    <div className="rounded-3xl border border-sky-100 bg-sky-50/70 p-4 sm:p-5">
      <p className="text-sm font-semibold uppercase tracking-[0.16em] text-sky-700">Подтверждение / отмена записи</p>
      <p className="mt-2 text-sm leading-6 text-gray-600">
        Выберите удобный способ связи, чтобы врач или администратор могли подтвердить или при необходимости отменить запись.
      </p>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <button
          type="button"
          onClick={() => setContactMethod("telegram")}
          className={`rounded-2xl border px-4 py-3 text-sm font-medium transition ${
            contactMethod === "telegram"
              ? "border-sky-600 bg-sky-600 text-white"
              : "border-gray-200 bg-white text-gray-700 hover:border-sky-300 hover:bg-sky-50"
          }`}
        >
          Telegram
        </button>
        <button
          type="button"
          onClick={() => setContactMethod("vk")}
          className={`rounded-2xl border px-4 py-3 text-sm font-medium transition ${
            contactMethod === "vk"
              ? "border-sky-600 bg-sky-600 text-white"
              : "border-gray-200 bg-white text-gray-700 hover:border-sky-300 hover:bg-sky-50"
          }`}
        >
          VK
        </button>
      </div>

      <div key={contactMethod}>
        {contactMethod === "telegram" ? (
          <div className="mt-4 rounded-2xl border border-blue-100 bg-blue-50 px-4 py-4">
            <p className="text-sm leading-6 text-gray-700">
              Сначала подключите Telegram, чтобы получать уведомления о записи, подтверждении и отмене консультации.
            </p>
            <div className="mt-4 flex flex-col gap-3">
              <button
                type="button"
                onClick={onTelegramConnect}
                disabled={loadingTelegramLink}
                className="inline-flex items-center justify-center rounded-2xl bg-blue-500 px-5 py-3.5 text-sm font-medium text-white transition hover:bg-blue-600 disabled:cursor-not-allowed disabled:bg-blue-300"
              >
                {loadingTelegramLink ? "Создаём ссылку..." : "Подключить Telegram"}
              </button>
              <button
                type="button"
                onClick={onCheckTelegram}
                disabled={!telegramPrelinkToken}
                className="inline-flex items-center justify-center rounded-2xl border border-gray-200 bg-white px-5 py-3.5 text-sm font-medium text-gray-700 transition hover:border-sky-300 hover:bg-sky-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Проверить подключение
              </button>
              <div className={`inline-flex items-center justify-center rounded-2xl px-4 py-3 text-sm font-medium ${
                telegramConnected ? "bg-green-100 text-green-700" : "border border-gray-200 bg-white text-gray-500"
              }`}>
                {telegramConnected ? "Telegram подключён" : "Telegram ещё не подключён"}
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-4 rounded-2xl border border-blue-100 bg-blue-50 px-5 py-5">
            <p className="text-sm leading-6 text-gray-700">
              Войдите через VK ID, чтобы получать уведомления и управлять записью во ВКонтакте.
            </p>
            <div className="mt-4 min-h-[50px]" ref={vkIdContainerRef} />
            {vkIdLoadError ? (
              <div className="mt-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{vkIdLoadError}</div>
            ) : !vkIdReady ? (
              <p className="mt-3 text-sm text-gray-500">Загружаем VK...</p>
            ) : null}
            <div className={`mt-4 inline-flex items-center justify-center rounded-2xl px-4 py-3 text-sm font-medium ${
              vkIdAuthorized ? "bg-green-100 text-green-700" : "border border-gray-200 bg-white text-gray-500"
            }`}>
              {vkIdAuthorized ? "VK подключён" : "Войдите через VK ID"}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
