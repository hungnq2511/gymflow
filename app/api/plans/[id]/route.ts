import { z } from 'zod';
import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { unwrap } from '@/lib/http';
import { safeTextSchema } from '@/lib/validation';
const schema = z.object({
  name: safeTextSchema(2, 150).optional(),
  price: z.number().min(0).optional(),
  durationDays: z.number().int().positive().optional(),
  visitLimit: z.number().int().positive().nullable().optional(),
  description: z.string().nullable().optional(),
  terms: z.string().nullable().optional(),
  isActive: z.boolean().optional(),
});
export async function PATCH(
  request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    const actor = await requireActor(['manager']);
    const { id } = await params;
    const p = schema.safeParse(await request.json());
    if (!p.success)
      return Response.json({ error: 'INVALID_INPUT' }, { status: 400 });
    const i = p.data;
    const changes = {
      ...(i.name !== undefined && { name: i.name }),
      ...(i.price !== undefined && { price: i.price }),
      ...(i.durationDays !== undefined && { duration_days: i.durationDays }),
      ...(i.visitLimit !== undefined && { visit_limit: i.visitLimit }),
      ...(i.description !== undefined && { description: i.description }),
      ...(i.terms !== undefined && { terms: i.terms }),
      ...(i.isActive !== undefined && { is_active: i.isActive }),
      updated_at: new Date().toISOString(),
    };
    const db = createAdminClient();
    const plan = unwrap(
      await db
        .from('membership_plans')
        .update(changes)
        .eq('id', id)
        .select()
        .single(),
    );
    unwrap(
      await db
        .from('audit_logs')
        .insert({
          actor_id: actor.id,
          action: 'update',
          entity_type: 'membership_plan',
          entity_id: id,
          details: changes,
        })
        .select()
        .single(),
    );
    return Response.json(plan);
  } catch (e) {
    return apiError(e);
  }
}
