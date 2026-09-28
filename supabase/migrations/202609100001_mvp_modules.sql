-- GymFlow MVP: Supabase Auth, full subscription lifecycle, receipts and freezes.
drop function if exists public.check_in_member(text, uuid);
drop function if exists public.sell_membership(uuid, uuid, public.payment_method, uuid);

alter table public.profiles alter column external_auth_id drop not null;
alter table public.profiles alter column email drop not null;
alter table public.profiles add column if not exists auth_user_id uuid unique references auth.users(id) on delete set null;
alter table public.profiles add column if not exists updated_at timestamptz not null default now();

alter table public.members add column if not exists updated_at timestamptz not null default now();
alter table public.membership_plans add column if not exists description text;
alter table public.membership_plans add column if not exists terms text;
alter table public.membership_plans add column if not exists updated_at timestamptz not null default now();

alter table public.subscriptions alter column status drop default;
alter table public.subscriptions alter column status type text using status::text;
drop type if exists public.subscription_status;
alter table public.subscriptions alter column status set default 'active';
alter table public.subscriptions add constraint subscriptions_status_check check (status in ('scheduled','active','frozen','expired','cancelled'));
alter table public.subscriptions add column if not exists plan_name_snapshot text;
alter table public.subscriptions add column if not exists price_snapshot numeric(14,2);
alter table public.subscriptions add column if not exists duration_days_snapshot integer;
alter table public.subscriptions add column if not exists visit_limit_snapshot integer;
alter table public.subscriptions add column if not exists sale_type text not null default 'new' check (sale_type in ('new','renewal'));
alter table public.subscriptions add column if not exists updated_at timestamptz not null default now();

alter table public.payments add column if not exists receipt_code text unique;
alter table public.payments add column if not exists cancelled_reason text;
create unique index if not exists payments_one_valid_per_subscription on public.payments(subscription_id) where status='valid';

create table if not exists public.subscription_freezes(
  id uuid primary key default gen_random_uuid(),
  subscription_id uuid not null references public.subscriptions(id),
  start_date date not null,
  expected_end_date date not null check(expected_end_date >= start_date),
  actual_end_date date,
  reason text not null,
  status text not null default 'active' check(status in ('active','completed','cancelled')),
  created_by uuid not null references public.profiles(id),
  ended_by uuid references public.profiles(id),
  created_at timestamptz not null default now(),
  ended_at timestamptz
);
create unique index if not exists one_active_freeze_per_subscription on public.subscription_freezes(subscription_id) where status='active';
alter table public.subscription_freezes enable row level security;

create or replace function public.current_profile_id() returns uuid language sql stable security definer set search_path=public as $$select id from public.profiles where auth_user_id=auth.uid() and status='active' limit 1$$;
create or replace function public.current_user_role() returns public.user_role language sql stable security definer set search_path=public as $$select role from public.profiles where auth_user_id=auth.uid() and status='active' limit 1$$;
revoke all on function public.current_profile_id() from public,anon;
revoke all on function public.current_user_role() from public,anon;
grant execute on function public.current_profile_id() to authenticated;
grant execute on function public.current_user_role() to authenticated;

create policy "profile reads self" on public.profiles for select to authenticated using(auth_user_id=auth.uid());
create policy "staff read members" on public.members for select to authenticated using(public.current_user_role() in ('manager','staff'));
create policy "member reads self" on public.members for select to authenticated using(profile_id=public.current_profile_id());
create policy "staff read subscriptions" on public.subscriptions for select to authenticated using(public.current_user_role() in ('manager','staff'));
create policy "member reads own subscriptions" on public.subscriptions for select to authenticated using(member_id in(select id from public.members where profile_id=public.current_profile_id()));
create policy "staff read payments" on public.payments for select to authenticated using(public.current_user_role() in ('manager','staff'));
create policy "member reads own payments" on public.payments for select to authenticated using(member_id in(select id from public.members where profile_id=public.current_profile_id()));
create policy "staff read checkins" on public.check_ins for select to authenticated using(public.current_user_role() in ('manager','staff'));
create policy "member reads own checkins" on public.check_ins for select to authenticated using(member_id in(select id from public.members where profile_id=public.current_profile_id()));
create policy "staff read freezes" on public.subscription_freezes for select to authenticated using(public.current_user_role() in ('manager','staff'));
create policy "member reads own freezes" on public.subscription_freezes for select to authenticated using(subscription_id in(select id from public.subscriptions where member_id in(select id from public.members where profile_id=public.current_profile_id())));
create policy "manager reads audit" on public.audit_logs for select to authenticated using(public.current_user_role()='manager');

