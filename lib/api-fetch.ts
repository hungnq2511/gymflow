'use client';

type Listener = () => void;

let activeRequests = 0;
const listeners = new Set<Listener>();

function emit() {
  listeners.forEach((listener) => listener());
}

export function subscribeToApiActivity(listener: Listener) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

export function getActiveApiRequests() {
  return activeRequests;
}

export async function apiFetch(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> {
  activeRequests += 1;
  emit();
  try {
    return await fetch(input, init);
  } finally {
    activeRequests = Math.max(0, activeRequests - 1);
    emit();
  }
}
