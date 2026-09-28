import { z } from 'zod';

// Fixture IDs are valid PostgreSQL UUID values even when they do not encode
// an RFC version/variant. Check the database UUID shape without rejecting them.
export const databaseIdSchema = z
  .string()
  .regex(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i);

// Contact numbers in this application are Vietnamese domestic numbers:
// a leading zero followed by exactly nine digits. Keep this rule on the API
// as browser validation can always be bypassed.
export const vietnamPhoneSchema = z
  .string()
  .trim()
  .regex(/^0\d{9}$/, 'Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0');

export const hasHtmlMarkup = (value: string) => /[<>]/.test(value);

export const safeTextSchema = (minimum: number, maximum: number) =>
  z
    .string()
    .trim()
    .min(minimum)
    .max(maximum)
    .refine((value) => !hasHtmlMarkup(value), 'Không được chứa thẻ HTML');

export const optionalSafeTextSchema = (maximum: number) =>
  z
    .string()
    .trim()
    .max(maximum)
    .refine((value) => !hasHtmlMarkup(value), 'Không được chứa thẻ HTML')
    .nullable()
    .optional();

export const passwordSchema = z
  .string()
  .min(8)
  .max(72)
  .refine(
    (value) => !hasHtmlMarkup(value),
    'Mật khẩu không được chứa thẻ HTML',
  );
