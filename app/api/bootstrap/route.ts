import { apiError, requireActor } from '@/lib/authz';
import { supabaseAdmin } from '@/lib/supabase/admin';
export async function GET() {
  try {
    const actor = await requireActor(['manager', 'staff', 'member']);
    const own = actor.role === 'member' ? `&profile_id=eq.${actor.id}` : '';
    const [members, plans, payments] = await Promise.all([
      supabaseAdmin(
        `members?select=id,member_code,full_name,phone,status,subscriptions(end_date,remaining_visits,status,membership_plans(name))${own}&order=created_at.desc`,
      ),
      supabaseAdmin(
        'membership_plans?select=*&is_active=eq.true&order=price.asc',
      ),
      supabaseAdmin(
        `payments?select=id,amount,method,status,paid_at,members(full_name),subscriptions(membership_plans(name))&status=eq.valid&order=paid_at.desc&limit=50`,
      ),
    ]);
    return Response.json({ actor, members, plans, payments });
  } catch (e) {
    return apiError(e);
  }
}
