# GymFlow

MVP quản lý một chi nhánh gym: tổng quan, hội viên, gói tập, thanh toán, check-in và báo cáo CSV.

## Chạy local

```bash
npm install
npm run db:generate
npm run dev
```

Ứng dụng triển khai bằng OpenAI Sites với D1. Schema trong `db/schema.ts` có thể chuyển sang PostgreSQL/Supabase bằng cách đổi adapter Drizzle. Danh tính đăng nhập do Sites cung cấp; vai trò nghiệp vụ lưu trong `profiles` và phải được kiểm tra tại mọi thao tác phía máy chủ.

## Quy tắc dữ liệu

- Không xóa cứng thanh toán hoặc đăng ký gói; chuyển sang `cancelled`.
- Check-in kiểm tra hội viên, ngày hết hạn, số lượt và khoảng chống trùng 10 phút.
- Tạo check-in và trừ lượt phải chạy trong cùng một batch/transaction D1.
- Doanh thu chỉ tổng hợp thanh toán có trạng thái `valid`.
