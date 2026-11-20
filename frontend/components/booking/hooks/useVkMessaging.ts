"use client";

import { useCallback, useEffect, useState } from "react";

import { fetchAPI } from "../../../lib/api";

type MessagingStatus = {
  can_message_user: boolean;
  dialog_url: string;
};

const POLL_INTERVAL_MS = 3000;
const POLL_LIMIT_MS = 5 * 60 * 1000;

/**
 * Проверяет, может ли сообщество писать пациенту в VK.
 *
 * Вход через VK ID такого права не даёт: пока пациент сам не написал
 * сообществу или не разрешил сообщения, ни подтверждение записи, ни
 * напоминание до него не дойдут. Хук опрашивает статус, пока пациент
 * открывает диалог с сообществом, и перепроверяет при возврате на вкладку.
 */
export function useVkMessaging(vkUserId: string | number | null | undefined) {
  const [allowed, setAllowed] = useState<boolean | null>(null);
  const [dialogUrl, setDialogUrl] = useState("");

  const check = useCallback(() => {
    if (!vkUserId) return;
    fetchAPI(`/appointments/vk/messaging-status?vk_user_id=${encodeURIComponent(String(vkUserId))}`)
      .then((raw) => {
        const data = raw as MessagingStatus | null;
        if (!data) return;
        setAllowed(Boolean(data.can_message_user));
        if (data.dialog_url) setDialogUrl(data.dialog_url);
      })
      // Сеть или лимит запросов — просто попробуем на следующем тике.
      .catch(() => {});
  }, [vkUserId]);

  useEffect(() => {
    if (!vkUserId) return;
    const first = window.setTimeout(check, 0);
    return () => window.clearTimeout(first);
  }, [vkUserId, check]);

  useEffect(() => {
    if (!vkUserId || allowed) return;
    const startedAt = Date.now();
    const timer = window.setInterval(() => {
      if (document.visibilityState !== "visible") return;
      if (Date.now() - startedAt > POLL_LIMIT_MS) {
        window.clearInterval(timer);
        return;
      }
      check();
    }, POLL_INTERVAL_MS);

    const onFocus = () => check();
    window.addEventListener("focus", onFocus);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("focus", onFocus);
    };
  }, [vkUserId, allowed, check]);

  return { allowed, dialogUrl, recheck: check };
}
