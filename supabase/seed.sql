-- GymFlow MVP demo data
-- Yêu cầu: đã chạy đủ 3 migration trước khi chạy file này.
-- An toàn khi chạy lại: chỉ cập nhật các bản ghi demo có UUID cố định, không xóa dữ liệu thật.

begin;
set local timezone = 'Asia/Ho_Chi_Minh';

-- 1. Hồ sơ quản lý, nhân viên và 2 tài khoản hội viên mẫu.
-- Muốn đăng nhập, tạo Auth User trong Supabase Authentication bằng đúng email bên dưới.
insert into public.profiles (id, email, full_name, phone, role, status)
values
  ('00000000-0000-0000-0000-000000000101', 'manager.demo@gymflow.local', 'Nguyễn Minh Quản', '0901000001', 'manager', 'active'),
  ('00000000-0000-0000-0000-000000000102', 'staff.demo@gymflow.local',   'Trần Thu Lễ Tân',  '0901000002', 'staff',   'active'),
  ('00000000-0000-0000-0000-000000000201', 'member.demo@gymflow.local',  'Nguyễn Văn An',    '0902000001', 'member',  'active'),
  ('00000000-0000-0000-0000-000000000202', 'member2.demo@gymflow.local', 'Trần Thị Bình',     '0902000002', 'member',  'active')
on conflict (id) do update set
  email=excluded.email, full_name=excluded.full_name, phone=excluded.phone,
  role=excluded.role, status=excluded.status, updated_at=now();

-- 2. Các loại gói: không giới hạn, theo lượt và ngừng bán.
insert into public.membership_plans
  (id, name, price, duration_days, visit_limit, description, terms, is_active)
values
  ('00000000-0000-0000-0000-000000000401', 'Gói tháng Unlimited', 500000, 30, null, 'Tập không giới hạn trong 30 ngày.', 'Check-in tối đa một lần trong 10 phút.', true),
  ('00000000-0000-0000-0000-000000000402', 'Gói quý Unlimited',  1350000, 90, null, 'Tập không giới hạn trong 90 ngày.', 'Không chuyển nhượng gói.', true),
  ('00000000-0000-0000-0000-000000000403', 'Gói 12 lượt',          420000, 60, 12,   '12 lượt tập, sử dụng trong 60 ngày.', 'Mỗi check-in trừ một lượt.', true),
  ('00000000-0000-0000-0000-000000000404', 'Gói sinh viên',        350000, 30, null, 'Ưu đãi dành cho sinh viên.', 'Xuất trình thẻ sinh viên khi đăng ký.', true),
  ('00000000-0000-0000-0000-000000000405', 'Gói cũ 6 tháng',      2100000, 180, null,'Gói cũ để kiểm tra lịch sử.', null, false)
on conflict (id) do update set
  name=excluded.name, price=excluded.price, duration_days=excluded.duration_days,
  visit_limit=excluded.visit_limit, description=excluded.description,
  terms=excluded.terms, is_active=excluded.is_active, updated_at=now();

-- 3. Hội viên: đang tập, sắp hết hạn, đóng băng, hết hạn, ngừng hoạt động và chưa mua gói.
insert into public.members
  (id, profile_id, member_code, qr_token, full_name, phone, email, date_of_birth,
   gender, address, emergency_contact, notes, status, created_at)
