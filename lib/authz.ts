import { getChatGPTUser } from '@/app/chatgpt-auth';
import { supabaseAdmin } from '@/lib/supabase/admin';

export type Actor = {
  id: string;
  role: 'manager' | 'staff' | 'member';
  email: string;
};
export async function requireActor(roles: Actor['role'][]): Promise<Actor> {
  const user = await getChatGPTUser();
  if (!user) throw new Error('UNAUTHENTICATED');
  const key = encodeURIComponent(user.userId),
    rows = await supabaseAdmin<Actor[]>(
      `profiles?external_auth_id=eq.${key}&select=id,role,email`,
    );
  let actor = rows[0];
  if (!actor) {
    const count = await supabaseAdmin<{ id: string }[]>(
      'profiles?select=id&limit=1',
    );
    if (count.length) throw new Error('FORBIDDEN');
    const created = await supabaseAdmin<Actor[]>('profiles', {
      method: 'POST',
      body: {
        external_auth_id: user.userId,
        email: user.email,
        full_name: user.displayName,
        role: 'manager',
        status: 'active',
      },
    });
    actor = created[0];
  }
  if (!roles.includes(actor.role)) throw new Error('FORBIDDEN');
  return actor;
}
export function apiError(error: unknown) {
  const message = error instanceof Error ? error.message : 'UNKNOWN';
  const status =
    message === 'UNAUTHENTICATED'
      ? 401
      : message === 'FORBIDDEN'
        ? 403
        : message === 'SUPABASE_NOT_CONFIGURED'
          ? 503
          : 500;
  return Response.json({ error: message }, { status });
}
