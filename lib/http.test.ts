import { describe, expect, it } from 'vitest';
import { vietnamDateTimeLocal, vietnamLocalDateTimeToIso } from './http';

describe('Vietnam date-time conversion', () => {
  it('formats an instant for datetime-local inputs', () => {
    expect(vietnamDateTimeLocal(new Date('2026-01-02T03:04:00.000Z'))).toBe(
      '2026-01-02T10:04',
    );
  });

  it('stores a Vietnam local time as an unambiguous instant', () => {
    expect(vietnamLocalDateTimeToIso('2026-01-02T10:04')).toBe(
      '2026-01-02T03:04:00.000Z',
    );
  });
});
