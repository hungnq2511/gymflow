export type CheckInCandidate = {
  memberActive: boolean;
  subscriptionActive: boolean;
  subscriptionFrozen?: boolean;
  startDate?: string;
  endDate: string;
  remainingVisits: number | null;
  lastCheckInAt: Date | null;
};
export type CheckInDecision =
  | { ok: true; decrementVisit: boolean }
  | {
      ok: false;
      reason:
        | 'MEMBER_INACTIVE'
        | 'NO_ACTIVE_SUBSCRIPTION'
        | 'NOT_STARTED'
        | 'FROZEN'
        | 'EXPIRED'
        | 'NO_VISITS_LEFT'
        | 'DUPLICATE';
    };
export function decideCheckIn(
  c: CheckInCandidate,
  now = new Date(),
  duplicateMinutes = 10,
): CheckInDecision {
  if (!c.memberActive) return { ok: false, reason: 'MEMBER_INACTIVE' };
  if (!c.subscriptionActive)
    return { ok: false, reason: 'NO_ACTIVE_SUBSCRIPTION' };
  if (c.startDate && c.startDate > now.toISOString().slice(0, 10))
    return { ok: false, reason: 'NOT_STARTED' };
  if (c.subscriptionFrozen) return { ok: false, reason: 'FROZEN' };
  if (c.endDate < now.toISOString().slice(0, 10))
    return { ok: false, reason: 'EXPIRED' };
  if (c.remainingVisits !== null && c.remainingVisits <= 0)
    return { ok: false, reason: 'NO_VISITS_LEFT' };
  if (
    c.lastCheckInAt &&
    now.getTime() - c.lastCheckInAt.getTime() < duplicateMinutes * 60000
  )
    return { ok: false, reason: 'DUPLICATE' };
  return { ok: true, decrementVisit: c.remainingVisits !== null };
}
