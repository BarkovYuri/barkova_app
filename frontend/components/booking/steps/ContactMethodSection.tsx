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
    <div className="animate-fade-in rounded-xl border border-neutral-200 bg-gradient-to-b from-neutral-50 to-white p-5 sm:p-6">
      <div className="mb-4">
        <p className="text-xs font-bold uppercase tracking-widest text-neutral-600">
          💬 Способ подтверждения записи
        </p>
        <p className="mt-2 text-sm text-neutral-600 leading-relaxed">
          Выберите удобный способ связи для подтверждения и отмены записи.
        </p>
      </div>

      {/* Contact Method Tabs */}
      <div className="mb-6 grid grid-cols-2 gap-3 sm:gap-4">
        <button
          type="button"
          onClick={() => setContactMethod("telegram")}
          className={`
            relative rounded-lg border-2 px-4 py-3 text-sm font-semibold
            transition-all duration-300 transform
            ${
              contactMethod === "telegram"
                ? "border-primary-600 bg-gradient-to-br from-primary-600 to-primary-700 text-white shadow-lg scale-105"
                : "border-neutral-300 bg-white text-neutral-700 hover:border-primary-400 hover:bg-primary-50 active:scale-95"
            }
          `}
        >
          <span className="text-lg">💬</span> Telegram
        </button>
        <button
          type="button"
          onClick={() => setContactMethod("vk")}
          className={`
            relative rounded-lg border-2 px-4 py-3 text-sm font-semibold
            transition-all duration-300 transform
            ${
              contactMethod === "vk"
                ? "border-primary-600 bg-gradient-to-br from-primary-600 to-primary-700 text-white shadow-lg scale-105"
                : "border-neutral-300 bg-white text-neutral-700 hover:border-primary-400 hover:bg-primary-50 active:scale-95"
            }
          `}
        >
          <span className="text-lg">👥</span> VK
        </button>
      </div>

      {/* Method-specific content */}
      <div key={contactMethod} className="animate-slide-in-down">
        {contactMethod === "telegram" ? (
          <div className="rounded-lg border border-blue-200 bg-gradient-to-br from-blue-50 to-white p-5">
            <div className="flex items-start gap-3">
              <span className="text-2xl">💬</span>
              <div className="flex-1">
                <p className="text-sm leading-6 text-neutral-700">
                  Подключите Telegram для получения уведомлений о подтверждении и отмене записи.
                </p>
              </div>
            </div>

            <div className="mt-4 space-y-3">
              <button
                type="button"
                onClick={onTelegramConnect}
                disabled={loadingTelegramLink}
                className={`
                  w-full inline-flex items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-semibold
                  transition-all duration-300 transform
                  ${
                    loadingTelegramLink
                      ? "bg-blue-300 text-white cursor-not-allowed"
                      : "bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-md hover:shadow-lg hover:scale-105 active:scale-95"
                  }
                `}
              >
                {loadingTelegramLink ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    <span>Создаём ссылку...</span>
                  </>
                ) : (
                  <>
                    <span>→</span>
                    <span>Подключить Telegram</span>
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={onCheckTelegram}
                disabled={!telegramPrelinkToken}
                className={`
                  w-full rounded-lg border-2 px-4 py-3 text-sm font-semibold
                  transition-all duration-300
                  ${
                    !telegramPrelinkToken
                      ? "border-neutral-200 bg-neutral-50 text-neutral-400 cursor-not-allowed"
                      : "border-neutral-300 bg-white text-neutral-700 hover:border-primary-400 hover:bg-primary-50"
                  }
                `}
              >
                🔍 Проверить подключение
              </button>

              <div
                className={`
                  rounded-lg px-4 py-3 text-sm font-semibold text-center transition-all
                  ${
                    telegramConnected
                      ? "border-2 border-green-500 bg-green-50 text-green-700"
                      : "border-2 border-neutral-300 bg-neutral-50 text-neutral-500"
                  }
                `}
              >
                {telegramConnected ? (
                  <div className="flex items-center justify-center gap-2">
                    <span>✓</span>
                    <span>Telegram подключён</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-2">
                    <span>⏳</span>
                    <span>Ожидание подключения...</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-lg border border-primary-200 bg-gradient-to-br from-primary-50 to-white p-5">
            <div className="flex items-start gap-3">
              <span className="text-2xl">👥</span>
              <div className="flex-1">
                <p className="text-sm leading-6 text-neutral-700">
                  Войдите через VK ID для получения уведомлений и управления записью.
                </p>
              </div>
            </div>

            <div className="mt-4">
              <div
                className="min-h-[60px] rounded-lg overflow-hidden"
                ref={vkIdContainerRef}
              />

              {vkIdLoadError ? (
                <div className="mt-3 animate-fade-in rounded-lg border-l-4 border-red-500 bg-red-50 px-4 py-3 text-sm text-red-800">
                  <p className="font-semibold">Ошибка загрузки VK</p>
                  <p>{vkIdLoadError}</p>
                </div>
              ) : !vkIdReady ? (
                <div className="mt-3 animate-pulse rounded-lg bg-neutral-200 h-12 flex items-center justify-center">
                  <p className="text-sm text-neutral-600">Загружаем VK...</p>
                </div>
              ) : null}

              <div
                className={`
                  mt-4 rounded-lg px-4 py-3 text-sm font-semibold text-center transition-all
                  ${
                    vkIdAuthorized
                      ? "border-2 border-green-500 bg-green-50 text-green-700"
                      : "border-2 border-neutral-300 bg-neutral-50 text-neutral-500"
                  }
                `}
              >
                {vkIdAuthorized ? (
                  <div className="flex items-center justify-center gap-2">
                    <span>✓</span>
                    <span>VK подключён</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-2">
                    <span>⏳</span>
                    <span>Ожидание подключения...</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
