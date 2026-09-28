import { z } from 'zod';
import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { unwrap } from '@/lib/http';
import { databaseIdSchema } from '@/lib/validation';

const schema = z.object({
  assignedTo: databaseIdSchema.optional(),
  status: z
    .enum(['pending', 'contacted', 'scheduled', 'renewed', 'not_interested'])
    .optional(),
  note: z.string().trim().max(2000).optional().nullable(),
  nextContactAt: z.string().optional().nullable(),
});

export async function PATCH(
  request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    const actor = await requireActor(['manager', 'staff']);
    const { id } = await params;
    const parsed = schema.safeParse(await request.json());
    if (!parsed.success)
      return Response.json({ error: 'INVALID_INPUT' }, { status: 400 });
    const i = parsed.data;
    const db = createAdminClient();
    if (i.assignedTo) {
      const assignee = await db
        .from('profiles')
        .select('id')
        .eq('id', i.assignedTo)
        .eq('role', 'staff')
        .eq('status', 'active')
        .maybeSingle();
      if (!assignee.data)
        return Response.json({ error: 'INVALID_ASSIGNEE' }, { status: 400 });
    }
    const target = await db
      .from('member_follow_ups')
      .select('id,assigned_to,created_by')
      .eq('id', id)
      .maybeSingle();
    if (!target.data)
      return Response.json({ error: 'DATA_NOT_FOUND' }, { status: 404 });
    if (actor.role === 'staff') {
      if (target.data.assigned_to !== actor.id)
        return Response.json({ error: 'FORBIDDEN' }, { status: 403 });
      const managerCreator = await db
        .from('profiles')
        .select('id')
        .eq('id', target.data.created_by)
        .eq('role', 'manager')
        .maybeSingle();
      if (!managerCreator.data)
        return Response.json({ error: 'FORBIDDEN' }, { status: 403 });
      if (
        i.assignedTo !== undefined ||
        i.note !== undefined ||
        i.nextContactAt !== undefined
      )
        return Response.json({ error: 'FORBIDDEN' }, { status: 403 });
    }
    const changes = {
      ...(i.assignedTo !== undefined && { assigned_to: i.assignedTo }),
      ...(i.status !== undefined && { status: i.status }),
      ...(i.note !== undefined && { note: i.note || null }),
      ...(i.nextContactAt !== undefined && {
        next_contact_at: i.nextContactAt || null,
      }),
      updated_at: new Date().toISOString(),
    };
    const row = unwrap(
      await db
        .from('member_follow_ups')
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
          action: 'update_follow_up',
          entity_type: 'member_follow_up',
          entity_id: id,
          details: changes,
        })
        .select()
        .single(),
    );
    return Response.json(row);
  } catch (error) {
    return apiError(error);
  }
}
