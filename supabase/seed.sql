-- GymFlow sample data
-- Yêu cầu: chạy toàn bộ migration trong supabase/migrations trước file này.
-- Có thể chạy lại: dữ liệu mẫu dùng UUID cố định và được upsert, không xóa dữ liệu thật.
-- Tài khoản quản trị: admin1@gmail.com / Admin@123

begin;
set local timezone = 'Asia/Ho_Chi_Minh';

-- 1. Một tài khoản quản trị có thể đăng nhập ngay.
insert into public.profiles
  (id, email, username, full_name, phone, role, status, must_change_password)
values
  ('00000000-0000-0000-0000-000000000101', 'admin1@gmail.com', 'admin1',
   'Quản trị viên GymFlow', '0901000001', 'manager', 'active', false)
on conflict (id) do update set
  email=excluded.email, username=excluded.username, full_name=excluded.full_name,
  phone=excluded.phone, role=excluded.role, status=excluded.status,
  must_change_password=excluded.must_change_password, auth_user_id=null,
  external_auth_id=null, updated_at=now();

-- Supabase Auth user cho tài khoản quản trị. Trigger on_auth_user_created sẽ liên kết profile.
insert into auth.users
  (instance_id, id, aud, role, email, encrypted_password, email_confirmed_at,
   raw_app_meta_data, raw_user_meta_data, created_at, updated_at,
   confirmation_token, email_change, email_change_token_new, recovery_token)
select
  '00000000-0000-0000-0000-000000000000',
  '10000000-0000-0000-0000-000000000101',
  'authenticated', 'authenticated', 'admin1@gmail.com',
  crypt('Admin@123', gen_salt('bf')), now(),
  '{"provider":"email","providers":["email"]}'::jsonb,
  '{"full_name":"Quản trị viên GymFlow","profile_id":"00000000-0000-0000-0000-000000000101"}'::jsonb,
  now(), now(), '', '', '', ''
where not exists (
  select 1 from auth.users where lower(email)=lower('admin1@gmail.com')
);

insert into auth.identities
  (id, user_id, provider_id, identity_data, provider, last_sign_in_at, created_at, updated_at)
select
  '20000000-0000-0000-0000-000000000101', u.id, u.id::text,
  jsonb_build_object('sub',u.id::text,'email',u.email,'email_verified',true,'phone_verified',false),
  'email', now(), now(), now()
from auth.users u
where lower(u.email)=lower('admin1@gmail.com')
  and not exists (
    select 1 from auth.identities i where i.user_id=u.id and i.provider='email'
  );

update public.profiles p
set auth_user_id=u.id, external_auth_id=u.id::text, updated_at=now()
from auth.users u
where p.id='00000000-0000-0000-0000-000000000101'
  and lower(u.email)=lower('admin1@gmail.com');

-- 2. Các gói tập dùng cho đăng ký và thanh toán mẫu.
insert into public.membership_plans
  (id, name, price, duration_days, visit_limit, description, terms, is_active)
values
  ('00000000-0000-0000-0000-000000000401', 'Gói tháng Unlimited', 500000, 30, null, 'Tập không giới hạn trong 30 ngày.', 'Không chuyển nhượng gói.', true),
  ('00000000-0000-0000-0000-000000000402', 'Gói quý Unlimited', 1350000, 90, null, 'Tập không giới hạn trong 90 ngày.', 'Không chuyển nhượng gói.', true),
  ('00000000-0000-0000-0000-000000000403', 'Gói 12 lượt', 420000, 60, 12, '12 lượt tập trong 60 ngày.', 'Mỗi check-in trừ một lượt.', true),
  ('00000000-0000-0000-0000-000000000404', 'Gói sinh viên', 350000, 30, null, 'Ưu đãi dành cho sinh viên.', 'Xuất trình thẻ sinh viên khi đăng ký.', true),
  ('00000000-0000-0000-0000-000000000405', 'Gói 6 tháng', 2400000, 180, null, 'Tập không giới hạn trong 180 ngày.', 'Không chuyển nhượng gói.', true)