values
  ('00000000-0000-0000-0000-000000000301', '00000000-0000-0000-0000-000000000201', 'GF-DEMO01', '10000000-0000-0000-0000-000000000001', 'Nguyễn Văn An', '0902000001', 'member.demo@gymflow.local',  '1998-04-15', 'Nam', 'Quận 7, TP.HCM', 'Nguyễn Văn Ba - 0909000001', 'Hội viên đang tập và đã gia hạn.', 'active', now()-interval '20 days'),
  ('00000000-0000-0000-0000-000000000302', '00000000-0000-0000-0000-000000000202', 'GF-DEMO02', '10000000-0000-0000-0000-000000000002', 'Trần Thị Bình',  '0902000002', 'member2.demo@gymflow.local', '2001-09-20', 'Nữ', 'Quận 4, TP.HCM', 'Trần Văn Minh - 0909000002', 'Gói theo lượt sắp hết hạn.', 'active', now()-interval '18 days'),
  ('00000000-0000-0000-0000-000000000303', null, 'GF-DEMO03', '10000000-0000-0000-0000-000000000003', 'Lê Hoàng Cường', '0902000003', 'cuong.demo@gymflow.local', '1995-01-11', 'Nam', 'Nhà Bè, TP.HCM', 'Lê Thị Hoa - 0909000003', 'Đang đóng băng gói.', 'active', now()-interval '40 days'),
  ('00000000-0000-0000-0000-000000000304', null, 'GF-DEMO04', '10000000-0000-0000-0000-000000000004', 'Phạm Minh Dung',  '0902000004', 'dung.demo@gymflow.local', '1992-06-08', 'Nữ', 'Quận 1, TP.HCM', null, 'Gói đã hết hạn.', 'active', now()-interval '80 days'),
  ('00000000-0000-0000-0000-000000000305', null, 'GF-DEMO05', '10000000-0000-0000-0000-000000000005', 'Võ Quốc Em',      '0902000005', 'em.demo@gymflow.local',   '1989-12-12', 'Nam', 'Thủ Đức, TP.HCM', null, 'Hội viên đã ngừng hoạt động.', 'inactive', now()-interval '120 days'),
  ('00000000-0000-0000-0000-000000000306', null, 'GF-DEMO06', '10000000-0000-0000-0000-000000000006', 'Đỗ Thanh Giang',   '0902000006', 'giang.demo@gymflow.local','2003-03-22', 'Khác', 'Bình Thạnh, TP.HCM', null, 'Hội viên mới chưa mua gói.', 'active', now()-interval '2 days')
on conflict (id) do update set
  profile_id=excluded.profile_id, member_code=excluded.member_code, qr_token=excluded.qr_token,
  full_name=excluded.full_name, phone=excluded.phone, email=excluded.email,
  date_of_birth=excluded.date_of_birth, gender=excluded.gender, address=excluded.address,
  emergency_contact=excluded.emergency_contact, notes=excluded.notes,
  status=excluded.status, updated_at=now();

-- 4. Đăng ký gói: active, scheduled (gia hạn), frozen, expired và cancelled.
insert into public.subscriptions
  (id, member_id, plan_id, start_date, end_date, remaining_visits, status,
   plan_name_snapshot, price_snapshot, duration_days_snapshot, visit_limit_snapshot,
   sale_type, cancelled_at, cancelled_by, created_at)
values
  ('00000000-0000-0000-0000-000000000501', '00000000-0000-0000-0000-000000000301', '00000000-0000-0000-0000-000000000401', current_date-10, current_date+19, null, 'active',    'Gói tháng Unlimited', 500000, 30, null, 'new',     null, null, now()-interval '10 days'),
  ('00000000-0000-0000-0000-000000000502', '00000000-0000-0000-0000-000000000301', '00000000-0000-0000-0000-000000000402', current_date+20, current_date+109, null, 'scheduled','Gói quý Unlimited', 1350000, 90, null, 'renewal', null, null, now()-interval '1 day'),
  ('00000000-0000-0000-0000-000000000503', '00000000-0000-0000-0000-000000000302', '00000000-0000-0000-0000-000000000403', current_date-56, current_date+3, 3,    'active',    'Gói 12 lượt', 420000, 60, 12, 'new', null, null, now()-interval '56 days'),
  ('00000000-0000-0000-0000-000000000504', '00000000-0000-0000-0000-000000000303', '00000000-0000-0000-0000-000000000402', current_date-30, current_date+59, null, 'frozen',   'Gói quý Unlimited', 1350000, 90, null, 'new', null, null, now()-interval '30 days'),
  ('00000000-0000-0000-0000-000000000505', '00000000-0000-0000-0000-000000000304', '00000000-0000-0000-0000-000000000401', current_date-35, current_date-6, null, 'expired',   'Gói tháng Unlimited', 500000, 30, null, 'new', null, null, now()-interval '35 days'),
  ('00000000-0000-0000-0000-000000000506', '00000000-0000-0000-0000-000000000305', '00000000-0000-0000-0000-000000000405', current_date-120,current_date+59,null, 'cancelled', 'Gói cũ 6 tháng', 2100000, 180, null, 'new', now()-interval '90 days', '00000000-0000-0000-0000-000000000101', now()-interval '120 days')
on conflict (id) do update set
  member_id=excluded.member_id, plan_id=excluded.plan_id, start_date=excluded.start_date,
  end_date=excluded.end_date, remaining_visits=excluded.remaining_visits, status=excluded.status,
  plan_name_snapshot=excluded.plan_name_snapshot, price_snapshot=excluded.price_snapshot,
  duration_days_snapshot=excluded.duration_days_snapshot, visit_limit_snapshot=excluded.visit_limit_snapshot,
  sale_type=excluded.sale_type, cancelled_at=excluded.cancelled_at,
  cancelled_by=excluded.cancelled_by, updated_at=now();

