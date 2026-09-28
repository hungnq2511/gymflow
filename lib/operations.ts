export type RetentionSubscription = {
  end_date: string;
  remaining_visits: number | null;
};

export function isRetentionCandidate(
  subscription: RetentionSubscription,
  until: string,
) {
  return (
    subscription.end_date <= until ||
    (subscription.remaining_visits !== null &&
      subscription.remaining_visits <= 3)
  );
}

export function calculateFinancialSummary(
  payments: Array<{ amount: number | string; status: string }>,
  expenses: Array<{ amount: number | string; status: string }>,
) {
  const revenue = payments
    .filter((item) => item.status === 'valid')
    .reduce((sum, item) => sum + Number(item.amount), 0);
  const expenseTotal = expenses
    .filter((item) => item.status === 'valid')
    .reduce((sum, item) => sum + Number(item.amount), 0);
  return { revenue, expenses: expenseTotal, profit: revenue - expenseTotal };
}
