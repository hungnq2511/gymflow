-- Remove the class scheduling and booking module while preserving audit logs.
begin;

drop function if exists public.cancel_class_booking(uuid,uuid);
drop function if exists public.book_class_session(uuid,uuid,uuid);

delete from public.notifications where kind='class_waitlist_promoted';
alter table public.notifications drop constraint if exists notifications_kind_check;
alter table public.notifications add constraint notifications_kind_check
  check(kind in ('subscription_expiring','visits_running_low','follow_up_due'));

drop table if exists public.class_bookings;
drop table if exists public.class_sessions;
drop table if exists public.trainers;
drop table if exists public.class_types;

commit;
