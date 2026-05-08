"use client";

import { Check, CalendarDays, Clock, FileText, Send } from "lucide-react";

type Step = {
  label: string;
  complete: boolean;
  icon: typeof CalendarDays;
};

type Props = {
  hasSelectedDate: boolean;
  hasSelectedSlot: boolean;
  hasFilledForm: boolean;
  hasContactMethod: boolean;
};

/**
 * 4-точечный stepper: круг с иконкой/галочкой + соединяющая линия
 * между шагами. Заменяет прежний прогресс-бар. Visual'но даёт
 * пациенту чёткую картину «3 из 4 пройдено».
 *
 * Шаг считается «активным» если он первый невыполненный.
 */
export function BookingStepper({
  hasSelectedDate,
  hasSelectedSlot,
  hasFilledForm,
  hasContactMethod,
}: Props) {
  const steps: Step[] = [
    { label: "Дата", complete: hasSelectedDate, icon: CalendarDays },
    { label: "Время", complete: hasSelectedSlot, icon: Clock },
    { label: "Данные", complete: hasFilledForm, icon: FileText },
    { label: "Канал", complete: hasContactMethod, icon: Send },
  ];

  // Индекс первого невыполненного шага — это текущий «активный».
  const activeIndex = steps.findIndex((s) => !s.complete);
  const completedCount = steps.filter((s) => s.complete).length;
  const allDone = completedCount === steps.length;

  return (
    <div className="mb-8 animate-fade-in">
      <div className="flex items-baseline justify-between mb-4">
        <p className="text-sm font-semibold text-neutral-900">
          {allDone ? "Готово к отправке" : `Шаг ${completedCount + 1} из ${steps.length}`}
        </p>
        <p className="text-xs font-medium text-neutral-500">
          {completedCount}/{steps.length} пройдено
        </p>
      </div>

      <div className="flex items-start">
        {steps.map((step, idx) => {
          const Icon = step.icon;
          const isActive = idx === activeIndex;
          const isLast = idx === steps.length - 1;

          return (
            <div key={step.label} className="flex flex-1 items-start">
              {/* Step bubble */}
              <div className="flex flex-col items-center min-w-0">
                <div
                  className={`flex h-10 w-10 sm:h-11 sm:w-11 shrink-0 items-center justify-center rounded-full border-2 transition-all duration-500
                    ${
                      step.complete
                        ? "border-secondary-500 bg-secondary-500 text-neutral-0 shadow-md shadow-secondary-500/30"
                        : isActive
                          ? "border-primary-600 bg-neutral-0 text-primary-700 ring-4 ring-primary-100"
                          : "border-neutral-300 bg-neutral-0 text-neutral-400"
                    }`}
                  aria-current={isActive ? "step" : undefined}
                >
                  {step.complete ? (
                    <Check className="h-5 w-5" strokeWidth={3} />
                  ) : (
                    <Icon className="h-4 w-4 sm:h-5 sm:w-5" strokeWidth={2} />
                  )}
                </div>
                <p
                  className={`mt-2 text-[11px] sm:text-xs font-semibold text-center max-w-[70px] sm:max-w-none transition-colors
                    ${
                      step.complete
                        ? "text-secondary-700"
                        : isActive
                          ? "text-primary-700"
                          : "text-neutral-500"
                    }`}
                >
                  {step.label}
                </p>
              </div>

              {/* Connector */}
              {!isLast ? (
                <div className="flex-1 mt-5 sm:mt-[22px] mx-1 sm:mx-2">
                  <div
                    className={`h-0.5 w-full rounded-full transition-colors duration-700
                      ${step.complete ? "bg-secondary-500" : "bg-neutral-200"}`}
                  />
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}