-- 5. Thanh toán: tiền mặt, chuyển khoản, gia hạn và giao dịch đã hủy.
insert into public.payments
  (id, receipt_code, subscription_id, member_id, amount, method, status,
   recorded_by, paid_at, cancelled_at, cancelled_by, cancelled_reason)
values
  ('00000000-0000-0000-0000-000000000601', 'PT-DEMO-0001', '00000000-0000-0000-0000-000000000501', '00000000-0000-0000-0000-000000000301', 500000,  'cash',          'valid',     '00000000-0000-0000-0000-000000000102', now()-interval '10 days', null, null, null),
  ('00000000-0000-0000-0000-000000000602', 'PT-DEMO-0002', '00000000-0000-0000-0000-000000000502', '00000000-0000-0000-0000-000000000301', 1350000, 'bank_transfer', 'valid',     '00000000-0000-0000-0000-000000000101', now()-interval '1 day',  null, null, null),
  ('00000000-0000-0000-0000-000000000603', 'PT-DEMO-0003', '00000000-0000-0000-0000-000000000503', '00000000-0000-0000-0000-000000000302', 420000,  'cash',          'valid',     '00000000-0000-0000-0000-000000000102', now()-interval '56 days', null, null, null),
  ('00000000-0000-0000-0000-000000000604', 'PT-DEMO-0004', '00000000-0000-0000-0000-000000000504', '00000000-0000-0000-0000-000000000303', 1350000, 'bank_transfer', 'valid',     '00000000-0000-0000-0000-000000000101', now()-interval '30 days', null, null, null),
  ('00000000-0000-0000-0000-000000000605', 'PT-DEMO-0005', '00000000-0000-0000-0000-000000000505', '00000000-0000-0000-0000-000000000304', 500000,  'cash',          'valid',     '00000000-0000-0000-0000-000000000102', now()-interval '35 days', null, null, null),
  ('00000000-0000-0000-0000-000000000606', 'PT-DEMO-0006', '00000000-0000-0000-0000-000000000506', '00000000-0000-0000-0000-000000000305', 2100000, 'bank_transfer', 'cancelled', '00000000-0000-0000-0000-000000000102', now()-interval '120 days',now()-interval '90 days','00000000-0000-0000-0000-000000000101','Khách yêu cầu hủy giao dịch mẫu')
on conflict (id) do update set
  receipt_code=excluded.receipt_code, subscription_id=excluded.subscription_id,
  member_id=excluded.member_id, amount=excluded.amount, method=excluded.method,
  status=excluded.status, recorded_by=excluded.recorded_by, paid_at=excluded.paid_at,
  cancelled_at=excluded.cancelled_at, cancelled_by=excluded.cancelled_by,
  cancelled_reason=excluded.cancelled_reason;

-- 6. Lịch sử check-in trong hôm nay và những ngày gần đây.
insert into public.check_ins (id, member_id, subscription_id, checked_in_by, checked_in_at)
values
  ('00000000-0000-0000-0000-000000000701', '00000000-0000-0000-0000-000000000301', '00000000-0000-0000-0000-000000000501', '00000000-0000-0000-0000-000000000102', now()-interval '1 hour'),
  ('00000000-0000-0000-0000-000000000702', '00000000-0000-0000-0000-000000000302', '00000000-0000-0000-0000-000000000503', '00000000-0000-0000-0000-000000000102', now()-interval '3 hours'),
  ('00000000-0000-0000-0000-000000000703', '00000000-0000-0000-0000-000000000301', '00000000-0000-0000-0000-000000000501', '00000000-0000-0000-0000-000000000101', now()-interval '1 day'),
  ('00000000-0000-0000-0000-000000000704', '00000000-0000-0000-0000-000000000302', '00000000-0000-0000-0000-000000000503', '00000000-0000-0000-0000-000000000102', now()-interval '2 days'),
  ('00000000-0000-0000-0000-000000000705', '00000000-0000-0000-0000-000000000303', '00000000-0000-0000-0000-000000000504', '00000000-0000-0000-0000-000000000101', now()-interval '5 days')
on conflict (id) do update set checked_in_at=excluded.checked_in_at;

-- 7. Một kỳ đóng băng đang hoạt động.
insert into public.subscription_freezes
  (id, subscription_id, start_date, expected_end_date, reason, status, created_by, created_at)
