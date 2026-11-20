"use client";

import { useEffect, useRef, useState } from "react";

export type VkIdPayload = {
  user_id?: string | number;
  access_token?: string;
  [key: string]: unknown;
};

// Реальный production App ID — запасной вариант, если CI не пробросил
// NEXT_PUBLIC_VK_APP_ID в build.
const VK_APP_ID = process.env.NEXT_PUBLIC_VK_APP_ID || "54546774";
const VK_REDIRECT_URL =
  process.env.NEXT_PUBLIC_VK_ID_REDIRECT_URL ||
  "https://doctor-barkova.ru/auth/vk/callback";

/**
 * Кнопка «Войти через VK ID».
 *
 * SDK подключается из npm-пакета @vkid/sdk с фиксированной версией и
 * собирается вместе с сайтом. Раньше он грузился с unpkg.com без версии:
 * в РФ это 5–10 секунд ожидания, а любое обновление SDK у VK могло
 * незаметно сломать форму записи.
 */
export function useVkId(active: boolean) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [ready, setReady] = useState(false);
  const [authorized, setAuthorized] = useState(false);
  const [payload, setPayload] = useState<VkIdPayload | null>(null);
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    if (!active) return;

    let disposed = false;
    const container = containerRef.current;

    (async () => {
      let VKID: typeof import("@vkid/sdk");
      try {
        VKID = await import("@vkid/sdk");
      } catch {
        if (!disposed) setLoadError("Не удалось загрузить VK ID. Обновите страницу.");
        return;
      }
      if (disposed || !container || container.childNodes.length > 0) return;

      try {
        VKID.Config.init({
          app: Number(VK_APP_ID),
          redirectUrl: VK_REDIRECT_URL,
          responseMode: VKID.ConfigResponseMode.Callback,
          source: VKID.ConfigSource.LOWCODE,
          scope: "",
        });

        const oneTap = new VKID.OneTap();
        oneTap
          .render({
            container,
            fastAuthEnabled: false,
            showAlternativeLogin: true,
            styles: { borderRadius: 15, height: 50 },
          })
          .on(VKID.WidgetEvents.ERROR, (err: unknown) => {
            console.error("VK ID widget error", err);
          })
          .on(
            VKID.OneTapInternalEvents.LOGIN_SUCCESS,
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            (p: any) => {
              const code = p?.code;
              const deviceId = p?.device_id;
              if (!code || !deviceId) {
                setLoadError("VK ID не вернул code или device_id.");
                return;
              }
              // VK ID 2.x использует PKCE: code_verifier живёт внутри SDK,
              // поэтому обменять code на токен может только сам SDK.
              // Бэкенд проверяет полученный токен у VK.
              VKID.Auth.exchangeCode(code, deviceId)
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                .then((data: any) => {
                  const userId = data?.user_id ?? data?.user?.id ?? p?.user_id;
                  const accessToken = data?.access_token;
                  if (!userId || !accessToken) {
                    setAuthorized(false);
                    setPayload(null);
                    setLoadError("VK ID не вернул токен авторизации. Попробуйте ещё раз.");
                    return;
                  }
                  setAuthorized(true);
                  setPayload({ user_id: userId, access_token: accessToken });
                  setLoadError("");
                })
                .catch(() => {
                  setAuthorized(false);
                  setPayload(null);
                  setLoadError("Не удалось завершить вход через VK ID.");
                });
            }
          );

        setReady(true);
      } catch {
        setLoadError("Не удалось инициализировать VK ID.");
      }
    })();

    return () => {
      disposed = true;
      if (container) container.innerHTML = "";
      setReady(false);
    };
  }, [active]);

  return { containerRef, ready, authorized, payload, loadError };
}
