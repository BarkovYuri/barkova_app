import { resolveIcon } from "../../lib/iconMap";
import {
  loadHowItWorksSteps,
  loadSiteBlocks,
  textOr,
} from "../../lib/siteContent";

const FALLBACK_STEPS = [
  {
    id: -1,
    icon: "calendar_days",
    title: "Выбор даты",
    description:
      "Откройте календарь и выберите удобный день и время. Все свободные слоты подсвечены.",
    order: 0,
  },
  {
    id: -2,
    icon: "message_square",
    title: "Контактные данные",
    description:
      "Оставьте имя и телефон, опишите вопрос. Подключите Telegram или VK для уведомлений.",
    order: 1,
  },
  {
    id: -3,
    icon: "check_check",
    title: "Подтверждение",
    description:
      "В мессенджер придёт сообщение с подтверждением записи и всеми деталями приёма.",
    order: 2,
  },
  {
    id: -4,
    icon: "stethoscope",
    title: "Приём",
    description:
      "В назначенное время — выходите на связь. Получаете план обследований и рекомендации.",
    order: 3,
  },
];

export async function HowItWorks() {
  const [steps, blocks] = await Promise.all([
    loadHowItWorksSteps(),
    loadSiteBlocks(),
  ]);

  const items = steps.length > 0 ? steps : FALLBACK_STEPS;
  const chip = textOr(blocks, "how_it_works.section_chip", "Процесс");
  const title = textOr(blocks, "how_it_works.section_title", "Как это работает");
  const subtitle = textOr(
    blocks,
    "how_it_works.section_subtitle",
    "От первой записи до получения рекомендаций — всё прозрачно и предсказуемо"
  );

  return (
    <section className="py-16 md:py-24">
      <div className="container">
        <div className="text-center mb-12 md:mb-16">
          <p className="chip mx-auto">{chip}</p>
          <h2 className="mt-5 text-neutral-900">{title}</h2>
          <p className="mt-4 text-base sm:text-lg leading-relaxed text-neutral-600 max-w-2xl mx-auto">
            {subtitle}
          </p>
        </div>

        <div className="relative">
          {/* Соединительная линия (только на md+) */}
          <div
            aria-hidden="true"
            className="hidden md:block absolute top-7 left-0 right-0 h-px"
            style={{
              background:
                "linear-gradient(90deg, transparent 4%, var(--color-primary-200) 12%, var(--color-primary-200) 88%, transparent 96%)",
            }}
          />

          <div className="grid gap-8 md:gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-4">
            {items.map((step, idx) => {
              const Icon = resolveIcon(step.icon);
              return (
                <div
                  key={step.id}
                  className="relative flex flex-col items-center text-center"
                >
                  {/* Иконка-кружок поверх линии */}
                  <div className="relative">
                    <div className="flex h-14 w-14 items-center justify-center rounded-full bg-neutral-0 border-2 border-primary-200 text-primary-700 shadow-md">
                      <Icon className="h-6 w-6" strokeWidth={1.75} />
                    </div>
                    {/* Номер шага */}
                    <div className="absolute -top-2 -right-2 flex h-6 w-6 items-center justify-center rounded-full bg-primary-600 text-neutral-0 text-xs font-bold shadow-md">
                      {idx + 1}
                    </div>
                  </div>

                  <h3 className="mt-5 text-neutral-900 text-lg font-semibold">
                    {step.title}
                  </h3>
                  <p className="mt-2 text-sm text-neutral-600 leading-relaxed max-w-xs">
                    {step.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