on conflict (id) do update set
  name=excluded.name, price=excluded.price, duration_days=excluded.duration_days,
  visit_limit=excluded.visit_limit, description=excluded.description,
  terms=excluded.terms, is_active=excluded.is_active, updated_at=now();

-- 3. 20 hội viên với thông tin liên hệ và trạng thái đa dạng.
with sample_members(row_no, full_name, gender, district) as (
  values
    (1, 'Nguyễn Văn An', 'Nam', 'Quận 1, TP.HCM'),
    (2, 'Trần Thị Bình', 'Nữ', 'Quận 3, TP.HCM'),
    (3, 'Lê Hoàng Cường', 'Nam', 'Quận 4, TP.HCM'),
    (4, 'Phạm Minh Dung', 'Nữ', 'Quận 5, TP.HCM'),
    (5, 'Võ Quốc Huy', 'Nam', 'Quận 6, TP.HCM'),
    (6, 'Đỗ Thanh Giang', 'Nữ', 'Quận 7, TP.HCM'),
    (7, 'Bùi Đức Hải', 'Nam', 'Quận 8, TP.HCM'),
    (8, 'Hồ Ngọc Lan', 'Nữ', 'Quận 10, TP.HCM'),
    (9, 'Đặng Tuấn Minh', 'Nam', 'Quận 11, TP.HCM'),
    (10, 'Dương Thảo My', 'Nữ', 'Quận 12, TP.HCM'),
    (11, 'Nguyễn Nhật Nam', 'Nam', 'Bình Thạnh, TP.HCM'),
    (12, 'Trần Kim Ngân', 'Nữ', 'Phú Nhuận, TP.HCM'),
    (13, 'Lý Thành Phát', 'Nam', 'Gò Vấp, TP.HCM'),
    (14, 'Phan Bảo Trâm', 'Nữ', 'Tân Bình, TP.HCM'),
    (15, 'Vũ Hoàng Quân', 'Nam', 'Tân Phú, TP.HCM'),
    (16, 'Mai Thanh Thư', 'Nữ', 'Bình Tân, TP.HCM'),
    (17, 'Tạ Minh Tuấn', 'Nam', 'Thủ Đức, TP.HCM'),
    (18, 'Đinh Khánh Vy', 'Nữ', 'Nhà Bè, TP.HCM'),
    (19, 'Ngô Anh Khoa', 'Nam', 'Hóc Môn, TP.HCM'),
    (20, 'Cao Thu Trang', 'Nữ', 'Củ Chi, TP.HCM')
)
insert into public.members
  (id, profile_id, member_code, qr_token, full_name, phone, email, date_of_birth,
   gender, address, emergency_contact, notes, status, created_at)
select
  ('00000000-0000-0000-0000-' || lpad((300+row_no)::text,12,'0'))::uuid,
  null,
  'GF-' || lpad(row_no::text,4,'0'),
  ('10000000-0000-0000-0000-' || lpad(row_no::text,12,'0'))::uuid,
  full_name,
  '0902' || lpad(row_no::text,6,'0'),
  'hoivien' || lpad(row_no::text,2,'0') || '@gymflow.vn',
  (date '1988-01-01' + row_no * interval '240 days')::date,
  gender,
  district,
  'Người thân - 0913' || lpad(row_no::text,6,'0'),
  case
    when row_no between 13 and 16 then 'Hội viên đã hết hạn gói.'
    when row_no=19 then 'Gói tập đang đóng băng.'
    when row_no=20 then 'Hội viên đã ngừng hoạt động.'
    else 'Hội viên mẫu đang hoạt động.'
  end,
  case when row_no=20 then 'inactive' else 'active' end::public.record_status,
  now() - row_no * interval '4 days'
