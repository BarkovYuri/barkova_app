import { ApiError } from "./errors";

const isServer = typeof window === "undefined";

const API_URL = isServer
  ? process.env.INTERNAL_API_URL || "http://backend:8000/api"
  : process.env.NEXT_PUBLIC_API_URL || "/api";

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

  const res = await fetch(`${API_URL}${normalizedEndpoint}`, {
    ...options,
    cache: "no-store",
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

  const res = await fetch(`${API_URL}${normalizedEndpoint}`, {
    method: "POST",
    body: formData,
  });

  const data = await parseJsonSafe(res);

  if (!res.ok) throw buildApiError(data, res.status);

  return data;
}
