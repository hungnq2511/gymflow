import { apiError, requireActor } from '@/lib/authz';
import { supabaseRpc } from '@/lib/supabase/admin';
export async function POST(request: Request) {
  try {
    const actor = await requireActor(['manager', 'staff']);
    const { token } = (await request.json()) as { token?: string };
    if (!token?.trim())
      return Response.json({ error: 'INVALID_TOKEN' }, { status: 400 });
    const result = await supabaseRpc('check_in_member', {
      p_qr_token: token.trim(),
      p_actor_id: actor.id,
    });
    return Response.json(result);
  } catch (e) {
    return apiError(e);
  }
}