create or replace function public.handle_new_auth_user()
returns trigger language plpgsql security definer set search_path=public as $$
declare v_profile uuid; v_member uuid; v_role public.user_role;
begin
  v_profile := nullif(new.raw_user_meta_data->>'profile_id','')::uuid;
  v_member := nullif(new.raw_user_meta_data->>'member_id','')::uuid;
  if v_profile is null then
    select id into v_profile from public.profiles where auth_user_id is null and lower(email)=lower(new.email) limit 1;
  end if;
  if v_profile is not null and exists(select 1 from public.profiles where id=v_profile and auth_user_id is null) then
    update public.profiles set auth_user_id=new.id,email=coalesce(email,new.email),updated_at=now() where id=v_profile;
  else
    select case when count(*)=0 then 'manager'::public.user_role else 'member'::public.user_role end into v_role from public.profiles;
    insert into public.profiles(auth_user_id,external_auth_id,email,full_name,role)
    values(new.id,new.id::text,new.email,coalesce(new.raw_user_meta_data->>'full_name',split_part(new.email,'@',1)),v_role)
    returning id into v_profile;
  end if;
  if v_member is not null then update public.members set profile_id=v_profile where id=v_member and profile_id is null; end if;
  return new;
end;$$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users for each row execute function public.handle_new_auth_user();

create or replace function public.sell_membership(
  p_member_id uuid,p_plan_id uuid,p_method public.payment_method,p_actor_id uuid,p_start_date date default current_date
) returns jsonb language plpgsql security definer set search_path=public as $$
declare v_plan public.membership_plans; v_member public.members; v_start date; v_end date; v_last_end date;
  v_subscription_id uuid; v_payment_id uuid; v_receipt text; v_sale_type text := 'new';
begin
  select * into v_member from public.members where id=p_member_id for update;
  if not found or v_member.status<>'active' then return jsonb_build_object('ok',false,'reason','MEMBER_NOT_ACTIVE'); end if;
  select * into v_plan from public.membership_plans where id=p_plan_id and is_active=true;
  if not found then return jsonb_build_object('ok',false,'reason','PLAN_NOT_FOUND'); end if;
  select max(end_date) into v_last_end from public.subscriptions where member_id=p_member_id and status in ('active','frozen','scheduled');
  if v_last_end is not null and v_last_end>=coalesce(p_start_date,current_date) then
    v_start := v_last_end+1; v_sale_type := 'renewal';
  else v_start := coalesce(p_start_date,current_date); end if;
  if exists(select 1 from public.subscriptions where member_id=p_member_id and status in ('active','frozen','scheduled') and daterange(start_date,end_date,'[]') && daterange(v_start,v_start+v_plan.duration_days-1,'[]')) then
    return jsonb_build_object('ok',false,'reason','OVERLAPPING_SUBSCRIPTION');
  end if;
  v_end := v_start+v_plan.duration_days-1;
  insert into public.subscriptions(member_id,plan_id,start_date,end_date,remaining_visits,status,plan_name_snapshot,price_snapshot,duration_days_snapshot,visit_limit_snapshot,sale_type)
  values(p_member_id,p_plan_id,v_start,v_end,v_plan.visit_limit,case when v_start>current_date then 'scheduled' else 'active' end,v_plan.name,v_plan.price,v_plan.duration_days,v_plan.visit_limit,v_sale_type)
  returning id into v_subscription_id;
  v_payment_id := gen_random_uuid();
  v_receipt := 'PT-'||to_char(clock_timestamp(),'YYYYMMDDHH24MISS')||'-'||upper(substr(replace(v_payment_id::text,'-',''),1,4));
  insert into public.payments(id,receipt_code,subscription_id,member_id,amount,method,recorded_by)
  values(v_payment_id,v_receipt,v_subscription_id,p_member_id,v_plan.price,p_method,p_actor_id);
  insert into public.audit_logs(actor_id,action,entity_type,entity_id,details)
  values(p_actor_id,'sell_membership','subscription',v_subscription_id,jsonb_build_object('payment_id',v_payment_id,'sale_type',v_sale_type));
  return jsonb_build_object('ok',true,'subscription_id',v_subscription_id,'payment_id',v_payment_id,'receipt_code',v_receipt,'sale_type',v_sale_type,'start_date',v_start,'end_date',v_end);