from sample_members
on conflict (id) do update set
  profile_id=excluded.profile_id, member_code=excluded.member_code, qr_token=excluded.qr_token,
  full_name=excluded.full_name, phone=excluded.phone, email=excluded.email,
  date_of_birth=excluded.date_of_birth, gender=excluded.gender, address=excluded.address,
  emergency_contact=excluded.emergency_contact, notes=excluded.notes,
  status=excluded.status, updated_at=now();

-- 4. Mỗi hội viên có một đăng ký gói để bảo đảm 20 thanh toán hợp lệ khóa ngoại.
with rows as (select generate_series(1,20) as row_no), subscription_data as (
  select
    r.row_no,
    ('00000000-0000-0000-0000-' || lpad((300+r.row_no)::text,12,'0'))::uuid as member_id,
    ('00000000-0000-0000-0000-' || lpad((400+((r.row_no-1)%5)+1)::text,12,'0'))::uuid as plan_id,
    case
      when r.row_no between 13 and 16 then current_date-p.duration_days-r.row_no
      when r.row_no between 17 and 18 then current_date+r.row_no
      else current_date-r.row_no
    end as start_date,
    p.*
  from rows r
  join public.membership_plans p
    on p.id=('00000000-0000-0000-0000-' || lpad((400+((r.row_no-1)%5)+1)::text,12,'0'))::uuid
)
insert into public.subscriptions
  (id, member_id, plan_id, start_date, end_date, remaining_visits, status,
   plan_name_snapshot, price_snapshot, duration_days_snapshot, visit_limit_snapshot,
   sale_type, cancelled_at, cancelled_by, created_at)
select
  ('00000000-0000-0000-0000-' || lpad((500+row_no)::text,12,'0'))::uuid,
  member_id, plan_id, start_date, start_date+duration_days-1,
  case when visit_limit is null then null else greatest(visit_limit-(row_no%6),0) end,
  case
    when row_no between 13 and 16 then 'expired'
    when row_no between 17 and 18 then 'scheduled'
    when row_no=19 then 'frozen'
    when row_no=20 then 'cancelled'
    else 'active'
  end,
  name, price, duration_days, visit_limit,
  case when row_no%5=0 then 'renewal' else 'new' end,
  case when row_no=20 then now()-interval '2 days' else null end,
  case when row_no=20 then '00000000-0000-0000-0000-000000000101'::uuid else null end,
  now()-row_no*interval '4 days'
from subscription_data
on conflict (id) do update set
  member_id=excluded.member_id, plan_id=excluded.plan_id, start_date=excluded.start_date,
  end_date=excluded.end_date, remaining_visits=excluded.remaining_visits, status=excluded.status,
  plan_name_snapshot=excluded.plan_name_snapshot, price_snapshot=excluded.price_snapshot,
  duration_days_snapshot=excluded.duration_days_snapshot,
  visit_limit_snapshot=excluded.visit_limit_snapshot, sale_type=excluded.sale_type,
  cancelled_at=excluded.cancelled_at, cancelled_by=excluded.cancelled_by, updated_at=now();

-- 5. 20 thanh toán: xen kẽ tiền mặt/chuyển khoản, có một giao dịch đã hủy.
with rows as (select generate_series(1,20) as row_no)
insert into public.payments
  (id, receipt_code, subscription_id, member_id, amount, method, status,
   recorded_by, paid_at, cancelled_at, cancelled_by, cancelled_reason)
select
  ('00000000-0000-0000-0000-' || lpad((600+row_no)::text,12,'0'))::uuid,
  'PT-' || to_char(current_date,'YYYYMM') || '-' || lpad(row_no::text,4,'0'),
  ('00000000-0000-0000-0000-' || lpad((500+row_no)::text,12,'0'))::uuid,
  ('00000000-0000-0000-0000-' || lpad((300+row_no)::text,12,'0'))::uuid,
  s.price_snapshot,
  case when row_no%2=0 then 'bank_transfer' else 'cash' end::public.payment_method,
  case when row_no=20 then 'cancelled' else 'valid' end::public.payment_status,
  '00000000-0000-0000-0000-000000000101',
  now()-row_no*interval '36 hours',
  case when row_no=20 then now()-interval '2 days' else null end,
  case when row_no=20 then '00000000-0000-0000-0000-000000000101'::uuid else null end,
  case when row_no=20 then 'Khách yêu cầu hủy giao dịch mẫu' else null end
