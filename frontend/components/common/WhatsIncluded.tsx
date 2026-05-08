import { resolveIcon } from "../../lib/iconMap";
import type { ConsultationFeature } from "../../lib/types";

type Props = {
  title?: string;
  subtitle?: string;
  features: ConsultationFeature[];
};

/**
 * Блок «Что входит» — список карточек с иконкой, заголовком и описанием.
 * Используется на /booking (онлайн) и /office (очный приём).
 *
 * Если features пуст — секция вообще не рендерится, чтобы не было
 * пустого блока на проде.
 */
export function WhatsIncluded({
  title = "Что входит в консультацию",
  subtitle,
  features,
}: Props) {
  if (features.length === 0) return null;

  return (
    <section className="mt-12 md:mt-16">
      <div className="max-w-3xl">
        <h2 className="text-h2-mobile sm:text-h2-desktop text-neutral-900">
          {title}
        </h2>
        {subtitle ? (
          <p className="mt-3 text-base sm:text-lg text-neutral-600 leading-relaxed">
            {subtitle}
          </p>
        ) : null}
      </div>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-2">
        {features.map((feature) => {
          const Icon = resolveIcon(feature.icon);
          return (
            <div
              key={feature.id}
              className="flex gap-4 rounded-2xl border border-neutral-200 bg-neutral-0 p-5 sm:p-6 transition-all hover:border-primary-200 hover:shadow-card-hover"
            >
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary-100 text-primary-700">
                <Icon className="h-5 w-5" strokeWidth={2.2} />
              </span>
              <div className="min-w-0">
                <p className="font-semibold text-neutral-900">{feature.title}</p>
                {feature.description ? (
                  <p className="mt-2 text-sm sm:text-base text-neutral-600 leading-relaxed">
                    {feature.description}
                  </p>
                ) : null}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
