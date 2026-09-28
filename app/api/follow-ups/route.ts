import { z } from 'zod';
import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { todayVietnam, unwrap, vietnamLocalDateTimeToIso } from '@/lib/http';
import { isRetentionCandidate } from '@/lib/operations';
import { databaseIdSchema } from '@/lib/validation';

const schema = z.object({
  memberId: databaseIdSchema,
  assignedTo: databaseIdSchema,
  status: z
    .enum(['pending', 'contacted', 'scheduled', 'renewed', 'not_interested'])
    .default('pending'),
  note: z.string().trim().max(2000).optional().nullable(),
  nextContactAt: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/)
    .refine(
      (value) => !Number.isNaN(new Date(`${value}:00+07:00`).getTime()),
      'Thời gian không hợp lệ',
    )
    .optional()
    .nullable(),
});

export async function GET() {
  try {
    const actor = await requireActor(['manager', 'staff']);
    const db = createAdminClient();
    const today = todayVietnam();
    const horizon = new Date(`${today}T00:00:00+07:00`);
    horizon.setDate(horizon.getDate() + 30);
    const until = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Ho_Chi_Minh',
    }).format(horizon);
    let followUpsQuery = db
      .from('member_follow_ups')
      .select(
        '*,profiles!member_follow_ups_assigned_to_fkey(full_name),creator:profiles!member_follow_ups_created_by_fkey!inner(role),members(full_name,member_code,phone)',
      )
      .order('updated_at', { ascending: false })
      .limit(300);
    if (actor.role === 'staff')
      followUpsQuery = followUpsQuery
        .eq('assigned_to', actor.id)
        .eq('creator.role', 'manager');
    const [followUps, members, staff] = await Promise.all([
      followUpsQuery,
      actor.role === 'manager'
        ? db
            .from('members')
            .select(
              'id,member_code,full_name,phone,email,subscriptions(id,end_date,remaining_visits,status)',
            )
            .eq('status', 'active')
        : Promise.resolve({ data: [], error: null }),
      actor.role === 'manager'
        ? db
            .from('profiles')
            .select('id,full_name')
            .eq('role', 'staff')
            .eq('status', 'active')
            .order('full_name')
        : Promise.resolve({ data: [], error: null }),
    ]);
    const candidates = unwrap(members)
      .flatMap((member) => {
        const subscription = member.subscriptions
          ?.filter((item) =>
            ['active', 'scheduled', 'frozen'].includes(item.status),
          )
          .sort((a, b) => a.end_date.localeCompare(b.end_date))[0];
        if (!subscription || !isRetentionCandidate(subscription, until))
          return [];
        return [{ ...member, subscription }];
      })
      .sort((a, b) =>
        a.subscription.end_date.localeCompare(b.subscription.end_date),
      );
    return Response.json({
      candidates,
      followUps: unwrap(followUps),
      staff: unwrap(staff),
      actorRole: actor.role,
      today,
      until,
    });
  } catch (error) {
    return apiError(error);
  }
}

export async function POST(request: Request) {
  try {
    const actor = await requireActor(['manager']);
    const parsed = schema.safeParse(await request.json());
    if (!parsed.success)
      return Response.json(
        { error: 'INVALID_INPUT', issues: parsed.error.issues },
        { status: 400 },
      );
    const i = parsed.data;
    if (
      i.nextContactAt &&
      new Date(`${i.nextContactAt}:00+07:00`).getTime() < Date.now()
    )
      return Response.json({ error: 'PAST_CONTACT_TIME' }, { status: 400 });
    const db = createAdminClient();
    const assignedTo = i.assignedTo;
    const assignee = await db
      .from('profiles')
      .select('id')
      .eq('id', assignedTo)
      .eq('role', 'staff')
      .eq('status', 'active')
      .maybeSingle();
    if (!assignee.data)
      return Response.json({ error: 'INVALID_ASSIGNEE' }, { status: 400 });
    const row = unwrap(
      await db
        .from('member_follow_ups')
        .insert({
          member_id: i.memberId,
          assigned_to: assignedTo,
          status: i.status,
          note: i.note || null,
          next_contact_at: i.nextContactAt
            ? vietnamLocalDateTimeToIso(i.nextContactAt)
            : null,
          created_by: actor.id,
        })
        .select()
        .single(),
    );
    unwrap(
      await db
        .from('audit_logs')
        .insert({
          actor_id: actor.id,
          action: 'create_follow_up',
          entity_type: 'member_follow_up',
          entity_id: row.id,
          details: { assigned_to: assignedTo, member_id: i.memberId },
        })
        .select()
        .single(),
    );
    return Response.json(row, { status: 201 });
  } catch (error) {
    return apiError(error);
  }
}
