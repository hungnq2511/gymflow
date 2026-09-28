import { createAdminClient } from '@/lib/supabase/admin';
import { createClient } from '@/lib/supabase/server';

export type Role = 'manager' | 'staff' | 'member';
export type Actor = {
  id: string;
  authUserId: string;
  role: Role;
  email: string | null;
  fullName: string;
  mustChangePassword: boolean;
};

export async function currentActor(): Promise<Actor | null> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return null;
  const { data, error } = await createAdminClient()
    .from('profiles')
    .select('id,auth_user_id,email,full_name,role,status,must_change_password')
    .eq('auth_user_id', user.id)
    .maybeSingle();
  if (error) throw error;
  if (!data || data.status !== 'active') return null;
  return {
    id: data.id,
    authUserId: data.auth_user_id,
    role: data.role,
    email: data.email,
    fullName: data.full_name,
    mustChangePassword: data.must_change_password,
  };
}

export async function requireActor(roles: Role[]): Promise<Actor> {
  const actor = await currentActor();
  if (!actor) throw new Error('UNAUTHENTICATED');
  if (actor.mustChangePassword) throw new Error('PASSWORD_CHANGE_REQUIRED');
  if (!roles.includes(actor.role)) throw new Error('FORBIDDEN');
  return actor;
}

export function apiError(error: unknown) {
  const raw = error instanceof Error ? error.message : 'UNKNOWN';
  const message = raw.includes('duplicate key') ? 'DUPLICATE_DATA' : raw;
  const status =
    message === 'UNAUTHENTICATED'
      ? 401
      : message === 'FORBIDDEN' || message === 'PASSWORD_CHANGE_REQUIRED'
        ? 403
        : message === 'SUPABASE_NOT_CONFIGURED'
          ? 503
          : message === 'DUPLICATE_DATA'
            ? 409
            : 500;
  return Response.json({ error: message }, { status });
}
