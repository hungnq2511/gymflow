import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { unwrap } from '@/lib/http';

export async function GET(request: Request) {
  try { await requireActor(['manager','staff']); const u = new URL(request.url); let q = createAdminClient().from('check_ins').select('*,members(full_name,member_code),subscriptions(plan_name_snapshot)').order('checked_in_at', { ascending: false }).limit(500); const member = u.searchParams.get('memberId'); if (member) q=q.eq('member_id',member); return Response.json(unwrap(await q)); } catch(e){ return apiError(e); }
}
export async function POST(request: Request) {
  try { const actor=await requireActor(['manager','staff']); const token=String((await request.json()).token??'').trim(); if(!token)return Response.json({error:'INVALID_TOKEN'},{status:400}); const result=unwrap(await createAdminClient().rpc('check_in_member',{p_token:token,p_actor_id:actor.id})); return Response.json(result,{status:result.ok?201:409}); } catch(e){return apiError(e);}
}
