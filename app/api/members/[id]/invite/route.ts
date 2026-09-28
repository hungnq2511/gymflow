import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { unwrap } from '@/lib/http';

export async function POST(request:Request,{params}:{params:Promise<{id:string}>}) {
  try { const actor=await requireActor(['manager','staff']); const {id}=await params; const db=createAdminClient(); const member=unwrap(await db.from('members').select('id,profile_id,email,full_name').eq('id',id).single()); if(!member.email)return Response.json({error:'EMAIL_REQUIRED'},{status:400}); if(member.profile_id)return Response.json({error:'ALREADY_LINKED'},{status:409}); const profile=unwrap(await db.from('profiles').insert({email:member.email,full_name:member.full_name,role:'member',status:'active'}).select().single()); const origin=new URL(request.url).origin; const {error}=await db.auth.admin.inviteUserByEmail(member.email,{redirectTo:`${origin}/update-password`,data:{profile_id:profile.id,member_id:member.id,full_name:member.full_name}}); if(error){await db.from('profiles').delete().eq('id',profile.id); throw error;} unwrap(await db.from('audit_logs').insert({actor_id:actor.id,action:'invite_member',entity_type:'member',entity_id:id,details:{email:member.email}}).select().single()); return Response.json({ok:true}); } catch(e){return apiError(e);}
}
