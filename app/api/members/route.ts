import { z } from 'zod';
import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { unwrap } from '@/lib/http';
import {
  optionalSafeTextSchema,
  safeTextSchema,
  vietnamPhoneSchema,
} from '@/lib/validation';

const memberSchema = z.object({
  fullName: safeTextSchema(2, 150),
  phone: vietnamPhoneSchema,
  email: z.email().optional().or(z.literal('')),
  dateOfBirth: z.string().optional().nullable(),
  gender: optionalSafeTextSchema(30),
  address: optionalSafeTextSchema(500),
  emergencyContact: optionalSafeTextSchema(250),
  avatarUrl: z.url().optional().nullable().or(z.literal('')),
  notes: optionalSafeTextSchema(2000),
});

export async function GET(request: Request) {
  try {
    await requireActor(['manager', 'staff']);
    const url = new URL(request.url);
    const q = url.searchParams.get('q')?.trim();
    const status = url.searchParams.get('status');
    let query = createAdminClient()
      .from('members')
      .select(
        '*,profiles(email,status),subscriptions(*,membership_plans(name))',
      )
      .order('created_at', { ascending: false });
    if (q)
      query = query.or(
        `full_name.ilike.%${q}%,member_code.ilike.%${q}%,phone.ilike.%${q}%,email.ilike.%${q}%`,
      );
    if (status === 'active' || status === 'inactive')
      query = query.eq('status', status);
    return Response.json(unwrap(await query));
  } catch (error) {
    return apiError(error);
  }
}

export async function POST(request: Request) {
  try {
    const actor = await requireActor(['manager', 'staff']);
    const parsed = memberSchema.safeParse(await request.json());
    if (!parsed.success)
      return Response.json(
        { error: 'INVALID_INPUT', issues: parsed.error.issues },
        { status: 400 },
      );
    const i = parsed.data;
    const db = createAdminClient();
    const duplicates = unwrap(
      await db
        .from('members')
        .select('id,member_code,full_name,phone,email')
        .or(`phone.eq.${i.phone}${i.email ? `,email.eq.${i.email}` : ''}`),
    );
    if (duplicates.length)
      return Response.json(
        { error: 'DUPLICATE_MEMBER', existing: duplicates[0] },
        { status: 409 },
      );
    const code = `GF-${Date.now().toString().slice(-7)}`;
    const member = unwrap(
      await db
        .from('members')
        .insert({
          member_code: code,
          qr_token: crypto.randomUUID(),
          full_name: i.fullName,
          phone: i.phone,
          email: i.email || null,
          date_of_birth: i.dateOfBirth || null,
          gender: i.gender || null,
          address: i.address || null,
          emergency_contact: i.emergencyContact || null,
          avatar_url: i.avatarUrl || null,
          notes: i.notes || null,
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
          entity_type: 'member',
          entity_id: member.id,
          details: { member_code: code },
        })
        .select()
        .single(),
    );
    return Response.json(member, { status: 201 });
  } catch (error) {
    return apiError(error);
  }
}
