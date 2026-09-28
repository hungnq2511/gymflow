'use client';

import { useSyncExternalStore } from 'react';
import { getActiveApiRequests, subscribeToApiActivity } from '@/lib/api-fetch';

export function ApiLoadingIndicator() {
  const activeRequests = useSyncExternalStore(
    subscribeToApiActivity,
    getActiveApiRequests,
    () => 0,
  );

  if (!activeRequests) return null;
  return (
    <div
      className="pointer-events-none fixed inset-x-0 top-0 z-[10000]"
      aria-live="polite"
    >
      <div className="h-1 overflow-hidden bg-primary/15">
        <div className="h-full w-1/3 animate-[api-loading_1s_ease-in-out_infinite] rounded-full bg-primary shadow-[0_0_16px_var(--primary)]" />
      </div>
      <span className="sr-only">Đang tải dữ liệu</span>
    </div>
  );
}
