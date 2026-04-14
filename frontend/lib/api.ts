const isServer = typeof window === "undefined";

const API_URL = isServer
  ? process.env.INTERNAL_API_URL || "http://backend:8000/api"
  : process.env.NEXT_PUBLIC_API_URL || "/api";

function normalizeEndpoint(endpoint: string) {
  if (!endpoint.startsWith("/")) {
    endpoint = `/${endpoint}`;
  }

  const [path, query] = endpoint.split("?");
  const normalizedPath = path.endsWith("/") ? path : `${path}/`;

  return query ? `${normalizedPath}?${query}` : normalizedPath;
}

async function parseJsonSafe(res: Response) {
  const text = await res.text();

  if (!text || !text.trim()) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    throw new Error("Некорректный JSON в ответе API");
  }
}

export async function fetchAPI(endpoint: string, options?: RequestInit) {
  const normalizedEndpoint = normalizeEndpoint(endpoint);

  const res = await fetch(`${API_URL}${normalizedEndpoint}`, {
    ...options,
    cache: "no-store",
  });

  if (res.status === 404) {
    return null;
  }

  const data = await parseJsonSafe(res);

  if (!res.ok) {
    throw new Error(
      data ? JSON.stringify(data) : `Ошибка API: ${res.status}`
    );
  }

  return data;
}

export async function postFormData(endpoint: string, formData: FormData) {
  const normalizedEndpoint = normalizeEndpoint(endpoint);

  const res = await fetch(`${API_URL}${normalizedEndpoint}`, {
    method: "POST",
    body: formData,
  });

  const data = await parseJsonSafe(res);

  if (!res.ok) {
    throw new Error(
      data ? JSON.stringify(data) : `Ошибка API: ${res.status}`
    );
  }

  return data;
}