values
  ('00000000-0000-0000-0000-000000000801', '00000000-0000-0000-0000-000000000504', current_date-2, current_date+5, 'Đi công tác 1 tuần', 'active', '00000000-0000-0000-0000-000000000101', now()-interval '2 days')
on conflict (id) do update set
  start_date=excluded.start_date, expected_end_date=excluded.expected_end_date,
  reason=excluded.reason, status=excluded.status, created_by=excluded.created_by;

-- 8. Dữ liệu mẫu cho chăm sóc hội viên.
insert into public.member_follow_ups
  (id, member_id, assigned_to, status, note, next_contact_at, created_by)
values
  ('00000000-0000-0000-0000-000000001501', '00000000-0000-0000-0000-000000000302', '00000000-0000-0000-0000-000000000102', 'scheduled', 'Khách muốn được gọi lại để tư vấn gia hạn.', now()+interval '1 day', '00000000-0000-0000-0000-000000000101')
on conflict (id) do update set status=excluded.status, note=excluded.note, next_contact_at=excluded.next_contact_at, updated_at=now();

-- 9. Chi phí mẫu trong tháng hiện tại.
insert into public.expenses(id,category_id,description,amount,expense_date,receipt_number,created_by)
select '00000000-0000-0000-0000-000000001401',id,'Tiền điện nước tháng này',350000,current_date,'HD-DEMO-01','00000000-0000-0000-0000-000000000101'
from public.expense_categories where name='Điện nước'
on conflict (id) do update set amount=excluded.amount,expense_date=excluded.expense_date,receipt_number=excluded.receipt_number;

-- 10. Nhật ký thao tác quan trọng.
insert into public.audit_logs (id, actor_id, action, entity_type, entity_id, details, created_at)
values
  ('00000000-0000-0000-0000-000000000901', '00000000-0000-0000-0000-000000000102', 'create',          'member',       '00000000-0000-0000-0000-000000000301', '{"source":"seed","member_code":"GF-DEMO01"}', now()-interval '20 days'),
  ('00000000-0000-0000-0000-000000000902', '00000000-0000-0000-0000-000000000102', 'sell_membership', 'subscription', '00000000-0000-0000-0000-000000000501', '{"source":"seed","sale_type":"new"}', now()-interval '10 days'),
  ('00000000-0000-0000-0000-000000000903', '00000000-0000-0000-0000-000000000101', 'sell_membership', 'subscription', '00000000-0000-0000-0000-000000000502', '{"source":"seed","sale_type":"renewal"}', now()-interval '1 day'),
  ('00000000-0000-0000-0000-000000000904', '00000000-0000-0000-0000-000000000101', 'freeze',          'subscription', '00000000-0000-0000-0000-000000000504', '{"source":"seed","reason":"Đi công tác 1 tuần"}', now()-interval '2 days'),
  ('00000000-0000-0000-0000-000000000905', '00000000-0000-0000-0000-000000000101', 'cancel_payment',  'payment',      '00000000-0000-0000-0000-000000000606', '{"source":"seed","reason":"Khách yêu cầu hủy"}', now()-interval '90 days')
on conflict (id) do update set details=excluded.details, created_at=excluded.created_at;

commit;

-- Kết quả kiểm tra sau khi seed.
select 'profiles' as table_name, count(*) as demo_rows from public.profiles where id::text like '00000000-0000-0000-0000-000000000%'
union all select 'plans', count(*) from public.membership_plans where id::text like '00000000-0000-0000-0000-0000000004%'
union all select 'members', count(*) from public.members where id::text like '00000000-0000-0000-0000-0000000003%'
union all select 'subscriptions', count(*) from public.subscriptions where id::text like '00000000-0000-0000-0000-0000000005%'
union all select 'payments', count(*) from public.payments where id::text like '00000000-0000-0000-0000-0000000006%'
union all select 'check_ins', count(*) from public.check_ins where id::text like '00000000-0000-0000-0000-0000000007%'
union all select 'freezes', count(*) from public.subscription_freezes where id::text like '00000000-0000-0000-0000-0000000008%'
union all select 'follow_ups', count(*) from public.member_follow_ups where id::text like '00000000-0000-0000-0000-0000000015%'
union all select 'expenses', count(*) from public.expenses where id::text like '00000000-0000-0000-0000-0000000014%'
union all select 'audit_logs', count(*) from public.audit_logs where id::text like '00000000-0000-0000-0000-0000000009%';
