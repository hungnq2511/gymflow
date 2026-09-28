import { z } from 'zod';
import { createAdminClient } from '@/lib/supabase/admin';
import { createClient } from '@/lib/supabase/server';
import { passwordSchema } from '@/lib/validation';

const schema = z.object({ password: passwordSchema });

export async function POST(request: Request) {
  const parsed = schema.safeParse(await request.json());
  if (!parsed.success)
    return Response.json({ error: 'WEAK_PASSWORD' }, { status: 400 });
  if (parsed.data.password === 'admin123')
    return Response.json(
      { error: 'DEFAULT_PASSWORD_NOT_ALLOWED' },
      { status: 400 },
    );
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user)
    return Response.json(
      { error: 'RECOVERY_SESSION_MISSING' },
      { status: 401 },
    );
  const { error } = await supabase.auth.updateUser({
    password: parsed.data.password,
  });
  if (error) {
    const code =
      error.code === 'same_password'
        ? 'SAME_PASSWORD'
        : error.code === 'weak_password'
          ? 'WEAK_PASSWORD'
          : 'RECOVERY_LINK_INVALID';
    return Response.json({ error: code }, { status: 400 });
  }
  const { error: profileError } = await createAdminClient()
    .from('profiles')
    .update({
      must_change_password: false,
      updated_at: new Date().toISOString(),
    })
    .eq('auth_user_id', user.id);
  if (profileError)
    return Response.json(
      { error: 'PASSWORD_FLAG_UPDATE_FAILED' },
      { status: 500 },
    );
  return Response.json({ ok: true });
}
