"use client";

import { ChevronDown, HelpCircle } from "lucide-react";
import { useState } from "react";

type FaqItem = {
  question: string;
  answer: string;
};

const FAQ_ITEMS: FaqItem[] = [
  {
    question: "Сколько длится онлайн-консультация?",
    answer:
      "Базовый приём — 30 минут. Этого достаточно, чтобы разобрать жалобы, обсудить уже имеющиеся анализы и составить план. Если случай сложный — возможно продление.",
  },
  {
    question: "Как проходит видеоконсультация?",
    answer:
      "За 10–15 минут до приёма в Telegram или VK придёт ссылка на видеовстречу. Вам нужны ноутбук или телефон с камерой и стабильный интернет. Никаких отдельных приложений ставить не нужно.",
  },
  {
    question: "Что подготовить к приёму?",
    answer:
      "Свежие анализы (если есть), список текущих лекарств с дозировками, краткую хронологию симптомов: когда началось, что меняли, что помогало. Документы можно прикрепить к заявке заранее.",
  },
  {
    question: "Можно ли получить рецепт после онлайн-приёма?",
    answer:
      "После онлайн-консультации врач может оформить рекомендации и направления. Рецепт на рецептурные препараты по правилам РФ выдаётся на очном приёме либо через подключённую электронную систему, если она доступна в вашем регионе.",
  },
  {
    question: "Сохраняются ли мои данные в тайне?",
    answer:
      "Да. Все ваши данные обрабатываются в соответствии с 152-ФЗ. Сообщения в Telegram и VK не пересылаются третьим лицам. Записи приёмов не ведутся — обсуждение остаётся между вами и врачом.",
  },
  {
    question: "Что делать, если стало хуже после консультации?",
    answer:
      "Если состояние ухудшилось — напишите в тот же мессенджер, где подтверждали запись. Доктор постарается ответить максимально быстро. При неотложной ситуации звоните в скорую помощь (103 или 112).",
  },
];

export function Faq() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section className="py-16 md:py-24">
      <div className="container">
        <div className="grid gap-10 md:gap-16 lg:grid-cols-[minmax(0,360px)_minmax(0,1fr)]">
          {/* Left: heading */}
          <div className="lg:sticky lg:top-24 lg:self-start">
            <p className="chip">
              <HelpCircle className="h-3.5 w-3.5" strokeWidth={2.5} />
              Частые вопросы
            </p>
            <h2 className="mt-5 text-neutral-900">
              Что обычно спрашивают
            </h2>
            <p className="mt-4 text-base text-neutral-600 leading-relaxed">
              Если ваш вопрос не нашёлся ниже — напишите в Telegram или VK,
              отвечу лично.
            </p>
          </div>

          {/* Right: accordion */}
          <div className="space-y-3">
            {FAQ_ITEMS.map((item, idx) => {
              const isOpen = openIndex === idx;
              return (
                <div
                  key={item.question}
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

                  {/* Animated content */}
                  <div
                    className="grid transition-all duration-300 ease-out"
                    style={{
                      gridTemplateRows: isOpen ? "1fr" : "0fr",
                    }}
                  >
                    <div className="overflow-hidden">
                      <div className="px-5 pb-5 md:px-6 md:pb-6 text-sm md:text-base text-neutral-600 leading-relaxed">
                        {item.answer}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
