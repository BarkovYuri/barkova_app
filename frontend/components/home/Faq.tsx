import { HelpCircle } from "lucide-react";

import { loadFaqItems, loadSiteBlocks, textOr } from "../../lib/siteContent";
import { FaqAccordion } from "./FaqAccordion";

const FALLBACK_FAQ = [
  {
    id: -1,
    question: "Сколько длится онлайн-консультация?",
    answer:
      "Базовый приём — 30 минут. Этого достаточно, чтобы разобрать жалобы, обсудить уже имеющиеся анализы и составить план.",
    order: 0,
  },
  {
    id: -2,
    question: "Как проходит видеоконсультация?",
    answer:
      "За 10–15 минут до приёма в Telegram или VK придёт ссылка на видеовстречу.",
    order: 1,
  },
];

export async function Faq() {
  const [items, blocks] = await Promise.all([loadFaqItems(), loadSiteBlocks()]);

  const faqList = items.length > 0 ? items : FALLBACK_FAQ;
  const chip = textOr(blocks, "faq.section_chip", "Частые вопросы");
  const title = textOr(blocks, "faq.section_title", "Что обычно спрашивают");
  const subtitle = textOr(
    blocks,
    "faq.section_subtitle",
    "Если ваш вопрос не нашёлся ниже — напишите в Telegram или VK, отвечу лично."
  );

  return (
    <section className="py-16 md:py-24">
      <div className="container">
        <div className="grid gap-10 md:gap-16 lg:grid-cols-[minmax(0,360px)_minmax(0,1fr)]">
          {/* Left: heading */}
          <div className="lg:sticky lg:top-24 lg:self-start">
            <p className="chip">
              <HelpCircle className="h-3.5 w-3.5" strokeWidth={2.5} />
              {chip}
            </p>
            <h2 className="mt-5 text-neutral-900">{title}</h2>
            <p className="mt-4 text-base text-neutral-600 leading-relaxed">
              {subtitle}
            </p>
          </div>

          {/* Right: accordion */}
          <FaqAccordion items={faqList} />
        </div>
      </div>
    </section>
  );
}
