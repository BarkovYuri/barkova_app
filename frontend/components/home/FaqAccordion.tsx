"use client";

import { ChevronDown } from "lucide-react";
import { useState } from "react";

import type { FaqItem } from "../../lib/types";

export function FaqAccordion({ items }: { items: FaqItem[] }) {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <div className="space-y-3">
      {items.map((item, idx) => {
        const isOpen = openIndex === idx;
        return (
          <div
            key={item.id}
            className={`rounded-2xl border bg-neutral-0 transition-colors ${
              isOpen
                ? "border-primary-200 shadow-sm"
                : "border-neutral-200 hover:border-neutral-300"
            }`}
          >
            <button
              type="button"
              onClick={() => setOpenIndex(isOpen ? null : idx)}
              aria-expanded={isOpen}
              className="flex w-full items-center justify-between gap-4 px-5 py-4 md:px-6 md:py-5 text-left"
            >
              <span
                className={`text-base md:text-lg font-semibold transition-colors ${
                  isOpen ? "text-primary-800" : "text-neutral-900"
                }`}
              >
                {item.question}
              </span>
              <span
                className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full transition-all duration-300 ${
                  isOpen
                    ? "bg-primary-600 text-neutral-0 rotate-180"
                    : "bg-neutral-100 text-neutral-500"
                }`}
              >
                <ChevronDown className="h-4 w-4" strokeWidth={2.5} />
              </span>
            </button>

            <div
              className="grid transition-all duration-300 ease-out"
              style={{ gridTemplateRows: isOpen ? "1fr" : "0fr" }}
            >
              <div className="overflow-hidden">
                <div className="px-5 pb-5 md:px-6 md:pb-6 text-sm md:text-base text-neutral-600 leading-relaxed whitespace-pre-line">
                  {item.answer}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
