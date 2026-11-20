import { ApiError } from "./errors";

const isServer = typeof window === "undefined";

const API_URL = isServer
  ? process.env.INTERNAL_API_URL || "http://backend:8000/api"
  : process.env.NEXT_PUBLIC_API_URL || "/api";

const USE_MOCK =
  (isServer ? process.env.USE_MOCK : process.env.NEXT_PUBLIC_USE_MOCK) === "1";

export const IS_MOCK_MODE = USE_MOCK;

// Серверные (SSR) GET-запросы кэшируем в Data Cache Next.js на минуту:
// раньше каждый просмотр страницы делал по 5–10 запросов в Django.
// Страницы при этом остаются динамическими (revalidate = 0 в page.tsx),
// поэтому `next build` в CI не ходит в недоступный бэкенд.
const SERVER_REVALIDATE_SECONDS = 60;

async function tryMock(endpoint: string, method: string): Promise<unknown> {
  if (!USE_MOCK) return undefined;
  // Моки подгружаются только в mock-режиме и не попадают в продакшн-бандл.
  const { tryMockResponse } = await import("./mock");
  return tryMockResponse(endpoint, method);
}

function normalizeEndpoint(endpoint: string): string {
  if (!endpoint.startsWith("/")) endpoint = `/${endpoint}`;
  const [path, query] = endpoint.split("?");
  const normalizedPath = path.endsWith("/") ? path : `${path}/`;
  return query ? `${normalizedPath}?${query}` : normalizedPath;
}

async function parseJsonSafe(res: Response): Promise<unknown> {
  const text = await res.text();
  if (!text || !text.trim()) return null;
  try {
    return JSON.parse(text);
  } catch {
    throw new ApiError("Некорректный JSON в ответе API");
  }
}

function buildApiError(data: unknown, httpStatus: number): ApiError {
  if (data && typeof data === "object") {
    const obj = data as Record<string, unknown>;
    const fields: Record<string, string[]> = {};

    for (const [key, val] of Object.entries(obj)) {
      if (key === "detail") continue;
      if (Array.isArray(val)) fields[key] = val.map(String);
      else if (typeof val === "string") fields[key] = [val];
    }

    const detail =
      typeof obj["detail"] === "string"
        ? obj["detail"]
        : Object.keys(fields).length > 0
        ? Object.values(fields)[0][0]
        : `Ошибка API: ${httpStatus}`;

    return new ApiError(detail, fields, httpStatus);
  }
  return new ApiError(`Ошибка API: ${httpStatus}`, {}, httpStatus);
}

export async function fetchAPI(
  endpoint: string,
  options?: RequestInit
): Promise<unknown> {
  const normalizedEndpoint = normalizeEndpoint(endpoint);
  const method = (options?.method ?? "GET").toUpperCase();

  const mock = await tryMock(normalizedEndpoint, method);
  if (mock !== undefined) return mock;

  const caching: RequestInit =
    isServer && method === "GET"
      ? { next: { revalidate: SERVER_REVALIDATE_SECONDS } }
      : { cache: "no-store" };

  const res = await fetch(`${API_URL}${normalizedEndpoint}`, {
    ...caching,
    ...options,
  });

  if (res.status === 404) return null;

  const data = await parseJsonSafe(res);

  if (!res.ok) throw buildApiError(data, res.status);

  return data;
}

export async function postFormData(
  endpoint: string,
  formData: FormData
): Promise<unknown> {
  const normalizedEndpoint = normalizeEndpoint(endpoint);

  const mock = await tryMock(normalizedEndpoint, "POST");
  if (mock !== undefined) return mock;

  const res = await fetch(`${API_URL}${normalizedEndpoint}`, {
    method: "POST",
    body: formData,
  });

  const data = await parseJsonSafe(res);

  if (!res.ok) throw buildApiError(data, res.status);

  return data;
}