end;$$;

create or replace function public.check_in_member(p_token text,p_actor_id uuid)
returns jsonb language plpgsql security definer set search_path=public as $$
declare v_member public.members; v_sub public.subscriptions; v_last timestamptz; v_id uuid; v_plan text;
begin
  select * into v_member from public.members where qr_token::text=p_token or lower(member_code)=lower(p_token) for update;
  if not found then return jsonb_build_object('ok',false,'reason','INVALID_QR'); end if;
  if v_member.status<>'active' then return jsonb_build_object('ok',false,'reason','MEMBER_INACTIVE'); end if;
  update public.subscriptions set status='expired',updated_at=now() where member_id=v_member.id and status='active' and end_date<current_date;
  update public.subscriptions set status='active',updated_at=now() where member_id=v_member.id and status='scheduled' and start_date<=current_date and end_date>=current_date;
  if exists(select 1 from public.subscriptions where member_id=v_member.id and status='frozen') then return jsonb_build_object('ok',false,'reason','SUBSCRIPTION_FROZEN'); end if;
  select s.* into v_sub from public.subscriptions s join public.membership_plans p on p.id=s.plan_id
  where s.member_id=v_member.id and s.status='active' and s.start_date<=current_date and s.end_date>=current_date order by s.end_date limit 1 for update of s;
  if not found then
    if exists(select 1 from public.subscriptions where member_id=v_member.id and status='scheduled') then return jsonb_build_object('ok',false,'reason','SUBSCRIPTION_NOT_STARTED'); end if;
    return jsonb_build_object('ok',false,'reason','NO_VALID_SUBSCRIPTION');
  end if;
  if v_sub.remaining_visits=0 then return jsonb_build_object('ok',false,'reason','NO_VISITS_LEFT'); end if;
  select checked_in_at into v_last from public.check_ins where member_id=v_member.id order by checked_in_at desc limit 1;
  if v_last>now()-interval '10 minutes' then return jsonb_build_object('ok',false,'reason','DUPLICATE'); end if;
  insert into public.check_ins(member_id,subscription_id,checked_in_by) values(v_member.id,v_sub.id,p_actor_id) returning id into v_id;
  if v_sub.remaining_visits is not null then update public.subscriptions set remaining_visits=remaining_visits-1,updated_at=now() where id=v_sub.id; end if;
  select coalesce(plan_name_snapshot,p.name) into v_plan from public.subscriptions s join public.membership_plans p on p.id=s.plan_id where s.id=v_sub.id;
  insert into public.audit_logs(actor_id,action,entity_type,entity_id,details) values(p_actor_id,'check_in','member',v_member.id,jsonb_build_object('check_in_id',v_id));
  return jsonb_build_object('ok',true,'check_in_id',v_id,'member_id',v_member.id,'member_name',v_member.full_name,'avatar_url',v_member.avatar_url,'plan_name',v_plan,'end_date',v_sub.end_date,'remaining_visits',case when v_sub.remaining_visits is null then null else v_sub.remaining_visits-1 end,'checked_in_at',now());
end;$$;

