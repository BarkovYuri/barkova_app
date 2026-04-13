const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

function normalizeEndpoint(endpoint: string) {
  if (!endpoint.startsWith("/")) {
    endpoint = `/${endpoint}`;
  }

  const [path, query] = endpoint.split("?");

  const normalizedPath = path.endsWith("/") ? path : `${path}/`;

  return query ? `${normalizedPath}?${query}` : normalizedPath;
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

  if (!res.ok) {
    throw new Error(`Ошибка API: ${res.status}`);
  }

  return res.json();
}

export async function postFormData(endpoint: string, formData: FormData) {
  const normalizedEndpoint = normalizeEndpoint(endpoint);

  const res = await fetch(`${API_URL}${normalizedEndpoint}`, {
    method: "POST",
    body: formData,
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    throw new Error(data ? JSON.stringify(data) : `Ошибка API: ${res.status}`);
  }

  return data;
}