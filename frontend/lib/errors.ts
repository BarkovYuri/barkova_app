/**
 * Централизованная обработка ошибок API.
 * Устраняет антипаттерн JSON.stringify/JSON.parse через Error.message.
 */

export class ApiError extends Error {
  public readonly fields: Record<string, string[]>;
  public readonly statusCode?: number;

  constructor(
    message: string,
    fields: Record<string, string[]> = {},
    statusCode?: number
  ) {
    super(message);
    this.name = "ApiError";
    this.fields = fields;
    this.statusCode = statusCode;
  }
}

/**
 * Превращает ответ API (любого вида) в человекочитаемую строку.
 */
export function extractErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    // Если есть field-ошибки — берём первую
    const firstField = Object.values(error.fields)[0];
    if (firstField?.length) return firstField[0];
    return error.message;
  }

  if (error instanceof Error) {
    // Обратная совместимость: старый код кидал JSON.stringify в message
    try {
      const parsed = JSON.parse(error.message);
      if (parsed && typeof parsed === "object") {
        const firstValue = Object.values(parsed)[0];
        if (Array.isArray(firstValue) && firstValue.length > 0) {
          return String(firstValue[0]);
        }
        if (typeof firstValue === "string") return firstValue;
        if (parsed.detail) return String(parsed.detail);
      }
    } catch {
      // не JSON — возвращаем как есть
    }
    return error.message;
  }

  return "Не удалось отправить запрос.";
}
