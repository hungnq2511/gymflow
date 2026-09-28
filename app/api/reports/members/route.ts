import ExcelJS from 'exceljs';
import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { todayVietnam, unwrap } from '@/lib/http';

export async function GET() {
  try {
    await requireActor(['manager', 'staff']);
    const members = unwrap(
      await createAdminClient()
        .from('members')
        .select(
          'member_code,full_name,phone,email,status,subscriptions(id,end_date,remaining_visits,status,plan_name_snapshot,membership_plans(name))',
        )
        .order('created_at', { ascending: false }),
    );
    const today = todayVietnam();
    const warningDate = new Date(`${today}T00:00:00+07:00`);
    warningDate.setDate(warningDate.getDate() + 7);
    const warningDay = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Ho_Chi_Minh',
    }).format(warningDate);

    const workbook = new ExcelJS.Workbook();
    workbook.creator = 'GymFlow';
    workbook.created = new Date();
    const sheet = workbook.addWorksheet('Hội viên', {
      views: [{ state: 'frozen', ySplit: 1 }],
      properties: { defaultRowHeight: 20 },
    });
    sheet.columns = [
      { header: 'Mã hội viên', key: 'code', width: 17 },
      { header: 'Họ và tên', key: 'name', width: 28 },
      { header: 'Điện thoại', key: 'phone', width: 17 },
      { header: 'Email', key: 'email', width: 30 },
      { header: 'Gói hiện tại', key: 'plan', width: 25 },
      { header: 'Ngày hết hạn', key: 'expiry', width: 17 },
      { header: 'Lượt còn lại', key: 'remaining', width: 17 },
      { header: 'Trạng thái', key: 'status', width: 18 },
    ];

    for (const member of members) {
      const subscription = member.subscriptions?.find((item) =>
        ['active', 'frozen'].includes(item.status),
      );
      const planRelation = subscription?.membership_plans as
        | { name?: string }
        | Array<{ name?: string }>
        | null
        | undefined;
      const planName = Array.isArray(planRelation)
        ? planRelation[0]?.name
        : planRelation?.name;
      const expiry = subscription?.end_date ?? null;
      const status =
        member.status !== 'active' || !expiry || expiry < today
          ? 'Hết hạn'
          : expiry <= warningDay
            ? 'Sắp hết hạn'
            : 'Đang tập';
      sheet.addRow({
        code: member.member_code,
        name: member.full_name,
        phone: member.phone,
        email: member.email ?? '',
        plan: subscription?.plan_name_snapshot ?? planName ?? 'Chưa có gói',
        expiry: expiry ? new Date(`${expiry}T00:00:00+07:00`) : '',
        remaining:
          subscription?.remaining_visits == null
            ? subscription
              ? 'Không giới hạn'
              : '—'
            : subscription.remaining_visits,
        status,
      });
    }

    const header = sheet.getRow(1);
    header.height = 28;
    header.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    header.fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF1F2937' },
    };
    header.alignment = { vertical: 'middle', horizontal: 'center' };
    header.border = {
      bottom: { style: 'medium', color: { argb: 'FF84CC16' } },
    };
    sheet.autoFilter = { from: 'A1', to: 'H1' };
    sheet.getColumn('code').numFmt = '@';
    sheet.getColumn('phone').numFmt = '@';
    sheet.getColumn('expiry').numFmt = 'dd/mm/yyyy';
    sheet.getColumn('remaining').alignment = { horizontal: 'center' };
    sheet.getColumn('status').alignment = { horizontal: 'center' };

    for (let rowNumber = 2; rowNumber <= sheet.rowCount; rowNumber += 1) {
      const row = sheet.getRow(rowNumber);
      row.alignment = { vertical: 'middle' };
      row.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: rowNumber % 2 === 0 ? 'FFF8FAFC' : 'FFFFFFFF' },
      };
      row.eachCell({ includeEmpty: true }, (cell) => {
        cell.border = {
          bottom: { style: 'hair', color: { argb: 'FFD1D5DB' } },
        };
      });
      const statusCell = row.getCell('status');
      statusCell.font = {
        bold: true,
        color: {
          argb:
            statusCell.value === 'Đang tập'
              ? 'FF15803D'
              : statusCell.value === 'Sắp hết hạn'
                ? 'FFB45309'
                : 'FFB91C1C',
        },
      };
    }

    const buffer = await workbook.xlsx.writeBuffer();
    return new Response(new Uint8Array(buffer), {
      headers: {
        'Content-Type':
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'Content-Disposition': 'attachment; filename="bao-cao-hoi-vien.xlsx"',
        'Cache-Control': 'no-store',
      },
    });
  } catch (error) {
    return apiError(error);
  }
}
