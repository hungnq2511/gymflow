import { z } from 'zod';
import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { unwrap } from '@/lib/http';
import {
  databaseIdSchema,
  optionalSafeTextSchema,
  safeTextSchema,
  vietnamPhoneSchema,
} from '@/lib/validation';

const schema = z.object({
  fullName: safeTextSchema(2, 150).optional(),
  phone: vietnamPhoneSchema.optional(),
  email: z.email().nullable().optional(),
  dateOfBirth: z.iso.date().nullable().optional(),
  gender: optionalSafeTextSchema(30),
  address: optionalSafeTextSchema(500),
  emergencyContact: optionalSafeTextSchema(250),
  avatarUrl: z.url().nullable().optional().or(z.literal('')),
  notes: optionalSafeTextSchema(2000),
  status: z.enum(['active', 'inactive']).optional(),
});
export async function PATCH(
  request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  try {
    const actor = await requireActor(['manager', 'staff']);
    const paramsResult = databaseIdSchema.safeParse((await params).id);
    if (!paramsResult.success)
      return Response.json({ error: 'INVALID_INPUT' }, { status: 400 });
    const id = paramsResult.data;
    const parsed = schema.safeParse(await request.json());
    if (!parsed.success)
      return Response.json(
        { error: 'INVALID_INPUT', issues: parsed.error.issues },
        { status: 400 },
      );
    const i = parsed.data;
    const db = createAdminClient();
    if (i.phone !== undefined || i.email !== undefined) {
      const filters = [
        i.phone !== undefined ? `phone.eq.${i.phone}` : '',
        i.email ? `email.eq.${i.email}` : '',
      ]
        .filter(Boolean)
        .join(',');
      if (filters) {
        const duplicates = unwrap(
          await db
            .from('members')
            .select('id')
            .neq('id', id)
            .or(filters)
            .limit(1),
        );
        if (duplicates.length)
          return Response.json({ error: 'DUPLICATE_MEMBER' }, { status: 409 });
      }
    }
    const changes = {
      ...(i.fullName !== undefined && { full_name: i.fullName }),
      ...(i.phone !== undefined && { phone: i.phone }),
      ...(i.email !== undefined && { email: i.email }),
      ...(i.dateOfBirth !== undefined && { date_of_birth: i.dateOfBirth }),
      ...(i.gender !== undefined && { gender: i.gender || null }),
      ...(i.address !== undefined && { address: i.address || null }),
      ...(i.emergencyContact !== undefined && {
        emergency_contact: i.emergencyContact || null,
      }),
      ...(i.avatarUrl !== undefined && { avatar_url: i.avatarUrl || null }),
      ...(i.notes !== undefined && { notes: i.notes || null }),
      ...(i.status !== undefined && { status: i.status }),
      updated_at: new Date().toISOString(),
    };
    const member = unwrap(
      await db.from('members').update(changes).eq('id', id).select().single(),
    );
    unwrap(
      await db
        .from('audit_logs')
        .insert({
          actor_id: actor.id,
          action: 'update',
          entity_type: 'member',
          entity_id: id,
          details: changes,
        })
        .select()
        .single(),
    );
    return Response.json(member);
  } catch (e) {
    return apiError(e);
  }
}