create or replace function public.freeze_membership(p_subscription_id uuid,p_start date,p_end date,p_reason text,p_actor_id uuid)
returns jsonb language plpgsql security definer set search_path=public as $$
declare v_sub public.subscriptions; v_id uuid;
begin
  select * into v_sub from public.subscriptions where id=p_subscription_id for update;
  if not found or v_sub.end_date<current_date then return jsonb_build_object('ok',false,'reason','SUBSCRIPTION_EXPIRED'); end if;
  if p_end<p_start or p_start<current_date or trim(coalesce(p_reason,''))='' then return jsonb_build_object('ok',false,'reason','INVALID_FREEZE'); end if;
  if exists(select 1 from public.subscription_freezes where subscription_id=p_subscription_id and status='active') then return jsonb_build_object('ok',false,'reason','ALREADY_FROZEN'); end if;
  insert into public.subscription_freezes(subscription_id,start_date,expected_end_date,reason,created_by) values(p_subscription_id,p_start,p_end,trim(p_reason),p_actor_id) returning id into v_id;
  update public.subscriptions set status='frozen',updated_at=now() where id=p_subscription_id;
  insert into public.audit_logs(actor_id,action,entity_type,entity_id,details) values(p_actor_id,'freeze','subscription',p_subscription_id,jsonb_build_object('freeze_id',v_id,'from',p_start,'to',p_end));
  return jsonb_build_object('ok',true,'freeze_id',v_id);
end;$$;

create or replace function public.unfreeze_membership(p_subscription_id uuid,p_actor_id uuid)
returns jsonb language plpgsql security definer set search_path=public as $$
declare v_freeze public.subscription_freezes; v_days integer;
begin
  select * into v_freeze from public.subscription_freezes where subscription_id=p_subscription_id and status='active' for update;
  if not found then return jsonb_build_object('ok',false,'reason','NOT_FROZEN'); end if;
  v_days := greatest(1,current_date-v_freeze.start_date+1);
  update public.subscription_freezes set status='completed',actual_end_date=current_date,ended_at=now(),ended_by=p_actor_id where id=v_freeze.id;
  update public.subscriptions set end_date=end_date+v_days,status='active',updated_at=now() where id=p_subscription_id;
  insert into public.audit_logs(actor_id,action,entity_type,entity_id,details) values(p_actor_id,'unfreeze','subscription',p_subscription_id,jsonb_build_object('days_extended',v_days));
  return jsonb_build_object('ok',true,'days_extended',v_days);
end;$$;

create or replace function public.cancel_payment(p_payment_id uuid,p_reason text,p_actor_id uuid)
returns jsonb language plpgsql security definer set search_path=public as $$
declare v_payment public.payments;
begin
  if trim(coalesce(p_reason,''))='' then return jsonb_build_object('ok',false,'reason','REASON_REQUIRED'); end if;
  select * into v_payment from public.payments where id=p_payment_id and status='valid' for update;
  if not found then return jsonb_build_object('ok',false,'reason','PAYMENT_NOT_FOUND'); end if;
  update public.payments set status='cancelled',cancelled_at=now(),cancelled_by=p_actor_id,cancelled_reason=trim(p_reason) where id=p_payment_id;
  update public.subscriptions set status='cancelled',cancelled_at=now(),cancelled_by=p_actor_id,updated_at=now() where id=v_payment.subscription_id and not exists(select 1 from public.check_ins where subscription_id=v_payment.subscription_id);
  insert into public.audit_logs(actor_id,action,entity_type,entity_id,details) values(p_actor_id,'cancel_payment','payment',p_payment_id,jsonb_build_object('reason',trim(p_reason)));
  return jsonb_build_object('ok',true);
end;$$;

revoke all on function public.sell_membership(uuid,uuid,public.payment_method,uuid,date) from public,anon,authenticated;
revoke all on function public.check_in_member(text,uuid) from public,anon,authenticated;
revoke all on function public.freeze_membership(uuid,date,date,text,uuid) from public,anon,authenticated;
revoke all on function public.unfreeze_membership(uuid,uuid) from public,anon,authenticated;
revoke all on function public.cancel_payment(uuid,text,uuid) from public,anon,authenticated;
grant execute on function public.sell_membership(uuid,uuid,public.payment_method,uuid,date) to service_role;
grant execute on function public.check_in_member(text,uuid) to service_role;
grant execute on function public.freeze_membership(uuid,date,date,text,uuid) to service_role;
grant execute on function public.unfreeze_membership(uuid,uuid) to service_role;
grant execute on function public.cancel_payment(uuid,text,uuid) to service_role;
