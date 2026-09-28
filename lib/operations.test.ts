import { describe, expect, it } from 'vitest';
import { calculateFinancialSummary, isRetentionCandidate } from './operations';

describe('isRetentionCandidate', () => {
  it('includes subscriptions expiring inside the warning window', () => {
    expect(
      isRetentionCandidate(
        { end_date: '2026-10-10', remaining_visits: null },
        '2026-10-15',
      ),
    ).toBe(true);
  });

  it('includes subscriptions with three or fewer visits', () => {
    expect(
      isRetentionCandidate(
        { end_date: '2027-01-01', remaining_visits: 3 },
        '2026-10-15',
      ),
    ).toBe(true);
  });

  it('excludes healthy subscriptions', () => {
    expect(
      isRetentionCandidate(
        { end_date: '2027-01-01', remaining_visits: 10 },
        '2026-10-15',
      ),
    ).toBe(false);
  });
});

describe('calculateFinancialSummary', () => {
  it('ignores cancelled payments and expenses', () => {
    expect(
      calculateFinancialSummary(
        [
          { amount: 1_000_000, status: 'valid' },
          { amount: 400_000, status: 'cancelled' },
        ],
        [
          { amount: 250_000, status: 'valid' },
          { amount: 50_000, status: 'cancelled' },
        ],
      ),
    ).toEqual({ revenue: 1_000_000, expenses: 250_000, profit: 750_000 });
  });
});
