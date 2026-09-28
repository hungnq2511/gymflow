import { z } from 'zod';
import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { unwrap } from '@/lib/http';
import { optionalSafeTextSchema, vietnamPhoneSchema } from '@/lib/validation';

export async function GET() {
  try {
    const actor = await requireActor(['member']);
    const db = createAdminClient();
    const member = unwrap(
      await db
        .from('members')
        .select(
          '*,subscriptions(*,membership_plans(name),subscription_freezes(*)),payments(*,subscriptions(plan_name_snapshot)),check_ins(*,subscriptions(plan_name_snapshot))',
        )
        .eq('profile_id', actor.id)
        .single(),
    );
    return Response.json({ actor, member });
  } catch (e) {
    return apiError(e);
  }
}
const schema = z.object({
  phone: vietnamPhoneSchema,
  address: optionalSafeTextSchema(500),
  emergencyContact: optionalSafeTextSchema(250),
});
export async function PATCH(request: Request) {
  try {
    const actor = await requireActor(['member']);
    const p = schema.safeParse(await request.json());
    if (!p.success)
      return Response.json(
        { error: 'INVALID_INPUT', issues: p.error.issues },
        { status: 400 },
      );
    const db = createAdminClient();
    const member = unwrap(
      await db
        .from('members')
        .update({
          phone: p.data.phone,
          address: p.data.address || null,
          emergency_contact: p.data.emergencyContact || null,
          updated_at: new Date().toISOString(),
        })
        .eq('profile_id', actor.id)
        .select()
        .single(),
    );
    unwrap(
      await db
        .from('audit_logs')
        .insert({
          actor_id: actor.id,
          action: 'portal_update',
          entity_type: 'member',
          entity_id: member.id,
        })
        .select()
        .single(),
    );
    return Response.json(member);
  } catch (e) {
    return apiError(e);
  }
}
