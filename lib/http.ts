import type { PostgrestError } from '@supabase/supabase-js';

export function unwrap<T>(result: {
  data: T;
  error: PostgrestError | null;
}): NonNullable<T> {
  if (result.error) throw new Error(result.error.message);
  if (result.data == null) throw new Error('DATA_NOT_FOUND');
  return result.data;
}

export function todayVietnam() {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Ho_Chi_Minh',
  }).format(new Date());
}

export function vietnamDateTimeLocal(date = new Date()) {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Ho_Chi_Minh',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  }).formatToParts(date);
  const value = Object.fromEntries(
    parts.map((part) => [part.type, part.value]),
  );
  return `${value.year}-${value.month}-${value.day}T${value.hour}:${value.minute}`;
}

export function vietnamLocalDateTimeToIso(value: string) {
  return new Date(`${value}:00+07:00`).toISOString();
}
