create or replace function public.check_in_member(p_qr_token text,p_actor_id uuid)
returns jsonb language plpgsql security definer set search_path=public as $$
declare
  v_member public.members;
  v_subscription public.subscriptions;
  v_last timestamptz;
  v_checkin uuid;
begin
  select * into v_member from public.members
    where qr_token::text=p_qr_token or lower(member_code)=lower(p_qr_token)
    for update;
  if not found then return jsonb_build_object('ok',false,'reason','INVALID_QR'); end if;
  if v_member.status<>'active' then return jsonb_build_object('ok',false,'reason','MEMBER_INACTIVE'); end if;

  select * into v_subscription from public.subscriptions
    where member_id=v_member.id and status='active' and end_date>=current_date
      and (remaining_visits is null or remaining_visits>0)
    order by end_date limit 1 for update;
  if not found then return jsonb_build_object('ok',false,'reason','NO_VALID_SUBSCRIPTION'); end if;

  select checked_in_at into v_last from public.check_ins
    where member_id=v_member.id order by checked_in_at desc limit 1;
  if v_last is not null and v_last>now()-interval '10 minutes' then
    return jsonb_build_object('ok',false,'reason','DUPLICATE');
  end if;

  insert into public.check_ins(member_id,subscription_id,checked_in_by)
    values(v_member.id,v_subscription.id,p_actor_id) returning id into v_checkin;
  if v_subscription.remaining_visits is not null then
    update public.subscriptions set remaining_visits=remaining_visits-1 where id=v_subscription.id;
  end if;
  insert into public.audit_logs(actor_id,action,entity_type,entity_id,details)
    values(p_actor_id,'check_in','member',v_member.id,jsonb_build_object('check_in_id',v_checkin));
  return jsonb_build_object('ok',true,'check_in_id',v_checkin,'member_id',v_member.id,'member_name',v_member.full_name);
end;$$;

revoke all on function public.check_in_member(text,uuid) from public,anon,authenticated;
grant execute on function public.check_in_member(text,uuid) to service_role;

create or replace function public.sell_membership(
  p_member_id uuid,
  p_plan_id uuid,
  p_method public.payment_method,
  p_actor_id uuid
) returns jsonb language plpgsql security definer set search_path=public as $$
declare
  v_plan public.membership_plans;
  v_subscription_id uuid;
  v_payment_id uuid;
  v_start date := current_date;
  v_end date;
begin
  select * into v_plan from public.membership_plans where id=p_plan_id and is_active=true;
  if not found then return jsonb_build_object('ok',false,'reason','PLAN_NOT_FOUND'); end if;
  if not exists(select 1 from public.members where id=p_member_id and status='active') then
    return jsonb_build_object('ok',false,'reason','MEMBER_NOT_FOUND');
  end if;

  v_end := v_start + (v_plan.duration_days - 1);
  update public.subscriptions set status='cancelled', cancelled_at=now(), cancelled_by=p_actor_id
    where member_id=p_member_id and status='active';
  insert into public.subscriptions(member_id,plan_id,start_date,end_date,remaining_visits)
    values(p_member_id,p_plan_id,v_start,v_end,v_plan.visit_limit)
    returning id into v_subscription_id;
  insert into public.payments(subscription_id,member_id,amount,method,recorded_by)
    values(v_subscription_id,p_member_id,v_plan.price,p_method,p_actor_id)
    returning id into v_payment_id;
  insert into public.audit_logs(actor_id,action,entity_type,entity_id,details)
    values(p_actor_id,'sell_membership','subscription',v_subscription_id,
      jsonb_build_object('payment_id',v_payment_id,'plan_id',p_plan_id));
  return jsonb_build_object('ok',true,'subscription_id',v_subscription_id,'payment_id',v_payment_id);
end;$$;

revoke all on function public.sell_membership(uuid,uuid,public.payment_method,uuid) from public,anon,authenticated;
grant execute on function public.sell_membership(uuid,uuid,public.payment_method,uuid) to service_role;
