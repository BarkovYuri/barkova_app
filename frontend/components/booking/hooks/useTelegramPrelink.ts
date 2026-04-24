"use client";

import { useState } from "react";
import { fetchAPI } from "../../../lib/api";

export function useTelegramPrelink() {
  const [token, setToken] = useState("");
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function connect() {
    const popup = window.open("", "_blank");
    try {
      setLoading(true);
      setError("");
      const data = await fetchAPI("/appointments/telegram/prelink", {
        method: "POST",
      }) as { token: string; bot_url: string };

      setToken(data.token);

      if (popup) {
        popup.location.href = data.bot_url;
      } else {
        window.location.href = data.bot_url;
      }
    } catch {
      if (popup) popup.close();
      setError("Не удалось создать ссылку для подключения Telegram.");
    } finally {
      setLoading(false);
    }
  }

  async function checkStatus() {
    if (!token) {
      setError("Сначала нажмите «Подключить Telegram».");
      return;
    }
    try {
      setError("");
      const data = await fetchAPI(
        `/appointments/telegram/prelink/status?token=${token}`
      ) as { linked: boolean };

      if (data?.linked) {
        setConnected(true);
      } else {
        setConnected(false);
        setError(
          "Telegram ещё не подтверждён. Нажмите Start в боте, затем проверьте снова."
        );
      }
    } catch {
      setError("Не удалось проверить подключение Telegram.");
    }
  }

  function reset() {
    setToken("");
    setConnected(false);
    setError("");
    setLoading(false);
  }

  return { token, connected, loading, error, connect, checkStatus, reset };
}
