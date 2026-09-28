import { z } from 'zod';
import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { unwrap } from '@/lib/http';

// PostgreSQL accepts UUID values without an RFC version nibble. The demo plan IDs
// use that form (for example, 00000000-0000-0000-0000-000000000402), while
// z.uuid() only accepts RFC 4122/9562 UUIDs.
const postgresUuid = z.string().regex(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i);
const schema = z.object({ memberId: postgresUuid, planId: postgresUuid, method: z.enum(['cash','bank_transfer']), startDate: z.iso.date().optional() });
export async function POST(request: Request) {
  try {
    const actor = await requireActor(['manager','staff']); const parsed = schema.safeParse(await request.json());
    if (!parsed.success) return Response.json({ error: 'INVALID_INPUT' }, { status: 400 });
    const i = parsed.data;
    const result = unwrap(await createAdminClient().rpc('sell_membership', { p_member_id: i.memberId, p_plan_id: i.planId, p_method: i.method, p_actor_id: actor.id, p_start_date: i.startDate || new Date().toISOString().slice(0,10) }));
    return Response.json(result, { status: result.ok ? 201 : 409 });
  } catch (e) { return apiError(e); }
}
