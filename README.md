# GymFlow

Ứng dụng quản lý một chi nhánh gym, dùng Supabase PostgreSQL và API server-side.

## Thiết lập Supabase

1. Tạo project tại Supabase.
2. Mở **SQL Editor**, dán và chạy toàn bộ file `supabase/migrations/202609090001_initial_schema.sql`.
3. Sao chép `.env.example` thành `.env.local`, rồi điền ba biến:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
```

4. Chạy `npm run dev`, đăng nhập vào Site. Người đầu tiên truy cập database trống được tạo thành `manager`.

## Bảo mật

- Không commit `.env.local`.
- Không dùng `SUPABASE_SERVICE_ROLE_KEY` trong Client Component hoặc biến `NEXT_PUBLIC_*`.
- RLS chặn truy cập trực tiếp bằng anon key; mọi thao tác dữ liệu đi qua API server và kiểm tra vai trò.
- Khi triển khai Sites, thêm ba biến qua phần Environment Variables của Site.
