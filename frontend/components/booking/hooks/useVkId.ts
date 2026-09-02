"use client";

import { useEffect, useRef, useState } from "react";

export type VkIdPayload = {
  user_id?: string | number;
  access_token?: string;
  [key: string]: unknown;
};

export function useVkId(active: boolean) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [ready, setReady] = useState(false);
  const [authorized, setAuthorized] = useState(false);
  const [payload, setPayload] = useState<VkIdPayload | null>(null);
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    if (!active) {
      if (containerRef.current) containerRef.current.innerHTML = "";
      // Это cleanup-сброс VK-state при деактивации хука (active=false),
      // а не каскадирующий render. setState в effect здесь безопасен
      // и осознанный.
      /* eslint-disable react-hooks/set-state-in-effect */
      setReady(false);
      setAuthorized(false);
      setPayload(null);
      setLoadError("");
      /* eslint-enable react-hooks/set-state-in-effect */
      return;
    }

    function tryInit() {
      // VK App ID. NEXT_PUBLIC_* переменные inlin'ятся при build,
      // и если CI не пробросил build-arg правильно — переменная пустая.
      // На случай этого fallback'имся на хардкод (это реальный production App ID).
      const appId =
        process.env.NEXT_PUBLIC_VK_APP_ID || "54546774";
      const container = containerRef.current;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const VKID = (window as any).VKIDSDK as any;
      const redirectUrl =
        process.env.NEXT_PUBLIC_VK_ID_REDIRECT_URL ||
        "https://doctor-barkova.ru/auth/vk/callback";

      if (!container || !VKID) return;
      if (!appId) {
        setLoadError("VK ID не настроен на фронтенде.");
        return;
      }
      if (container.childNodes.length > 0) return;

      try {
        VKID.Config.init({
          app: Number(appId),
          redirectUrl,
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
              // VK ID 2.x использует PKCE. code_verifier живёт внутри
              // VKID SDK, наружу не отдаётся — поэтому обменивать code
              // на access_token может ТОЛЬКО сам SDK (через exchangeCode).
              // Backend получает уже выданный access_token и проверяет
              // его через api.vk.com/method/users.get.
              VKID.Auth.exchangeCode(code, deviceId)
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                .then((data: any) => {
                  const userId =
                    data?.user_id ?? data?.user?.id ?? p?.user_id;
                  const accessToken = data?.access_token;
                  if (!userId || !accessToken) {
                    setAuthorized(false);
                    setPayload(null);
                    setLoadError(
                      "VK ID не вернул токен авторизации. Попробуйте ещё раз."
                    );
                    return;
                  }
                  setAuthorized(true);
                  setPayload({
                    user_id: userId,
                    access_token: accessToken,
                  });
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
    }

    tryInit();

    const timer = setInterval(() => {
      if ((window as any).VKIDSDK) tryInit(); // eslint-disable-line @typescript-eslint/no-explicit-any
    }, 500);

    return () => clearInterval(timer);
  }, [active]);

  return { containerRef, ready, authorized, payload, loadError };
}
