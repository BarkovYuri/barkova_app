"use client";

import { Loader2, X } from "lucide-react";
import { useEffect, useState } from "react";

import { fetchAPI } from "../../lib/api";
import type { LegalDocument } from "../../lib/types";

type Props = {
  open: boolean;
  docType: "offer" | "privacy" | "consent" | null;
  onClose: () => void;
};

const TITLE_FALLBACK: Record<NonNullable<Props["docType"]>, string> = {
  offer: "Публичная оферта",
  privacy: "Политика конфиденциальности",
  consent: "Согласие на обработку персональных данных",
};

export function LegalModal({ open, docType, onClose }: Props) {
  const [loading, setLoading] = useState(false);
  const [doc, setDoc] = useState<LegalDocument | null>(null);
  const [error, setError] = useState("");

  // Загружаем документ при открытии
  useEffect(() => {
    if (!open || !docType) return;

    let cancelled = false;
    setLoading(true);
    setDoc(null);
    setError("");

    (async () => {
      try {
        const data = (await fetchAPI("/legal")) as LegalDocument[] | null;
        if (cancelled) return;
        const found = (data || []).find((d) => d.doc_type === docType);
        if (!found) {
          setError("Документ пока не добавлен.");
        } else {
          setDoc(found);
        }
      } catch {
        if (!cancelled) {
          setError("Не удалось загрузить документ.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [open, docType]);

  // Закрытие по Esc
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [open, onClose]);

  // Блокируем скролл body
  useEffect(() => {
    if (!open) return;
    const orig = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = orig;
    };
  }, [open]);

  if (!open || !docType) return null;

  const title = doc?.title || TITLE_FALLBACK[docType];

  return (
    <div
      className="fixed inset-0 z-[60] flex items-end sm:items-center justify-center p-0 sm:p-6 animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-label={title}
    >
      {/* Backdrop */}
      <button
        type="button"
        aria-label="Закрыть"
        onClick={onClose}
        className="absolute inset-0 bg-neutral-900/40 backdrop-blur-sm"
      />

      {/* Panel */}
      <div className="relative z-10 w-full sm:max-w-2xl max-h-[92dvh] sm:max-h-[80dvh] flex flex-col rounded-t-3xl sm:rounded-3xl bg-neutral-0 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 px-6 py-5 border-b border-neutral-200 sticky top-0 bg-neutral-0 z-10">
          <div className="min-w-0">
            <p className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
              Юридическая информация
            </p>
            <h3 className="mt-1 text-neutral-900 text-h3-mobile sm:text-h3-desktop leading-tight">
              {title}
            </h3>
            {doc?.version ? (
              <p className="mt-1 text-xs text-neutral-500">
                Версия {doc.version}
              </p>
            ) : null}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Закрыть"
            className="flex-shrink-0 flex h-10 w-10 items-center justify-center rounded-full bg-neutral-100 text-neutral-600 hover:bg-neutral-200 transition"
          >
            <X className="h-5 w-5" strokeWidth={2.25} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          {loading ? (
            <div className="flex items-center justify-center py-12 text-neutral-500">
              <Loader2 className="h-5 w-5 animate-spin mr-2" strokeWidth={2.5} />
              Загружаем документ...
            </div>
          ) : error ? (
            <div className="rounded-2xl border border-error-100 bg-error-50 px-4 py-3 text-sm text-error-700">
              {error}
            </div>
          ) : doc ? (
            <div className="whitespace-pre-line text-sm sm:text-base text-neutral-700 leading-relaxed">
              {doc.content}
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-neutral-200 bg-neutral-50">
          <button
            type="button"
            onClick={onClose}
            className="btn-primary w-full"
          >
            Понятно
          </button>
        </div>
      </div>
    </div>
  );
}
