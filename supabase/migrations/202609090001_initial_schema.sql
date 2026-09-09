create extension if not exists pgcrypto;
create type public.user_role as enum ('manager','staff','member');
create type public.record_status as enum ('active','inactive');
create type public.subscription_status as enum ('active','cancelled');
create type public.payment_method as enum ('cash','bank_transfer');
create type public.payment_status as enum ('valid','cancelled');

create table public.profiles(id uuid primary key default gen_random_uuid(),external_auth_id text unique not null,email text unique not null,full_name text not null,phone text,role public.user_role not null default 'member',status public.record_status not null default 'active',created_at timestamptz not null default now());
create table public.members(id uuid primary key default gen_random_uuid(),profile_id uuid unique references public.profiles(id),member_code text unique not null,qr_token uuid unique not null default gen_random_uuid(),full_name text not null,phone text not null,email text,date_of_birth date,gender text,address text,emergency_contact text,avatar_url text,notes text,status public.record_status not null default 'active',created_at timestamptz not null default now());
create table public.membership_plans(id uuid primary key default gen_random_uuid(),name text not null,price numeric(14,2) not null check(price>=0),duration_days integer not null check(duration_days>0),visit_limit integer check(visit_limit is null or visit_limit>0),is_active boolean not null default true,created_at timestamptz not null default now());
create table public.subscriptions(id uuid primary key default gen_random_uuid(),member_id uuid not null references public.members(id),plan_id uuid not null references public.membership_plans(id),start_date date not null,end_date date not null check(end_date>=start_date),remaining_visits integer check(remaining_visits is null or remaining_visits>=0),status public.subscription_status not null default 'active',cancelled_at timestamptz,cancelled_by uuid references public.profiles(id),created_at timestamptz not null default now());
create table public.payments(id uuid primary key default gen_random_uuid(),subscription_id uuid not null references public.subscriptions(id),member_id uuid not null references public.members(id),amount numeric(14,2) not null check(amount>0),method public.payment_method not null,status public.payment_status not null default 'valid',recorded_by uuid not null references public.profiles(id),paid_at timestamptz not null default now(),cancelled_at timestamptz,cancelled_by uuid references public.profiles(id));
create table public.check_ins(id uuid primary key default gen_random_uuid(),member_id uuid not null references public.members(id),subscription_id uuid not null references public.subscriptions(id),checked_in_by uuid not null references public.profiles(id),checked_in_at timestamptz not null default now());
create table public.audit_logs(id uuid primary key default gen_random_uuid(),actor_id uuid not null references public.profiles(id),action text not null,entity_type text not null,entity_id uuid not null,details jsonb,created_at timestamptz not null default now());

create index members_name_idx on public.members using gin(to_tsvector('simple',full_name));
create index subscriptions_member_idx on public.subscriptions(member_id,status,end_date);
create index payments_paid_at_idx on public.payments(paid_at desc) where status='valid';
create index check_ins_member_time_idx on public.check_ins(member_id,checked_in_at desc);

alter table public.profiles enable row level security;
alter table public.members enable row level security;
alter table public.membership_plans enable row level security;
alter table public.subscriptions enable row level security;
alter table public.payments enable row level security;
alter table public.check_ins enable row level security;
alter table public.audit_logs enable row level security;
-- Không cấp policy cho anon/authenticated. Ứng dụng truy cập qua API server đã xác thực,
-- dùng service role; service role bypass RLS. Tuyệt đối không đưa key này xuống browser.
create policy "public can read active plans" on public.membership_plans for select to anon, authenticated using (is_active = true);

create or replace function public.check_in_member(p_qr_token text,p_actor_id uuid)
returns jsonb language plpgsql security definer set search_path=public as $$
declare v_member public.members;v_subscription public.subscriptions;v_last timestamptz;v_checkin uuid;
begin
  select * into v_member from public.members where qr_token::text=p_qr_token for update;
  if not found then return jsonb_build_object('ok',false,'reason','INVALID_QR');end if;
  if v_member.status<>'active' then return jsonb_build_object('ok',false,'reason','MEMBER_INACTIVE');end if;
  select * into v_subscription from public.subscriptions where member_id=v_member.id and status='active' and end_date>=current_date and (remaining_visits is null or remaining_visits>0) order by end_date limit 1 for update;
  if not found then return jsonb_build_object('ok',false,'reason','NO_VALID_SUBSCRIPTION');end if;
  select checked_in_at into v_last from public.check_ins where member_id=v_member.id order by checked_in_at desc limit 1;
  if v_last is not null and v_last>now()-interval '10 minutes' then return jsonb_build_object('ok',false,'reason','DUPLICATE');end if;
  insert into public.check_ins(member_id,subscription_id,checked_in_by) values(v_member.id,v_subscription.id,p_actor_id) returning id into v_checkin;
  if v_subscription.remaining_visits is not null then update public.subscriptions set remaining_visits=remaining_visits-1 where id=v_subscription.id;end if;
  insert into public.audit_logs(actor_id,action,entity_type,entity_id,details) values(p_actor_id,'check_in','member',v_member.id,jsonb_build_object('check_in_id',v_checkin));
  return jsonb_build_object('ok',true,'check_in_id',v_checkin,'member_id',v_member.id,'member_name',v_member.full_name);
end;$$;

revoke all on function public.check_in_member(text,uuid) from public,anon,authenticated;
grant execute on function public.check_in_member(text,uuid) to service_role;
