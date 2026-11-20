"use client";

import {
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  Hourglass,
  MessageSquare,
  Phone,
  Users,
} from "lucide-react";

import { reachGoal } from "../../../lib/metrika";
import type { ContactMethod } from "../../../lib/types";

type Props = {
  contactMethod: ContactMethod;
  setContactMethod: (method: ContactMethod) => void;
  vkIdReady: boolean;
  vkIdLoadError: string;
  vkIdAuthorized: boolean;
  vkIdContainerRef: React.RefObject<HTMLDivElement | null>;
  /** null — ещё не проверяли; true/false — может ли сообщество писать пациенту. */
  messagesAllowed: boolean | null;
  dialogUrl: string;
};

export function ContactMethodSection({
  contactMethod,
  setContactMethod,
  vkIdReady,
  vkIdLoadError,
  vkIdAuthorized,
  vkIdContainerRef,
  messagesAllowed,
  dialogUrl,
}: Props) {
  if (contactMethod === "phone") {
    return (
      <div className="animate-fade-in rounded-2xl border border-neutral-200 bg-gradient-to-b from-neutral-50 to-neutral-0 p-5 sm:p-6">
        <p className="inline-flex items-center gap-2 text-ui-label uppercase text-neutral-500">
          <Phone className="h-4 w-4 text-primary-600" strokeWidth={2} />
          Связь по телефону
        </p>
        <p className="mt-3 text-sm leading-6 text-neutral-700">
          Врач или администратор позвонит по указанному номеру, чтобы
          подтвердить запись. Напоминаний в VK не будет.
        </p>
        <button
          type="button"
          onClick={() => setContactMethod("vk")}
          className="mt-4 text-sm font-semibold text-primary-700 underline decoration-primary-300 underline-offset-2 hover:text-primary-800"
        >
          Подтвердить через VK
        </button>
      </div>
    );
  }

  const vkReady = vkIdAuthorized && messagesAllowed === true;

  return (
    <div className="animate-fade-in rounded-2xl border border-neutral-200 bg-gradient-to-b from-neutral-50 to-neutral-0 p-5 sm:p-6">
      <div className="mb-5">
        <p className="inline-flex items-center gap-2 text-ui-label uppercase text-neutral-500">
          <MessageSquare className="h-4 w-4 text-primary-600" strokeWidth={2} />
          Способ подтверждения записи
        </p>
        <p className="mt-2 text-sm text-neutral-600 leading-relaxed">
          Подтверждение, напоминание и отмена записи приходят в сообщения VK.
        </p>
      </div>

      <div className="animate-fade-in rounded-2xl border border-primary-100 bg-primary-50/50 p-5">
        <div className="flex items-start gap-3">
          <Users className="h-5 w-5 mt-0.5 text-primary-700" strokeWidth={2} />
          <p className="flex-1 text-sm leading-6 text-neutral-700">
            <span className="font-semibold">Шаг 1.</span> Войдите через VK ID.
          </p>
        </div>

        <div className="mt-4">
          <div className="min-h-[60px] rounded-xl overflow-hidden" ref={vkIdContainerRef} />

          {vkIdLoadError ? (
            <div className="mt-3 animate-fade-in rounded-2xl border border-error-100 bg-error-50 px-4 py-3 text-sm text-error-700">
              <p className="inline-flex items-center gap-2 font-semibold">
                <AlertTriangle className="h-4 w-4" strokeWidth={2.25} />
                Ошибка VK
              </p>
              <p className="mt-1 text-error-600">{vkIdLoadError}</p>
            </div>
          ) : !vkIdReady ? (
            <div className="mt-3 skeleton h-12 flex items-center justify-center">
              <p className="text-sm text-neutral-600">Загружаем VK...</p>
            </div>
          ) : null}
        </div>

        {vkIdAuthorized ? (
          <div className="mt-5 border-t border-primary-100 pt-5">
            <p className="text-sm leading-6 text-neutral-700">
              <span className="font-semibold">Шаг 2.</span> Разрешите сообществу
              писать вам, иначе подтверждение и напоминание не придут.
            </p>
            {messagesAllowed === true ? null : (
              <>
                <a
                  href={dialogUrl || "https://vk.com"}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => reachGoal("booking_open_vk_dialog")}
                  className="btn-primary mt-3 w-full justify-center text-sm"
                >
                  Открыть диалог с сообществом
                  <ExternalLink className="h-4 w-4" strokeWidth={2.5} />
                </a>
                <p className="mt-2 text-xs leading-5 text-neutral-500">
                  В открывшемся диалоге нажмите «Начать» или напишите любое
                  сообщение, затем вернитесь сюда. Статус обновится сам.
                </p>
              </>
            )}
          </div>
        ) : null}

        <div className="mt-4">
          <ConnectionPill
            connected={vkReady}
            label={
              vkReady
                ? "VK подключён, сообщения разрешены"
                : vkIdAuthorized
                ? messagesAllowed === null
                  ? "Проверяем доступ к сообщениям..."
                  : "Ждём разрешения сообщений..."
                : "Ожидание входа через VK ID..."
            }
          />
        </div>
      </div>

      <button
        type="button"
        onClick={() => setContactMethod("phone")}
        className="mt-4 text-sm font-semibold text-neutral-600 underline decoration-neutral-300 underline-offset-2 hover:text-neutral-800"
      >
        У меня нет VK, позвоните мне
      </button>
    </div>
  );
}

function ConnectionPill({ connected, label }: { connected: boolean; label: string }) {
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
        <span>{label}</span>
      </div>
    </div>
  );
}
