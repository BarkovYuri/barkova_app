"use client";

import { useCallback, useEffect, useRef } from "react";

import { fetchAPI } from "../../../lib/api";

type Held = { slotId: number; token: string };

type ReserveResponse = {
  slot_id: number;
  reservation_token: string;
  expires_in: number;
};

/**
 * Soft-reservation: при выборе слота держим за пользователем 5 минут.
 * При смене слота освобождаем предыдущий. На размонтировании — тоже,
 * чтобы не висело лишних 5 минут после ухода со страницы.
 *
 * Если reserve вернул 409 — слот уже занят кем-то параллельно. В этом
 * случае onConflict даёт UI возможность сбросить выбор и обновить список.
 */
export function useSlotReservation({
  selectedSlotId,
  onConflict,
}: {
  selectedSlotId: number | null;
  onConflict?: () => Promise<void> | void;
}) {
  const heldRef = useRef<Held | null>(null);

  const release = useCallback(async (held: Held | null) => {
    if (!held) return;
    try {
      await fetchAPI(`/slots/${held.slotId}/release`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ reservation_token: held.token }),
      });
    } catch {
      // best-effort: TTL всё равно истечёт за 5 минут
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    const previous = heldRef.current;

    if (previous && previous.slotId === selectedSlotId) {
      return;
    }

    if (selectedSlotId == null) {
      if (previous) {
        heldRef.current = null;
        release(previous);
      }
      return;
    }

    (async () => {
      try {
        const data = (await fetchAPI(`/slots/${selectedSlotId}/reserve`, {
          method: "POST",
        })) as ReserveResponse | null;

        if (cancelled) {
          if (data) {
            release({ slotId: data.slot_id, token: data.reservation_token });
          }
          return;
        }

        if (data) {
          heldRef.current = {
            slotId: data.slot_id,
            token: data.reservation_token,
          };
          // Старый лок отпускаем после успешного нового, чтобы не было
          // момента «оба свободны → третий может забрать».
          if (previous) release(previous);
        }
      } catch (err) {
        if (cancelled) return;
        // 409 conflict — слот уже занят; UI должен обновить список и
        // снять выбор.
        const status = (err as { status?: number })?.status;
        if (status === 409 && onConflict) {
          await onConflict();
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [selectedSlotId, onConflict, release]);

  // Освобождаем лок при размонтировании компонента (уход со страницы).
  useEffect(() => {
    return () => {
      const held = heldRef.current;
      if (held) {
        heldRef.current = null;
        // Используем navigator.sendBeacon-подобный подход: fire-and-forget.
        // fetchAPI ничего не ждёт, await не нужен.
        fetchAPI(`/slots/${held.slotId}/release`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ reservation_token: held.token }),
        }).catch(() => {});
      }
    };
  }, []);

  const getToken = useCallback(
    (slotId: number | null): string => {
      if (slotId == null) return "";
      const held = heldRef.current;
      if (held && held.slotId === slotId) return held.token;
      return "";
    },
    [],
  );

  const clear = useCallback(() => {
    const held = heldRef.current;
    heldRef.current = null;
    return release(held);
  }, [release]);

  return { getToken, clear };
}
