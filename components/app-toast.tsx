'use client';

export function AppToast({ message }: { message: string }) {
  if (!message) return null;
  return (
    <output
      aria-live="polite"
      className="pointer-events-none fixed right-4 top-4 z-[9999] block max-w-[calc(100vw-2rem)] rounded-xl border border-white/10 bg-slate-950 px-4 py-3 text-sm font-medium text-white shadow-2xl sm:right-6 sm:top-6 sm:max-w-sm"
    >
      {message}
    </output>
  );
}
