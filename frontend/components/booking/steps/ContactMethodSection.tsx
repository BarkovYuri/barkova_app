"use client";

import {
  AlertTriangle,
  CheckCircle2,
  Hourglass,
  MessageSquare,
  Users,
} from "lucide-react";

type Props = {
  vkIdReady: boolean;
  vkIdLoadError: string;
  vkIdAuthorized: boolean;
  vkIdContainerRef: React.RefObject<HTMLDivElement | null>;
};

export function ContactMethodSection({
  vkIdReady,
  vkIdLoadError,
  vkIdAuthorized,
  vkIdContainerRef,
}: Props) {
  return (
    <div className="animate-fade-in rounded-2xl border border-neutral-200 bg-gradient-to-b from-neutral-50 to-neutral-0 p-5 sm:p-6">
      <div className="mb-5">
        <p className="inline-flex items-center gap-2 text-ui-label uppercase text-neutral-500">
          <MessageSquare className="h-4 w-4 text-primary-600" strokeWidth={2} />
          Способ подтверждения записи
        </p>
        <p className="mt-2 text-sm text-neutral-600 leading-relaxed">
          Выберите удобный способ связи для подтверждения и отмены записи.
        </p>
      </div>

      <div className="animate-fade-in rounded-2xl border border-primary-100 bg-primary-50/50 p-5">
        <div className="flex items-start gap-3">
          <Users
            className="h-5 w-5 mt-0.5 text-primary-700"
            strokeWidth={2}
          />
          <p className="flex-1 text-sm leading-6 text-neutral-700">
            Войдите через VK ID для получения уведомлений и управления
            записью.
          </p>
        </div>

        <div className="mt-5">
          <div
            className="min-h-[60px] rounded-xl overflow-hidden"
            ref={vkIdContainerRef}
          />

          {vkIdLoadError ? (
            <div className="mt-3 animate-fade-in rounded-2xl border border-error-100 bg-error-50 px-4 py-3 text-sm text-error-700">
              <p className="inline-flex items-center gap-2 font-semibold">
                <AlertTriangle className="h-4 w-4" strokeWidth={2.25} />
                Ошибка загрузки VK
              </p>
              <p className="mt-1 text-error-600">{vkIdLoadError}</p>
            </div>
          ) : !vkIdReady ? (
            <div className="mt-3 skeleton h-12 flex items-center justify-center">
              <p className="text-sm text-neutral-600">Загружаем VK...</p>
            </div>
          ) : null}

          <div className="mt-4">
            <ConnectionPill
              connected={vkIdAuthorized}
              connectedLabel="VK подключён"
              pendingLabel="Ожидание подключения..."
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function ConnectionPill({
  connected,
  connectedLabel,
  pendingLabel,
}: {
  connected: boolean;
  connectedLabel: string;
  pendingLabel: string;
}) {
  return (
    <div
      className={`rounded-2xl px-4 py-3 text-sm font-semibold text-center transition-all border ${
        connected
          ? "border-secondary-300 bg-secondary-50 text-secondary-700"
          : "border-neutral-200 bg-neutral-50 text-neutral-500"
      }`}
    >
      <div className="flex items-center justify-center gap-2">
        {connected ? (
          <CheckCircle2 className="h-4 w-4" strokeWidth={2.5} />
        ) : (
          <Hourglass className="h-4 w-4" strokeWidth={2} />
        )}
        <span>{connected ? connectedLabel : pendingLabel}</span>
      </div>
    </div>
  );
}
