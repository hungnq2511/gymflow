import { z } from 'zod';
import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { unwrap } from '@/lib/http';
import { safeTextSchema } from '@/lib/validation';

const schema = z.object({
  name: safeTextSchema(2, 150),
  price: z.coerce.number().min(0),
  durationDays: z.coerce.number().int().positive(),
  visitLimit: z.coerce.number().int().positive().nullable().optional(),
  description: z.string().max(1000).optional(),
  terms: z.string().max(2000).optional(),
});
export async function GET() {
  try {
    await requireActor(['manager', 'staff']);
    return Response.json(
      unwrap(
        await createAdminClient()
          .from('membership_plans')
          .select('*')
          .order('created_at', { ascending: false }),
      ),
    );
  } catch (e) {
    return apiError(e);
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
    const db = createAdminClient();
    const plan = unwrap(
      await db
        .from('membership_plans')
        .insert({
          name: i.name,
          price: i.price,
          duration_days: i.durationDays,
          visit_limit: i.visitLimit ?? null,
          description: i.description || null,
          terms: i.terms || null,
        })
        .select()
        .single(),
    );
    unwrap(
      await db
        .from('audit_logs')
        .insert({
          actor_id: actor.id,
          action: 'create',
          entity_type: 'membership_plan',
          entity_id: plan.id,
        })
        .select()
        .single(),
    );
    return Response.json(plan, { status: 201 });
  } catch (e) {
    return apiError(e);
  }
}
