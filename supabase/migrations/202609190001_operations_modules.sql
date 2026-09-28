-- GymFlow operations modules: retention, classes and expenses.

create table if not exists public.member_follow_ups(
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references public.members(id) on delete cascade,
  assigned_to uuid references public.profiles(id) on delete set null,
  status text not null default 'pending' check(status in ('pending','contacted','scheduled','renewed','not_interested')),
  note text,
  next_contact_at timestamptz,
  created_by uuid not null references public.profiles(id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.notifications(
  id uuid primary key default gen_random_uuid(),
  recipient_id uuid references public.profiles(id) on delete cascade,
  member_id uuid references public.members(id) on delete cascade,
  kind text not null check(kind in ('subscription_expiring','visits_running_low','follow_up_due','class_waitlist_promoted')),
  title text not null,
  body text not null,
  dedupe_key text not null unique,
  read_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.class_types(
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  description text,
  duration_minutes integer not null check(duration_minutes between 15 and 300),
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.trainers(
  id uuid primary key default gen_random_uuid(),
  full_name text not null,
  phone text,
  specialty text,
  status public.record_status not null default 'active',
  created_at timestamptz not null default now()
);

create table if not exists public.class_sessions(
  id uuid primary key default gen_random_uuid(),
  class_type_id uuid not null references public.class_types(id),
  trainer_id uuid references public.trainers(id) on delete set null,
  starts_at timestamptz not null,
  ends_at timestamptz not null,
  room text not null,
  capacity integer not null check(capacity between 1 and 500),
  status text not null default 'scheduled' check(status in ('scheduled','completed','cancelled')),
  created_by uuid not null references public.profiles(id),
  created_at timestamptz not null default now(),
  check(ends_at > starts_at)
);

create table if not exists public.class_bookings(
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.class_sessions(id) on delete cascade,
  member_id uuid not null references public.members(id) on delete cascade,
  status text not null check(status in ('booked','waitlisted','cancelled','attended','no_show')),
  position integer,
  booked_at timestamptz not null default now(),
  cancelled_at timestamptz,
  unique(session_id,member_id)
);

create table if not exists public.expense_categories(
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.expenses(
  id uuid primary key default gen_random_uuid(),
  category_id uuid not null references public.expense_categories(id),
  description text not null,
  amount numeric(14,2) not null check(amount > 0),
  expense_date date not null,
  receipt_number text,
  recurring boolean not null default false,
  status text not null default 'valid' check(status in ('valid','cancelled')),
  created_by uuid not null references public.profiles(id),
  created_at timestamptz not null default now(),
  cancelled_at timestamptz,
  cancelled_by uuid references public.profiles(id)
);

create index if not exists follow_ups_member_status_idx on public.member_follow_ups(member_id,status,next_contact_at);
create index if not exists notifications_recipient_unread_idx on public.notifications(recipient_id,read_at,created_at desc);
create index if not exists class_sessions_starts_idx on public.class_sessions(starts_at,status);
create index if not exists class_bookings_session_status_idx on public.class_bookings(session_id,status,position);
create index if not exists expenses_date_status_idx on public.expenses(expense_date,status);
create index if not exists subscriptions_end_status_idx on public.subscriptions(end_date,status);

alter table public.member_follow_ups enable row level security;
alter table public.notifications enable row level security;
alter table public.class_types enable row level security;
alter table public.trainers enable row level security;
alter table public.class_sessions enable row level security;
alter table public.class_bookings enable row level security;
alter table public.expense_categories enable row level security;
alter table public.expenses enable row level security;

create policy "staff read follow ups" on public.member_follow_ups for select to authenticated using(public.current_user_role() in ('manager','staff'));
create policy "users read notifications" on public.notifications for select to authenticated using(recipient_id=public.current_profile_id() or (recipient_id is null and public.current_user_role() in ('manager','staff')));
create policy "users read class types" on public.class_types for select to authenticated using(public.current_user_role() in ('manager','staff','member'));
create policy "users read trainers" on public.trainers for select to authenticated using(public.current_user_role() in ('manager','staff','member'));
create policy "users read class sessions" on public.class_sessions for select to authenticated using(public.current_user_role() in ('manager','staff','member'));
create policy "staff read bookings" on public.class_bookings for select to authenticated using(public.current_user_role() in ('manager','staff'));
create policy "member reads bookings" on public.class_bookings for select to authenticated using(member_id in(select id from public.members where profile_id=public.current_profile_id()));
create policy "manager reads expense categories" on public.expense_categories for select to authenticated using(public.current_user_role()='manager');
create policy "manager reads expenses" on public.expenses for select to authenticated using(public.current_user_role()='manager');

create or replace function public.book_class_session(p_session_id uuid,p_member_id uuid,p_actor_id uuid)
returns jsonb language plpgsql security definer set search_path=public as $$
declare v_session public.class_sessions; v_member public.members; v_booked integer; v_position integer; v_status text; v_id uuid;
begin
  select * into v_session from public.class_sessions where id=p_session_id for update;
  if not found or v_session.status<>'scheduled' then return jsonb_build_object('ok',false,'reason','SESSION_NOT_AVAILABLE'); end if;
  if v_session.starts_at<=now() then return jsonb_build_object('ok',false,'reason','SESSION_STARTED'); end if;
  select * into v_member from public.members where id=p_member_id and status='active';
  if not found then return jsonb_build_object('ok',false,'reason','MEMBER_NOT_ACTIVE'); end if;
  if not exists(select 1 from public.subscriptions where member_id=p_member_id and status in ('active','scheduled') and end_date>=v_session.starts_at::date and start_date<=v_session.starts_at::date) then
    return jsonb_build_object('ok',false,'reason','NO_VALID_SUBSCRIPTION');
  end if;
  if exists(select 1 from public.class_bookings where session_id=p_session_id and member_id=p_member_id and status<>'cancelled') then
    return jsonb_build_object('ok',false,'reason','ALREADY_BOOKED');
  end if;
  select count(*) into v_booked from public.class_bookings where session_id=p_session_id and status in ('booked','attended');
  if v_booked<v_session.capacity then v_status:='booked'; v_position:=null;
  else
    v_status:='waitlisted';
    select coalesce(max(position),0)+1 into v_position from public.class_bookings where session_id=p_session_id and status='waitlisted';
  end if;
  insert into public.class_bookings(session_id,member_id,status,position) values(p_session_id,p_member_id,v_status,v_position)
  on conflict(session_id,member_id) do update set status=excluded.status,position=excluded.position,booked_at=now(),cancelled_at=null returning id into v_id;
  insert into public.audit_logs(actor_id,action,entity_type,entity_id,details) values(p_actor_id,'book_class','class_booking',v_id,jsonb_build_object('status',v_status));
  return jsonb_build_object('ok',true,'booking_id',v_id,'status',v_status,'position',v_position);
end;$$;

create or replace function public.cancel_class_booking(p_booking_id uuid,p_actor_id uuid)
returns jsonb language plpgsql security definer set search_path=public as $$
declare v_booking public.class_bookings; v_promoted public.class_bookings; v_member_profile uuid;
begin
  select * into v_booking from public.class_bookings where id=p_booking_id for update;
  if not found or v_booking.status not in ('booked','waitlisted') then return jsonb_build_object('ok',false,'reason','BOOKING_NOT_ACTIVE'); end if;
  update public.class_bookings set status='cancelled',cancelled_at=now(),position=null where id=p_booking_id;
  if v_booking.status='booked' then
    select * into v_promoted from public.class_bookings where session_id=v_booking.session_id and status='waitlisted' order by position,booked_at limit 1 for update;
    if found then
      update public.class_bookings set status='booked',position=null where id=v_promoted.id;
      select profile_id into v_member_profile from public.members where id=v_promoted.member_id;
      if v_member_profile is not null then
        insert into public.notifications(recipient_id,member_id,kind,title,body,dedupe_key)
        values(v_member_profile,v_promoted.member_id,'class_waitlist_promoted','Bạn đã có chỗ trong lớp','Một chỗ trống vừa được mở cho bạn.','class-promoted:'||v_promoted.id::text)
        on conflict(dedupe_key) do nothing;
      end if;
    end if;
  end if;
  insert into public.audit_logs(actor_id,action,entity_type,entity_id) values(p_actor_id,'cancel_class_booking','class_booking',p_booking_id);
  return jsonb_build_object('ok',true);
end;$$;

revoke all on function public.book_class_session(uuid,uuid,uuid) from public,anon,authenticated;
revoke all on function public.cancel_class_booking(uuid,uuid) from public,anon,authenticated;
grant execute on function public.book_class_session(uuid,uuid,uuid) to service_role;
grant execute on function public.cancel_class_booking(uuid,uuid) to service_role;

insert into public.expense_categories(name) values
  ('Thuê mặt bằng'),('Điện nước'),('Lương nhân sự'),('Thiết bị'),('Marketing'),('Khác')
on conflict(name) do nothing;
