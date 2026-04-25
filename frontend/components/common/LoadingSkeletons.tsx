"use client";

export function CardSkeleton() {
  return (
    <div className="animate-pulse space-y-4 rounded-xl border border-neutral-200 bg-white p-6">
      <div className="h-6 w-2/3 rounded-lg bg-neutral-200" />
      <div className="space-y-2">
        <div className="h-4 w-full rounded-lg bg-neutral-200" />
        <div className="h-4 w-5/6 rounded-lg bg-neutral-200" />
      </div>
      <div className="h-10 w-1/2 rounded-lg bg-neutral-200" />
    </div>
  );
}

export function FormSkeleton() {
  return (
    <div className="animate-pulse space-y-6 rounded-xl border border-neutral-200 bg-white p-6">
      {/* Header */}
      <div className="space-y-3">
        <div className="h-8 w-2/3 rounded-lg bg-neutral-200" />
        <div className="h-4 w-full rounded-lg bg-neutral-200" />
      </div>

      {/* Form fields */}
      {[1, 2, 3].map((i) => (
        <div key={i} className="space-y-2">
          <div className="h-4 w-1/3 rounded-lg bg-neutral-200" />
          <div className="h-10 w-full rounded-lg bg-neutral-200" />
        </div>
      ))}

      {/* Submit button */}
      <div className="h-12 w-full rounded-lg bg-neutral-200" />
    </div>
  );
}

export function PageSkeleton() {
  return (
    <div className="space-y-8 animate-pulse">
      {/* Hero */}
      <div className="h-64 w-full rounded-xl bg-neutral-200 sm:h-96" />

      {/* Content */}
      <div className="space-y-4 px-4">
        <div className="h-8 w-3/4 rounded-lg bg-neutral-200" />
        <div className="space-y-2">
          <div className="h-4 w-full rounded-lg bg-neutral-200" />
          <div className="h-4 w-5/6 rounded-lg bg-neutral-200" />
          <div className="h-4 w-4/5 rounded-lg bg-neutral-200" />
        </div>
      </div>

      {/* Cards */}
      <div className="grid gap-4 px-4 sm:grid-cols-2 md:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="space-y-2 rounded-xl bg-neutral-200 p-4 h-40" />
        ))}
      </div>
    </div>
  );
}

export function CalendarSkeleton() {
  return (
    <div className="animate-pulse space-y-4 rounded-xl border border-neutral-200 bg-white p-6">
      {/* Header */}
      <div className="h-6 w-2/3 rounded-lg bg-neutral-200" />

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-2">
        {Array.from({ length: 35 }).map((_, i) => (
          <div key={i} className="h-12 rounded-lg bg-neutral-200" />
        ))}
      </div>

      {/* Slots */}
      <div className="space-y-2">
        <div className="h-4 w-1/3 rounded-lg bg-neutral-200" />
        <div className="grid grid-cols-3 gap-2">
          {Array.from({ length: 9 }).map((_, i) => (
            <div key={i} className="h-10 rounded-lg bg-neutral-200" />
          ))}
        </div>
      </div>
    </div>
  );
}
