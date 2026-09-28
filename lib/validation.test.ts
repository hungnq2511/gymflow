import { describe, expect, it } from 'vitest';
import {
  databaseIdSchema,
  optionalSafeTextSchema,
  passwordSchema,
  safeTextSchema,
  vietnamPhoneSchema,
} from './validation';

describe('databaseIdSchema', () => {
  it('accepts generated UUIDs', () => {
    expect(databaseIdSchema.safeParse(crypto.randomUUID()).success).toBe(true);
  });

  it('accepts deterministic database fixture UUIDs', () => {
    expect(
      databaseIdSchema.safeParse('00000000-0000-0000-0000-000000009999')
        .success,
    ).toBe(true);
  });

  it('rejects non-UUID identifiers', () => {
    expect(databaseIdSchema.safeParse('not-a-uuid').success).toBe(false);
  });
});

describe('input validation', () => {
  it('only accepts a 10-digit Vietnamese phone number', () => {
    expect(vietnamPhoneSchema.safeParse('0912345678').success).toBe(true);
    expect(vietnamPhoneSchema.safeParse('091234567').success).toBe(false);
    expect(vietnamPhoneSchema.safeParse('09123abc78').success).toBe(false);
    expect(vietnamPhoneSchema.safeParse('<script>1</script>').success).toBe(
      false,
    );
  });

  it('rejects HTML-like input in user-visible text', () => {
    expect(safeTextSchema(2, 100).safeParse('Nguyễn Văn An').success).toBe(
      true,
    );
    expect(
      safeTextSchema(2, 100).safeParse('<script>alert(1)</script>').success,
    ).toBe(false);
    expect(optionalSafeTextSchema(500).safeParse('<img src=x>').success).toBe(
      false,
    );
  });

  it('rejects HTML-like input in a new password', () => {
    expect(passwordSchema.safeParse('MatKhau-123').success).toBe(true);
    expect(passwordSchema.safeParse('<script>alert(1)</script>').success).toBe(
      false,
    );
  });
});
