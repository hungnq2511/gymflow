alter table public.profiles
  add column if not exists username text,
  add column if not exists must_change_password boolean not null default false;

create unique index if not exists profiles_username_unique_idx
  on public.profiles (lower(username))
  where username is not null;

alter table public.profiles
  drop constraint if exists profiles_username_format_check;

alter table public.profiles
  add constraint profiles_username_format_check
  check (username is null or username ~ '^[a-z0-9._-]{3,32}$');