from rows
join public.subscriptions s
  on s.id=('00000000-0000-0000-0000-' || lpad((500+row_no)::text,12,'0'))::uuid
on conflict (id) do update set
  receipt_code=excluded.receipt_code, subscription_id=excluded.subscription_id,
  member_id=excluded.member_id, amount=excluded.amount, method=excluded.method,
  status=excluded.status, recorded_by=excluded.recorded_by, paid_at=excluded.paid_at,
  cancelled_at=excluded.cancelled_at, cancelled_by=excluded.cancelled_by,
  cancelled_reason=excluded.cancelled_reason;

-- 6. 10 khoản chi phí thuộc nhiều danh mục khác nhau.
with sample_expenses(row_no, category_name, description, amount, days_ago, recurring) as (
  values
    (1, 'Thuê mặt bằng', 'Tiền thuê mặt bằng tháng này', 18000000::numeric, 2, true),
    (2, 'Điện nước', 'Tiền điện tháng này', 4200000::numeric, 3, true),
    (3, 'Điện nước', 'Tiền nước tháng này', 950000::numeric, 3, true),
    (4, 'Lương nhân sự', 'Lương huấn luyện viên', 12000000::numeric, 5, true),
    (5, 'Lương nhân sự', 'Lương nhân viên lễ tân', 8000000::numeric, 5, true),
    (6, 'Thiết bị', 'Bảo trì máy chạy bộ', 2500000::numeric, 7, false),
    (7, 'Thiết bị', 'Mua thảm tập yoga', 1800000::numeric, 9, false),
    (8, 'Marketing', 'Quảng cáo mạng xã hội', 3000000::numeric, 11, false),
    (9, 'Khác', 'Nước uống cho hội viên', 1200000::numeric, 13, true),
    (10, 'Khác', 'Vệ sinh và giặt khăn', 1600000::numeric, 15, true)
)
insert into public.expenses
  (id, category_id, description, amount, expense_date, receipt_number,
   recurring, status, created_by, created_at)
select
  ('00000000-0000-0000-0000-' || lpad((1400+e.row_no)::text,12,'0'))::uuid,
  c.id, e.description, e.amount, current_date-e.days_ago,
  'CP-' || to_char(current_date,'YYYYMM') || '-' || lpad(e.row_no::text,3,'0'),
  e.recurring, 'valid', '00000000-0000-0000-0000-000000000101',
  now()-e.days_ago*interval '1 day'
from sample_expenses e
join public.expense_categories c on c.name=e.category_name
on conflict (id) do update set
  category_id=excluded.category_id, description=excluded.description,
  amount=excluded.amount, expense_date=excluded.expense_date,
  receipt_number=excluded.receipt_number, recurring=excluded.recurring,
  status=excluded.status, created_by=excluded.created_by;

commit;

-- Kết quả mong đợi trên database mới: 1 admin, 20 hội viên, 20 thanh toán, 10 chi phí.
select 'admin_accounts' as data_type, count(*) as sample_rows
from public.profiles where id='00000000-0000-0000-0000-000000000101'
union all
select 'members', count(*) from public.members
where id between '00000000-0000-0000-0000-000000000301' and '00000000-0000-0000-0000-000000000320'
union all
select 'payments', count(*) from public.payments
where id between '00000000-0000-0000-0000-000000000601' and '00000000-0000-0000-0000-000000000620'
union all
select 'expenses', count(*) from public.expenses
where id between '00000000-0000-0000-0000-000000001401' and '00000000-0000-0000-0000-000000001410';
