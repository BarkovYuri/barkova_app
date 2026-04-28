/**
 * Лёгкая обёртка над Telegram WebApp SDK.
 *
 * SDK подключается через <Script src="https://telegram.org/js/telegram-web-app.js">
 * и регистрирует глобал `window.Telegram.WebApp`. Когда сайт открыт в обычном
 * браузере — глобала нет. Хук возвращает null в этом случае.
 *
 * Документация: https://core.telegram.org/bots/webapps
 */

import { useEffect, useState } from "react";

// Минимальный type для нашего использования. Полный type см. в документации.
export type TelegramWebApp = {
  initData: string;
  initDataUnsafe: {
    user?: {
      id: number;
      first_name?: string;
      last_name?: string;
      username?: string;
      language_code?: string;
    };
    auth_date?: number;
    hash?: string;
    start_param?: string;
  };
  themeParams: {
    bg_color?: string;
    text_color?: string;
    hint_color?: string;
    link_color?: string;
    button_color?: string;
    button_text_color?: string;
    secondary_bg_color?: string;
  };
  colorScheme: "light" | "dark";
  version: string;
  platform: string;
  isExpanded: boolean;
  viewportHeight: number;
  viewportStableHeight: number;

  ready: () => void;
  expand: () => void;
  close: () => void;

  MainButton: {
    text: string;
    isVisible: boolean;
    isActive: boolean;
    setText: (text: string) => void;
    show: () => void;
    hide: () => void;
    enable: () => void;
    disable: () => void;
    showProgress: (leaveActive?: boolean) => void;
    hideProgress: () => void;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
    setParams: (params: {
      text?: string;
      color?: string;
      text_color?: string;
      is_active?: boolean;
      is_visible?: boolean;
    }) => void;
  };

  BackButton: {
    isVisible: boolean;
    show: () => void;
    hide: () => void;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
  };

  HapticFeedback: {
    impactOccurred: (
      style: "light" | "medium" | "heavy" | "rigid" | "soft"
    ) => void;
    notificationOccurred: (type: "error" | "success" | "warning") => void;
    selectionChanged: () => void;
  };

  showAlert: (message: string, callback?: () => void) => void;
  showConfirm: (
    message: string,
    callback?: (confirmed: boolean) => void
  ) => void;
};

declare global {
  interface Window {
    Telegram?: {
      WebApp?: TelegramWebApp;
    };
  }
}

/**
 * Хук возвращает экземпляр Telegram.WebApp если сайт открыт внутри Telegram,
 * иначе null. Также возвращает `ready: boolean` — стало ли SDK доступно
 * (актуально, потому что скрипт загружается асинхронно).
 */
export function useTelegramWebApp(): {
  webApp: TelegramWebApp | null;
  ready: boolean;
  isInTelegram: boolean;
} {
  const [webApp, setWebApp] = useState<TelegramWebApp | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // SDK уже подключён?
    if (typeof window !== "undefined" && window.Telegram?.WebApp) {
      const tg = window.Telegram.WebApp;
      // initData есть только при открытии из Telegram
      if (tg.initData) {
        setWebApp(tg);
        try {
          tg.ready();
          tg.expand();
        } catch {
          // ignore
        }
      }
      setReady(true);
      return;
    }

    // Ждём загрузки скрипта (next/script добавляет асинхронно)
    const interval = setInterval(() => {
      if (typeof window !== "undefined" && window.Telegram?.WebApp) {
        const tg = window.Telegram.WebApp;
        if (tg.initData) {
          setWebApp(tg);
          try {
            tg.ready();
            tg.expand();
          } catch {
            // ignore
          }
        }
        setReady(true);
        clearInterval(interval);
      }
    }, 100);

    // Если за 3 секунды не появился — считаем что не в Telegram
    const timeout = setTimeout(() => {
      clearInterval(interval);
      setReady(true);
    }, 3000);

    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, []);

  return {
    webApp,
    ready,
    isInTelegram: webApp !== null,
  };
}

/**
 * Применяет theme params Telegram к CSS-переменным документа.
 * Цвета меняются в зависимости от темы пользователя в его клиенте.
 */
export function applyTelegramTheme(webApp: TelegramWebApp): void {
  if (typeof document === "undefined") return;
  const t = webApp.themeParams;
  const root = document.documentElement;

  if (t.bg_color) root.style.setProperty("--tg-bg", t.bg_color);
  if (t.text_color) root.style.setProperty("--tg-text", t.text_color);
  if (t.hint_color) root.style.setProperty("--tg-hint", t.hint_color);
  if (t.button_color) root.style.setProperty("--tg-button", t.button_color);
  if (t.button_text_color)
    root.style.setProperty("--tg-button-text", t.button_text_color);
}
