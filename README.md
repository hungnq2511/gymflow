# GymFlow MVP

Web quản lý một chi nhánh phòng gym bằng **Next.js 16 + TypeScript + Supabase**. Dự án hiện được cấu hình để phát triển và kiểm thử local, chưa có cấu hình triển khai Vercel.

## Các module nghiệp vụ

1. Đăng nhập, quên/đổi mật khẩu và phân quyền `manager`, `staff`, `member`.
2. Quản lý hội viên, trạng thái, lời mời tài khoản và xuất CSV.
3. Quản lý gói, bán mới, gia hạn nối tiếp và đóng băng.
4. Thanh toán đủ bằng tiền mặt/chuyển khoản, phiếu thu và hủy giao dịch.
5. Check-in bằng QR hoặc mã hội viên, chặn quét trùng và trừ lượt nguyên tử.
6. Dashboard doanh thu, hội viên, check-in và báo cáo.
7. Cổng hội viên: QR, gói hiện tại/kế tiếp, lịch sử và thông tin liên hệ.
8. Chăm sóc hội viên: cảnh báo hết hạn/hết lượt, phân công và lịch sử liên hệ.
9. Tài chính: ghi nhận chi phí, doanh thu, lợi nhuận và phân tích theo danh mục.

## 1. Cấu hình Supabase

Tạo file `.env` (hoặc `.env.local`) theo `.env.example`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=your-publishable-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

`SUPABASE_SERVICE_ROLE_KEY` chỉ được dùng bởi Route Handler phía server. Không thêm tiền tố `NEXT_PUBLIC_` cho khóa này và không commit file env.

Trong Supabase SQL Editor, chạy lần lượt các file ở `supabase/migrations` theo thứ tự tên. Với database mới, chạy toàn bộ migration. Với database hiện có, chạy thêm các migration chưa được áp dụng, bao gồm `202609170001_staff_credentials.sql` để hỗ trợ tài khoản đăng nhập nội bộ cho nhân viên.

Trong **Authentication → URL Configuration**, đặt local Site URL là `http://localhost:3000` và thêm redirect URL:

```text
http://localhost:3000/**
```

Trong **Authentication → Email Templates → Reset password**, đặt liên kết trong nút “Đặt lại mật khẩu” thành:

```html
<a
  href="{{ .SiteURL }}/auth/confirm?token_hash={{ .TokenHash }}&type=recovery&next=/update-password"
  >Đặt lại mật khẩu</a
>
```

Với email mời tài khoản, trong **Email Templates → Invite user**, đặt tiêu đề
`Lời mời tạo tài khoản GymFlow` và dùng nội dung tiếng Việt tại
`supabase/templates/invite.html`. Supabase local tự đọc template này từ
`supabase/config.toml`. Nút kích hoạt trong template dùng liên kết:

```html
<a
  href="{{ .SiteURL }}/auth/confirm?token_hash={{ .TokenHash }}&type=invite&next=/update-password"
  >Kích hoạt tài khoản</a
>
```

Route `/auth/confirm` xác minh `token_hash` và tạo recovery session trước khi mở màn hình đặt mật khẩu. Cấu hình này cũng hoạt động khi người dùng mở email bằng trình duyệt khác. Chỉ dùng email khôi phục mới nhất vì Supabase có thể vô hiệu hóa liên kết cũ sau khi gửi lại.

Trong MVP, tắt public sign-up vì tài khoản hội viên/nhân viên được tạo bằng lời mời. Auth user đầu tiên trên database trống được trigger gán quyền `manager`; các tài khoản sau nhận quyền từ hồ sơ lời mời.

## 2. Chạy local

```bash
npm install
npm run dev
```

Mở `http://localhost:3000`. Các lệnh kiểm tra:

```bash
npm test
npm run lint
npm run build
```

## Dữ liệu mẫu

Sau khi đã chạy đủ migration, mở Supabase SQL Editor và chạy toàn bộ file `supabase/seed.sql`. File có UUID cố định, có thể chạy lại và không xóa dữ liệu thật.

Dữ liệu mẫu gồm một tài khoản quản trị, 20 hội viên, 5 loại gói, 20 đăng ký, 20 thanh toán và 10 khoản chi phí. File seed tự tạo Supabase Auth User và liên kết với profile quản trị, nên có thể đăng nhập ngay bằng:

```text
Email: admin1@gmail.com
Mật khẩu: Admin@123
```

Đây là thông tin đăng nhập dành cho môi trường demo; hãy thay đổi hoặc xóa tài khoản này trước khi dùng dữ liệu thật.

## Bảo mật và dữ liệu

- Mọi API đều xác thực session Supabase và kiểm tra vai trò ở server.
- Nhân viên được tạo bằng tên đăng nhập, dùng mật khẩu tạm `admin123` và bắt buộc đổi mật khẩu trong lần đăng nhập đầu tiên.
- Vai trò `staff` không được truy cập Báo cáo và quản lý Nhân viên.
- Service role không được gửi xuống trình duyệt.
- Bán gói/thanh toán, check-in/trừ lượt, đóng băng và hủy thanh toán nằm trong PostgreSQL function để giữ tính nguyên tử.
- Giao dịch, check-in và audit log không bị xóa cứng.
- QR chỉ chứa token UUID ngẫu nhiên, không chứa thông tin cá nhân.
