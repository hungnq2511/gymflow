import { z } from 'zod';
import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { unwrap } from '@/lib/http';

export async function GET() {
  try {
    await requireActor(['manager']);
    return Response.json(
      unwrap(
        await createAdminClient()
          .from('profiles')
          .select('id,username,full_name,phone,role,status,created_at')
          .in('role', ['manager', 'staff'])
          .order('created_at'),
      ),
    );
  } catch (error) {
    return apiError(error);
  }
}

export async function POST(request: Request) {
  try {
    const actor = await requireActor(['manager']);
    const parsed = z
      .object({
        username: z
          .string()
          .trim()
          .toLowerCase()
          .regex(/^[a-z0-9._-]{3,32}$/),
        fullName: z.string().trim().min(2),
      })
      .safeParse(await request.json());
    if (!parsed.success)
      return Response.json({ error: 'INVALID_INPUT' }, { status: 400 });

    const db = createAdminClient();
    const loginEmail = `${parsed.data.username}@staff.gymflow.local`;
    const { data: existing } = await db
      .from('profiles')
      .select('id')
      .ilike('username', parsed.data.username)
      .maybeSingle();
    if (existing)
      return Response.json({ error: 'DUPLICATE_USERNAME' }, { status: 409 });
    const profile = unwrap(
      await db
        .from('profiles')
        .insert({
          username: parsed.data.username,
          full_name: parsed.data.fullName,
          role: 'staff',
          status: 'active',
          must_change_password: true,
        })
        .select()
        .single(),
    );
    const { data: authData, error: authError } = await db.auth.admin.createUser(
      {
        email: loginEmail,
        password: 'admin123',
        email_confirm: true,
        user_metadata: {
          profile_id: profile.id,
          full_name: parsed.data.fullName,
          username: parsed.data.username,
        },
      },
    );
    if (authError || !authData.user) {
      await db.from('profiles').delete().eq('id', profile.id);
      if (authError?.message.toLowerCase().includes('already'))
        return Response.json({ error: 'DUPLICATE_USERNAME' }, { status: 409 });
      throw authError ?? new Error('AUTH_USER_CREATE_FAILED');
    }
    unwrap(
      await db
        .from('audit_logs')
        .insert({
          actor_id: actor.id,
          action: 'create_staff',
          entity_type: 'profile',
          entity_id: profile.id,
          details: { role: 'staff', username: parsed.data.username },
        })
        .select()
        .single(),
    );
    return Response.json(profile, { status: 201 });
  } catch (error) {
    return apiError(error);
  }
}
