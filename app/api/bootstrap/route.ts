import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { todayVietnam, unwrap } from '@/lib/http';

export async function GET() {
  try {
    const actor = await requireActor(['manager', 'staff']);
    const db = createAdminClient();
    const today = todayVietnam();
    const monthStart = `${today.slice(0, 7)}-01T00:00:00+07:00`;
    const checkInStart = new Date(Date.now() - 30 * 86400000).toISOString();
    const [members, plans, payments, checkIns] = await Promise.all([
      db.from('members').select('id,member_code,full_name,phone,email,date_of_birth,gender,address,emergency_contact,notes,status,created_at,subscriptions(id,start_date,end_date,remaining_visits,status,sale_type,created_at,plan_name_snapshot,membership_plans(name))').order('created_at', { ascending: false }),
      db.from('membership_plans').select('id,name,price,duration_days,visit_limit,is_active,description,terms,subscriptions(count)').order('price'),
      db.from('payments').select('id,receipt_code,amount,method,status,paid_at,members(full_name),subscriptions(plan_name_snapshot,membership_plans(name))').gte('paid_at', monthStart).order('paid_at', { ascending: false }).limit(500),
      db.from('check_ins').select('id,checked_in_at,members(full_name,member_code)').gte('checked_in_at', checkInStart).order('checked_in_at', { ascending: false }).limit(1000),
    ]);
    return Response.json({ actor, members: unwrap(members), plans: unwrap(plans), payments: unwrap(payments), checkIns: unwrap(checkIns), updatedAt: new Date().toISOString() });
  } catch (error) { return apiError(error); }
}
