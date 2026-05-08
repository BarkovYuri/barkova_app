import { resolveIcon } from "../../lib/iconMap";
import type { ConsultationFeature } from "../../lib/types";

type Props = {
  title?: string;
  /**
   * Подзаголовок над карточками (опционально). Используется реже —
   * обычно достаточно intro.
   */
  subtitle?: string;
  /**
   * Свободный текст-нарратив. Показывается перед карточками
   * (если они есть). Поддерживает переносы строк / абзацы.
   */
  intro?: string;
  /**
   * Опциональные карточки-пункты. Если массив пуст — секция всё
   * равно отрендерится, если есть intro.
   */
  features?: ConsultationFeature[];
};

export function WhatsIncluded({
  title = "Что входит в консультацию",
  subtitle,
  intro,
  features = [],
}: Props) {
  const hasIntro = Boolean(intro?.trim());
  const hasFeatures = features.length > 0;

  if (!hasIntro && !hasFeatures) return null;

  return (
    <section className="mt-2 mb-12 md:mb-16">
      <div className="rounded-3xl border border-neutral-200 bg-neutral-0 p-6 sm:p-8 md:p-10 shadow-card">
        <div className="max-w-3xl">
          <span className="chip">Что входит</span>
          <h2 className="mt-4 text-h3-mobile sm:text-h3-desktop text-neutral-900">
            {title}
          </h2>
          {subtitle ? (
            <p className="mt-3 text-base text-neutral-600 leading-relaxed">
              {subtitle}
            </p>
          ) : null}
        </div>

        {hasIntro ? (
          <div className="mt-6 max-w-3xl text-base sm:text-lg text-neutral-700 leading-relaxed whitespace-pre-line">
            {intro}
          </div>
        ) : null}

        {hasFeatures ? (
          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            {features.map((feature) => {
              const Icon = resolveIcon(feature.icon);
              return (
                <div
                  key={feature.id}
                  className="flex gap-4 rounded-2xl border border-neutral-200 bg-neutral-50 p-5 transition-all hover:border-primary-200 hover:bg-neutral-0"
                >
                  <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary-100 text-primary-700">
                    <Icon className="h-5 w-5" strokeWidth={2.2} />
                  </span>
                  <div className="min-w-0">
                    <p className="font-semibold text-neutral-900">
                      {feature.title}
                    </p>
                    {feature.description ? (
                      <p className="mt-2 text-sm text-neutral-600 leading-relaxed">
                        {feature.description}
                      </p>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
        ) : null}
      </div>
    </section>
  );
}
