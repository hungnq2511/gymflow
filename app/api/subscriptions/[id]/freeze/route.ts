import { z } from 'zod';
import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { unwrap } from '@/lib/http';
const schema=z.object({startDate:z.string(),endDate:z.string(),reason:z.string().trim().min(3)});
export async function POST(request:Request,{params}:{params:Promise<{id:string}>}){try{const actor=await requireActor(['manager']);const {id}=await params;const p=schema.safeParse(await request.json());if(!p.success)return Response.json({error:'INVALID_INPUT'},{status:400});const result=unwrap(await createAdminClient().rpc('freeze_membership',{p_subscription_id:id,p_start:p.data.startDate,p_end:p.data.endDate,p_reason:p.data.reason,p_actor_id:actor.id}));return Response.json(result,{status:result.ok?201:409});}catch(e){return apiError(e);}}
export async function DELETE(_:Request,{params}:{params:Promise<{id:string}>}){try{const actor=await requireActor(['manager']);const {id}=await params;const result=unwrap(await createAdminClient().rpc('unfreeze_membership',{p_subscription_id:id,p_actor_id:actor.id}));return Response.json(result,{status:result.ok?200:409});}catch(e){return apiError(e);}}
