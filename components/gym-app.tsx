'use client';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  Activity,
  CalendarClock,
  Camera,
  CheckCircle2,
  CircleDollarSign,
  Download,
  Dumbbell,
  LayoutDashboard,
  Menu,
  Package,
  Pencil,
  QrCode,
  ReceiptText,
  HandHeart,
  Search,
  ShieldCheck,
  LogOut,
  UserRoundPlus,
  Users,
  WalletCards,
  XCircle,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { AppToast } from '@/components/app-toast';
import { errorMessage, responseError } from '@/lib/error-messages';
import { apiFetch } from '@/lib/api-fetch';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/ui/spinner';
import {
  ExpensesModule,
  FollowUpsModule,
} from '@/components/operations-modules';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
type Page =
  | 'Tổng quan'
  | 'Hội viên'
  | 'Gói tập'
  | 'Check-in'
  | 'Thanh toán'
  | 'Chăm sóc'
  | 'Chi phí'
  | 'Báo cáo'
  | 'Nhân viên';
type Member = {
  databaseId: string;
  id: string;
  name: string;
  phone: string;
  plan: string;
  expiry: string;
  status: 'Đang tập' | 'Sắp hết hạn' | 'Hết hạn';
  remaining: string;
  email: string;
  dateOfBirth: string;
  gender: string;
  address: string;
  emergencyContact: string;
  notes: string;
  active: boolean;
  subscriptionId?: string;
  subscriptionStatus?: string;
  createdAt: string;
  sales: Array<{ saleType: 'new' | 'renewal'; createdAt: string }>;
};
type Plan = {
  id: string;
  name: string;
  price: number;
  durationDays: number;
  visitLimit: number | null;
  members: number;
  color: string;
  isActive: boolean;
};
type Payment = {
  id: string;
  member: string;
  description: string;
  amount: number;
  method: string;
  paidAt: string;
  receiptCode: string;
  status: 'valid' | 'cancelled';
};
type CheckIn = {
  id: string;
  member: string;
  code: string;
  checkedInAt: string;
};
const initialMembers: Member[] = [];
const money = (n: number) =>
  new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(n);
const WEEKDAYS = [
  'Chủ nhật',
  'Thứ 2',
  'Thứ 3',
  'Thứ 4',
  'Thứ 5',
  'Thứ 6',
  'Thứ 7',
];
const formatHeaderDate = (date: Date) =>
  `${WEEKDAYS[date.getUTCDay()]}, ${String(date.getUTCDate()).padStart(2, '0')}/${String(date.getUTCMonth() + 1).padStart(2, '0')}`;
const formatShortWeekday = (date: Date) =>
  date.getUTCDay() === 0 ? 'CN' : `T${date.getUTCDay() + 1}`;
const vietnamDay = (value: string | Date) =>
  new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Ho_Chi_Minh' }).format(
    new Date(value),
  );

export default function GymApp({
  renderedAt,
  userName,
}: {
  renderedAt: string;
  userName: string;
}) {
  const [page, setPage] = useState<Page>('Tổng quan'),
    [members, setMembers] = useState(initialMembers),
    [search, setSearch] = useState(''),
    [status, setStatus] = useState('Tất cả'),
    [open, setOpen] = useState(false),
    [mobile, setMobile] = useState(false),
    [toast, setToast] = useState(''),
    [database, setDatabase] = useState<'loading' | 'unavailable' | 'connected'>(
      'loading',
    ),
    [livePlans, setLivePlans] = useState<Plan[]>([]),
    [payments, setPayments] = useState<Payment[]>([]),
    [checkIns, setCheckIns] = useState<CheckIn[]>([]),
    [qr, setQr] = useState(''),
    [result, setResult] = useState<'ok' | 'error' | null>(null),
    [checkinReason, setCheckinReason] = useState('');
  const [actorRole, setActorRole] = useState<'manager' | 'staff'>('staff');
  const filtered = useMemo(
    () =>
      members.filter(
        (m) =>
          `${m.name} ${m.id} ${m.phone}`
            .toLowerCase()
            .includes(search.toLowerCase()) &&
          (status === 'Tất cả' || m.status === status),
      ),
    [members, search, status],
  );
  const loadData = useCallback(async () => {
    try {
      const response = await apiFetch('/api/bootstrap');
      if (!response.ok) throw new Error('BOOTSTRAP_FAILED');
      const data = (await response.json()) as {
        actor: { role: 'manager' | 'staff' };
        members: Array<{
          id: string;
          member_code: string;
          full_name: string;
          phone: string;
          email: string | null;
          date_of_birth: string | null;
          gender: string | null;
          address: string | null;
          emergency_contact: string | null;
          notes: string | null;
          status: string;
          created_at: string;
          subscriptions?: Array<{
            end_date: string;
            remaining_visits: number | null;
            status: string;
            id: string;
            sale_type: 'new' | 'renewal';
            created_at: string;
            membership_plans?: { name: string } | null;
          }>;
        }>;
        plans: Array<{
          id: string;
          name: string;
          price: number | string;
          duration_days: number;
          visit_limit: number | null;
          is_active: boolean;
          subscriptions?: Array<{ count: number }>;
        }>;
        payments: Array<{
          id: string;
          receipt_code: string;
          status: 'valid' | 'cancelled';
          amount: number | string;
          method: string;
          paid_at: string;
          members?: { full_name: string } | null;
          subscriptions?: {
            plan_name_snapshot?: string | null;
            membership_plans?: { name: string } | null;
          } | null;
        }>;
        checkIns: Array<{
          id: string;
          checked_in_at: string;
          members?: { full_name: string; member_code: string } | null;
        }>;
      };
      setActorRole(data.actor.role);
      const today = new Date();
      const warningDate = new Date(today);
      warningDate.setDate(warningDate.getDate() + 7);
      setMembers(
        data.members.map((member) => {
          const subscription = member.subscriptions?.find(
            (item) => item.status === 'active' || item.status === 'frozen',
          );
          const expiry = subscription?.end_date;
          const memberStatus =
            member.status !== 'active' ||
            !expiry ||
            expiry < today.toISOString().slice(0, 10)
              ? 'Hết hạn'
              : expiry <= warningDate.toISOString().slice(0, 10)
                ? 'Sắp hết hạn'
                : 'Đang tập';
          return {
            databaseId: member.id,
            id: member.member_code,
            name: member.full_name,
            phone: member.phone,
            email: member.email ?? '',
            dateOfBirth: member.date_of_birth ?? '',
            gender: member.gender ?? '',
            address: member.address ?? '',
            emergencyContact: member.emergency_contact ?? '',
            notes: member.notes ?? '',
            active: member.status === 'active',
            subscriptionId: subscription?.id,
            subscriptionStatus: subscription?.status,
            createdAt: member.created_at,
            sales: (member.subscriptions ?? []).map((item) => ({
              saleType: item.sale_type,
              createdAt: item.created_at,
            })),
            plan: subscription?.membership_plans?.name ?? 'Chưa có gói',
            expiry: expiry ?? '—',
            status: memberStatus,
            remaining:
              subscription?.remaining_visits == null
                ? 'Không giới hạn'
                : `${subscription.remaining_visits} lượt`,
          };
        }),
      );
      const colors = [
        'bg-sky-500',
        'bg-violet-500',
        'bg-emerald-500',
        'bg-orange-500',
        'bg-pink-500',
      ];
      setLivePlans(
        data.plans.map((plan, index) => ({
          id: plan.id,
          name: plan.name,
          price: Number(plan.price),
          durationDays: plan.duration_days,
          visitLimit: plan.visit_limit,
          members: plan.subscriptions?.[0]?.count ?? 0,
          color: colors[index % colors.length],
          isActive: plan.is_active,
        })),
      );
      setPayments(
        data.payments.map((payment) => ({
          id: payment.id,
          receiptCode:
            payment.receipt_code ?? payment.id.slice(0, 8).toUpperCase(),
          status: payment.status,
          member: payment.members?.full_name ?? '—',
          description:
            payment.subscriptions?.plan_name_snapshot ??
            payment.subscriptions?.membership_plans?.name ??
            'Gói tập',
          amount: Number(payment.amount),
          method: payment.method === 'cash' ? 'Tiền mặt' : 'Chuyển khoản',
          paidAt: payment.paid_at,
        })),
      );
      setCheckIns(
        data.checkIns.map((item) => ({
          id: item.id,
          member: item.members?.full_name ?? '—',
          code: item.members?.member_code ?? '—',
          checkedInAt: item.checked_in_at,
        })),
      );
      setDatabase('connected');
    } catch {
      setDatabase('unavailable');
    }
  }, []);
  // The initial request intentionally hydrates client state from the server API.
  useEffect(() => {
    // oxlint-disable-next-line react/react-compiler -- hydrate API-backed state on mount
    void loadData();
  }, [loadData]);
  const notice = (s: string) => {
      setToast(s);
      setTimeout(() => setToast(''), 2500);
    },
    add = async (d: FormData) => {
      const rawName = d.get('name'),
        rawPhone = d.get('phone'),
        rawEmail = d.get('email'),
        name = typeof rawName === 'string' ? rawName.trim() : '',
        phone = typeof rawPhone === 'string' ? rawPhone.trim() : '',
        email = typeof rawEmail === 'string' ? rawEmail.trim() : '';
      if (!name || !phone) return;
      const response = await apiFetch('/api/members', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fullName: name, phone, email }),
      });
      if (!response.ok) {
        notice(await responseError(response, 'Không thể lưu hội viên.'));
        return;
      }
      setOpen(false);
      await loadData();
      notice('Đã thêm hội viên mới');
    },
    checkin = async (scannedToken?: string) => {
      const token = scannedToken?.trim() || qr.trim();
      if (!token) return;
      const response = await apiFetch('/api/check-ins', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      });
      const payload = (await response.json()) as {
        ok?: boolean;
        member_name?: string;
        reason?: string;
      };
      setCheckinReason(payload.reason ?? '');
      setResult(response.ok && payload.ok ? 'ok' : 'error');
      if (response.ok && payload.ok) {
        notice(`Check-in thành công: ${payload.member_name ?? ''}`);
        setQr('');
        await loadData();
      } else {
        notice(errorMessage(payload.reason, 'Không thể thực hiện check-in.'));
      }
    },
    csv = async () => {
      const response = await apiFetch('/api/reports/members');
      if (!response.ok) {
        notice(await responseError(response, 'Không thể xuất báo cáo.'));
        return;
      }
      const b = await response.blob();
      const a = document.createElement('a');
      const url = URL.createObjectURL(b);
      a.href = url;
      a.download = 'bao-cao-hoi-vien.xlsx';
      a.click();
      URL.revokeObjectURL(url);
      notice('Đã xuất báo cáo Excel');
    };
  const nav: [[Page, typeof LayoutDashboard]][number][] = [
    ['Tổng quan', LayoutDashboard],
    ['Hội viên', Users],
    ['Gói tập', Package],
    ['Check-in', QrCode],
    ['Thanh toán', ReceiptText],
    ['Chăm sóc', HandHeart],
    ...(actorRole === 'manager'
      ? ([
          ['Chi phí', WalletCards],
          ['Báo cáo', Activity],
          ['Nhân viên', ShieldCheck],
        ] as [[Page, typeof LayoutDashboard]][number][])
      : []),
  ];
  return (
    <main className="app-shell surface-grid min-h-screen bg-background">
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 border-r border-white/8 bg-sidebar/95 px-4 py-6 shadow-2xl backdrop-blur-2xl transition-transform lg:translate-x-0 ${mobile ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="mb-9 flex items-center gap-3 px-3">
          <span className="grid size-11 place-items-center rounded-full bg-primary text-primary-foreground shadow-[0_0_30px_oklch(0.86_0.2_125/20%)]">
            <Dumbbell size={22} />
          </span>
          <div>
            <p className="font-heading text-lg font-black tracking-tight text-white">
              GymFlow
            </p>
            <p className="text-xs text-white/45">
              Nhóm 7 ·{' '}
              {database === 'connected'
                ? 'Đã kết nối'
                : database === 'loading'
                  ? 'Đang tải'
                  : 'Mất kết nối'}
            </p>
          </div>
        </div>
        <nav className="space-y-1">
          {nav.map(([n, I], index) => (
            <button
              id={`admin-nav-${index}`}
              type="button"
              key={n}
              onClick={() => {
                setPage(n);
                setMobile(false);
              }}
              className={`group flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-all ${page === n ? 'bg-white text-slate-950 shadow-lg' : 'text-white/55 hover:bg-white/6 hover:text-white'}`}
            >
              <I
                size={18}
                className={
                  page === n
                    ? 'text-slate-950'
                    : 'transition-colors group-hover:text-primary'
                }
              />
              {n}
            </button>
          ))}
        </nav>
        <button
          id="admin-logout-button"
          type="button"
          onClick={async () => {
            const { createClient } = await import('@/lib/supabase/client');
            await createClient().auth.signOut();
            location.href = '/login';
          }}
          className="absolute inset-x-4 bottom-5 flex items-center gap-3 rounded-2xl border border-white/8 bg-white/4 p-4 text-left transition hover:border-white/15 hover:bg-white/7"
        >
          <Avatar name={userName} />
          <span>
            <b className="block max-w-32 truncate text-sm text-white">
              {userName}
            </b>
            <small className="text-white/45">
              {actorRole === 'manager' ? 'Quản lý' : 'Nhân viên'}
            </small>
          </span>
          <LogOut className="ml-auto size-4 text-white/40" />
        </button>
      </aside>
      {mobile && (
        <button
          id="admin-mobile-menu-backdrop"
          type="button"
          aria-label="Đóng menu"
          className="fixed inset-0 z-30 bg-slate-950/40 lg:hidden"
          onClick={() => setMobile(false)}
        />
      )}
      <section className="lg:ml-64">
        <header className="sticky top-0 z-20 flex h-20 items-center justify-between border-b border-white/8 bg-background/75 px-4 backdrop-blur-2xl md:px-8">
          <div className="flex items-center gap-3">
            <Button
              id="admin-mobile-menu-open-button"
              type="button"
              className="lg:hidden"
              variant="outline"
              size="icon"
              onClick={() => setMobile(true)}
            >
              <Menu />
            </Button>
            <div>
              <p className="hidden text-sm text-muted-foreground sm:block">
                {formatHeaderDate(new Date(renderedAt))}
              </p>
              <h1 className="text-lg font-semibold tracking-tight">{page}</h1>
            </div>
          </div>
          {page === 'Hội viên' && (
            <AddDialog open={open} setOpen={setOpen} add={add} />
          )}
        </header>
        <div className="mx-auto max-w-[1440px] p-4 md:p-8 lg:p-10">
          {page === 'Tổng quan' && (
            <Dashboard
              members={members}
              payments={payments}
              checkIns={checkIns}
              renderedAt={renderedAt}
            />
          )}
          {page === 'Hội viên' && (
            <Members
              list={filtered}
              search={search}
              setSearch={setSearch}
              status={status}
              setStatus={setStatus}
              csv={csv}
              reload={loadData}
              notice={notice}
              manager={actorRole === 'manager'}
            />
          )}{' '}
          {page === 'Gói tập' && (
            <Plans
              list={livePlans}
              onCreated={loadData}
              notice={notice}
              manager={actorRole === 'manager'}
            />
          )}
          {page === 'Check-in' && (
            <Checkin
              qr={qr}
              setQr={setQr}
              result={result}
              reason={checkinReason}
              submit={checkin}
            />
          )}{' '}
          {page === 'Thanh toán' && (
            <Payments
              list={payments}
              members={members}
              plans={livePlans.filter((plan) => plan.isActive)}
              onCreated={loadData}
              notice={notice}
            />
          )}{' '}
          {page === 'Chăm sóc' && (
            <FollowUpsModule
              notice={notice}
              manager={actorRole === 'manager'}
            />
          )}
          {page === 'Chi phí' && actorRole === 'manager' && (
            <ExpensesModule notice={notice} />
          )}
          {page === 'Báo cáo' && actorRole === 'manager' && (
            <Reports
              csv={csv}
              members={members}
              payments={payments}
              renderedAt={renderedAt}
            />
          )}
          {page === 'Nhân viên' && actorRole === 'manager' && (
            <Staff notice={notice} />
          )}
        </div>
      </section>
      <AppToast message={toast} />
    </main>
  );
}
function AddDialog({
  open,
  setOpen,
  add,
}: {
  open: boolean;
  setOpen: (x: boolean) => void;
  add: (d: FormData) => void | Promise<void>;
}) {
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger
        render={<Button id="member-create-open-button" type="button" />}
      >
        <UserRoundPlus /> Thêm hội viên
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Thêm hội viên mới</DialogTitle>
          <DialogDescription>
            Nhập thông tin cơ bản. Có thể đăng ký gói sau.
          </DialogDescription>
        </DialogHeader>
        <form action={add} className="space-y-4">
          <div>
            <Label htmlFor="name">Họ và tên</Label>
            <Input
              id="name"
              name="name"
              className="mt-2"
              minLength={2}
              maxLength={150}
              pattern="[^<>]*"
              title="Họ tên không được chứa thẻ HTML"
              required
            />
          </div>
          <div>
            <Label htmlFor="phone">Số điện thoại</Label>
            <Input
              id="phone"
              name="phone"
              type="tel"
              inputMode="numeric"
              autoComplete="tel"
              className="mt-2"
              pattern="0[0-9]{9}"
              minLength={10}
              maxLength={10}
              title="Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0"
              required
            />
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input id="email" name="email" type="email" className="mt-2" />
          </div>
          <div className="flex justify-end gap-2">
            <Button
              id="member-create-cancel-button"
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
            >
              Hủy
            </Button>
            <Button id="member-create-submit-button" type="submit">
              Lưu hội viên
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
function Head({
  top,
  title,
  action,
}: {
  top: string;
  title: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-8 flex items-end justify-between gap-3">
      <div>
        <p className="eyebrow">{top}</p>
        <h2 className="text-2xl font-semibold tracking-[-0.035em] md:text-4xl">
          {title}
        </h2>
      </div>
      {action}
    </div>
  );
}
function Avatar({ name }: { name: string }) {
  return (
    <span className="grid size-10 shrink-0 place-items-center rounded-full border border-primary/15 bg-primary/10 font-bold text-primary">
      {name.split(' ').at(-1)?.[0]}
    </span>
  );
}
function Dashboard({
  members,
  payments,
  checkIns,
  renderedAt,
}: {
  members: Member[];
  payments: Payment[];
  checkIns: CheckIn[];
  renderedAt: string;
}) {
  const active = members.filter((member) => member.status !== 'Hết hạn').length;
  const expiring = members.filter(
    (member) => member.status === 'Sắp hết hạn',
  ).length;
  const revenue = payments
    .filter((payment) => payment.status === 'valid')
    .reduce((sum, payment) => sum + payment.amount, 0);
  const today = vietnamDay(renderedAt),
    month = today.slice(0, 7);
  const todayCheckIns = checkIns.filter(
    (x) => vietnamDay(x.checkedInAt) === today,
  );
  const todayRevenue = payments
    .filter((p) => p.status === 'valid' && vietnamDay(p.paidAt) === today)
    .reduce((sum, p) => sum + p.amount, 0);
  const newMembers = members.filter(
    (m) => vietnamDay(m.createdAt).slice(0, 7) === month,
  ).length;
  const sales = members
    .flatMap((m) => m.sales)
    .filter((s) => vietnamDay(s.createdAt).slice(0, 7) === month);
  return (
    <>
      <Head
        top="TÌNH HÌNH HÔM NAY"
        title="Sẵn sàng cho một ngày bứt phá"
        action={
          <Badge
            className="border-primary/20 bg-primary/10 text-primary"
            variant="outline"
          >
            ● Dữ liệu trực tiếp
          </Badge>
        }
      />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          [
            'Hội viên hoạt động',
            String(active),
            `${members.length} hội viên`,
            Users,
          ],
          [
            'Check-in hôm nay',
            String(todayCheckIns.length),
            'Lượt vào phòng tập',
            Activity,
          ],
          [
            'Doanh thu tháng',
            money(revenue),
            `${payments.length} giao dịch`,
            CircleDollarSign,
          ],
          ['Sắp hết hạn', String(expiring), 'Trong 7 ngày tới', CalendarClock],
          [
            'Hội viên mới',
            String(newMembers),
            'Trong tháng này',
            UserRoundPlus,
          ],
          [
            'Doanh thu hôm nay',
            money(todayRevenue),
            'Giao dịch hợp lệ',
            CircleDollarSign,
          ],
          [
            'Gói bán mới',
            String(sales.filter((s) => s.saleType === 'new').length),
            'Trong tháng này',
            Package,
          ],
          [
            'Lượt gia hạn',
            String(sales.filter((s) => s.saleType === 'renewal').length),
            'Trong tháng này',
            CalendarClock,
          ],
        ].map(([l, v, n, I]) => (
          <article
            key={l as string}
            className="metric-card before:absolute before:inset-x-0 before:top-0 before:h-px before:bg-gradient-to-r before:from-transparent before:via-primary/35 before:to-transparent"
          >
            <div className="mb-6 flex justify-between">
              <p className="text-sm text-muted-foreground">{l as string}</p>
              <span className="icon-chip">
                <I size={18} />
              </span>
            </div>
            <p className="text-3xl font-semibold tracking-[-0.04em]">
              {v as string}
            </p>
            <p className="mt-2 text-xs text-muted-foreground">{n as string}</p>
          </article>
        ))}
      </div>
      <div className="mt-6 grid gap-6 xl:grid-cols-[1.55fr_1fr]">
        <Revenue payments={payments} renderedAt={renderedAt} />
        <article className="panel">
          <h3 className="panel-title mb-4">Check-in gần đây</h3>
          <div className="divide-y">
            {checkIns.slice(0, 6).map((item) => (
              <div key={item.id} className="flex items-center gap-3 py-3">
                <Avatar name={item.member} />
                <div className="min-w-0 flex-1">
                  <b className="block truncate text-sm">{item.member}</b>
                  <small className="text-muted-foreground">{item.code}</small>
                </div>
                <time className="text-sm">
                  {new Intl.DateTimeFormat('vi-VN', {
                    hour: '2-digit',
                    minute: '2-digit',
                  }).format(new Date(item.checkedInAt))}
                </time>
              </div>
            ))}
            {!checkIns.length && (
              <p className="py-12 text-center text-sm text-muted-foreground">
                Chưa có lượt check-in.
              </p>
            )}
          </div>
        </article>
      </div>
      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <DailyCheckIns checkIns={checkIns} renderedAt={renderedAt} />
        <TopPlans payments={payments} />
      </div>
    </>
  );
}
function DailyCheckIns({
  checkIns,
  renderedAt,
}: {
  checkIns: CheckIn[];
  renderedAt: string;
}) {
  const days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(renderedAt);
    d.setUTCDate(d.getUTCDate() - (6 - i));
    const key = vietnamDay(d);
    return {
      key,
      label: formatShortWeekday(d),
      count: checkIns.filter((x) => vietnamDay(x.checkedInAt) === key).length,
    };
  });
  const max = Math.max(...days.map((x) => x.count), 1);
  return (
    <article className="panel">
      <h3 className="panel-title">Lượt check-in 7 ngày</h3>
      <div className="mt-6 flex h-44 items-end gap-3 border-b border-l border-white/8 px-3">
        {days.map((x) => (
          <div
            key={x.key}
            className="flex h-full flex-1 items-end"
            title={`${x.count} lượt`}
          >
            <div
              className="w-full rounded-t-md bg-gradient-to-t from-primary/35 to-primary shadow-[0_0_20px_oklch(0.86_0.2_125/12%)]"
              style={{
                height: `${x.count ? Math.max((x.count / max) * 100, 5) : 0}%`,
              }}
            />
          </div>
        ))}
      </div>
      <div className="mt-3 grid grid-cols-7 text-center text-xs text-muted-foreground">
        {days.map((x) => (
          <span key={x.key}>{x.label}</span>
        ))}
      </div>
    </article>
  );
}
function TopPlans({ payments }: { payments: Payment[] }) {
  const rows = Object.entries(
    payments
      .filter((x) => x.status === 'valid')
      .reduce<Record<string, number>>(
        (a, x) => ({ ...a, [x.description]: (a[x.description] ?? 0) + 1 }),
        {},
      ),
  )
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
  return (
    <article className="panel">
      <h3 className="panel-title">Gói được mua nhiều nhất</h3>
      <div className="mt-5 space-y-3">
        {rows.map(([name, count], i) => (
          <div
            key={name}
            className="flex items-center gap-3 rounded-xl bg-muted p-3"
          >
            <b className="grid size-8 place-items-center rounded-lg bg-primary/15 text-primary">
              {i + 1}
            </b>
            <span className="flex-1 font-medium">{name}</span>
            <Badge variant="outline">{count} lượt</Badge>
          </div>
        ))}
        {!rows.length && (
          <p className="py-8 text-center text-muted-foreground">
            Chưa có dữ liệu bán gói.
          </p>
        )}
      </div>
    </article>
  );
}
function Revenue({
  payments,
  renderedAt,
}: {
  payments: Payment[];
  renderedAt: string;
}) {
  const days = Array.from({ length: 7 }, (_, offset) => {
    const date = new Date(renderedAt);
    date.setUTCHours(0, 0, 0, 0);
    date.setUTCDate(date.getUTCDate() - (6 - offset));
    const dayKey = vietnamDay(date);
    const total = payments
      .filter(
        (payment) =>
          payment.status === 'valid' && vietnamDay(payment.paidAt) === dayKey,
      )
      .reduce((sum, payment) => sum + payment.amount, 0);
    return {
      label: formatShortWeekday(date),
      total,
    };
  });
  const max = Math.max(...days.map((day) => day.total), 1);
  const total = days.reduce((sum, day) => sum + day.total, 0);
  return (
    <article className="panel min-h-[340px]">
      <div className="mb-7 flex justify-between">
        <div>
          <h3 className="panel-title">Doanh thu 7 ngày</h3>
          <p className="text-sm text-muted-foreground">{money(total)}</p>
        </div>
        <Badge variant="outline">7 ngày gần nhất</Badge>
      </div>
      <div className="flex h-52 items-end gap-3 border-b border-l border-white/8 px-3">
        {days.map((day) => (
          <div
            key={day.label}
            className="flex h-full flex-1 items-end"
            title={money(day.total)}
          >
            <div
              className="w-full rounded-t-md bg-gradient-to-t from-primary/30 to-primary shadow-[0_0_24px_oklch(0.86_0.2_125/10%)] transition hover:brightness-110"
              style={{
                height: `${day.total ? Math.max((day.total / max) * 100, 4) : 0}%`,
              }}
            />
          </div>
        ))}
      </div>
      <div className="mt-3 grid grid-cols-7 text-center text-xs text-muted-foreground">
        {days.map((day) => (
          <span key={day.label}>{day.label}</span>
        ))}
      </div>
    </article>
  );
}
function Members({
  list,
  search,
  setSearch,
  status,
  setStatus,
  csv,
  reload,
  notice,
  manager,
}: {
  list: Member[];
  search: string;
  setSearch: (x: string) => void;
  status: string;
  setStatus: (x: string) => void;
  csv: () => void;
  reload: () => Promise<void>;
  notice: (x: string) => void;
  manager: boolean;
}) {
  const [editing, setEditing] = useState<Member | null>(null);
  const [saving, setSaving] = useState(false);
  async function edit(formData: FormData) {
    if (!editing || saving) return;
    setSaving(true);
    const value = (name: string) => {
      const raw = formData.get(name);
      return typeof raw === 'string' ? raw.trim() : '';
    };
    const nullable = (name: string) => value(name) || null;
    const response = await apiFetch(`/api/members/${editing.databaseId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fullName: value('fullName'),
        phone: value('phone'),
        email: nullable('email'),
        dateOfBirth: nullable('dateOfBirth'),
        gender: nullable('gender'),
        address: nullable('address'),
        emergencyContact: nullable('emergencyContact'),
        notes: nullable('notes'),
      }),
    });
    setSaving(false);
    if (!response.ok) {
      notice(await responseError(response, 'Không thể cập nhật hội viên.'));
      return;
    }
    setEditing(null);
    await reload();
    notice('Đã cập nhật thông tin hội viên');
  }
  async function toggle(member: Member) {
    const response = await apiFetch(`/api/members/${member.databaseId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: member.active ? 'inactive' : 'active' }),
    });
    notice(
      response.ok
        ? member.active
          ? 'Đã ngừng hoạt động hội viên'
          : 'Đã kích hoạt lại hội viên'
        : await responseError(response, 'Không thể cập nhật hội viên.'),
    );
    if (response.ok) await reload();
  }
  async function invite(member: Member) {
    const response = await apiFetch(
      `/api/members/${member.databaseId}/invite`,
      {
        method: 'POST',
      },
    );
    notice(
      response.ok
        ? 'Đã gửi lời mời đặt mật khẩu'
        : await responseError(response, 'Không thể gửi lời mời.'),
    );
  }
  async function freeze(member: Member) {
    if (!member.subscriptionId) return;
    if (member.subscriptionStatus === 'frozen') {
      const response = await apiFetch(
        `/api/subscriptions/${member.subscriptionId}/freeze`,
        { method: 'DELETE' },
      );
      notice(
        response.ok
          ? 'Đã mở lại gói tập'
          : await responseError(response, 'Không thể mở lại gói.'),
      );
      if (response.ok) await reload();
      return;
    }
    const endDate = window.prompt('Ngày kết thúc dự kiến (YYYY-MM-DD)');
    const reason = window.prompt('Lý do đóng băng');
    if (!endDate || !reason) return;
    const response = await apiFetch(
      `/api/subscriptions/${member.subscriptionId}/freeze`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          startDate: new Date().toISOString().slice(0, 10),
          endDate,
          reason,
        }),
      },
    );
    notice(
      response.ok
        ? 'Đã đóng băng gói tập'
        : await responseError(response, 'Không thể đóng băng gói.'),
    );
    if (response.ok) await reload();
  }
  return (
    <>
      <Head
        top="DANH SÁCH"
        title={`${list.length} hội viên`}
        action={
          <Button
            id="members-export-button"
            type="button"
            variant="outline"
            onClick={csv}
          >
            <Download /> Xuất CSV
          </Button>
        }
      />
      <div className="panel">
        <div className="mb-5 flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 size-4 text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
              placeholder="Tên, mã hoặc số điện thoại"
            />
          </div>
          <Select
            value={status}
            onValueChange={(v) => setStatus(v ?? 'Tất cả')}
          >
            <SelectTrigger className="w-full sm:w-44">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {['Tất cả', 'Đang tập', 'Sắp hết hạn', 'Hết hạn'].map((x) => (
                <SelectItem key={x} value={x}>
                  {x}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="mb-4 flex flex-wrap gap-x-5 gap-y-2 rounded-xl bg-muted/60 px-4 py-3 text-xs text-muted-foreground">
          <span>
            <b className="text-emerald-700">Đang tập:</b> gói còn hiệu lực trên
            7 ngày.
          </span>
          <span>
            <b className="text-amber-700">Sắp hết hạn:</b> gói còn tối đa 7
            ngày.
          </span>
          <span>
            <b className="text-rose-700">Hết hạn:</b> không có gói hợp lệ, gói
            đã hết hạn hoặc hội viên đã ngừng.
          </span>
        </div>
        <div className="overflow-x-auto">
          <Table className="min-w-[1050px] table-fixed">
            <TableHeader>
              <TableRow>
                <TableHead className="w-[24%]">Hội viên</TableHead>
                <TableHead className="w-[15%]">Liên hệ</TableHead>
                <TableHead className="w-[19%]">Gói tập</TableHead>
                <TableHead className="w-[11%]">Hết hạn</TableHead>
                <TableHead className="w-[12%]">Trạng thái</TableHead>
                <TableHead className="w-[19%]">Thao tác</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {list.map((m) => (
                <TableRow key={m.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <Avatar name={m.name} />
                      <div>
                        <b>{m.name}</b>
                        <p className="text-xs text-muted-foreground">{m.id}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <p>{m.phone}</p>
                    <p className="truncate text-xs text-muted-foreground">
                      {m.email || 'Chưa có email'}
                    </p>
                  </TableCell>
                  <TableCell>
                    <b className="text-sm">{m.plan}</b>
                    <p className="text-xs text-muted-foreground">
                      {m.remaining}
                    </p>
                  </TableCell>
                  <TableCell>{m.expiry}</TableCell>
                  <TableCell>
                    <Badge
                      className={
                        m.status === 'Đang tập'
                          ? 'bg-emerald-100 text-emerald-700'
                          : m.status === 'Sắp hết hạn'
                            ? 'bg-amber-100 text-amber-700'
                            : 'bg-rose-100 text-rose-700'
                      }
                    >
                      {m.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-2">
                      <Button
                        id={`member-edit-${m.databaseId}`}
                        type="button"
                        size="sm"
                        variant="outline"
                        onClick={() => setEditing(m)}
                      >
                        <Pencil /> Sửa
                      </Button>
                      <Button
                        id={`member-invite-${m.databaseId}`}
                        type="button"
                        size="sm"
                        variant="outline"
                        onClick={() => invite(m)}
                        disabled={!m.email}
                      >
                        Mời
                      </Button>
                      {manager && m.subscriptionId && (
                        <Button
                          id={`member-freeze-${m.databaseId}`}
                          type="button"
                          size="sm"
                          variant="outline"
                          onClick={() => freeze(m)}
                        >
                          {m.subscriptionStatus === 'frozen'
                            ? 'Mở gói'
                            : 'Đóng băng'}
                        </Button>
                      )}
                      <Button
                        id={`member-toggle-${m.databaseId}`}
                        type="button"
                        size="sm"
                        variant="outline"
                        onClick={() => toggle(m)}
                      >
                        {m.active ? 'Ngừng' : 'Kích hoạt'}
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        {!list.length && (
          <p className="py-12 text-center text-muted-foreground">
            Không tìm thấy hội viên.
          </p>
        )}
      </div>
      <Dialog
        open={editing !== null}
        onOpenChange={(isOpen) => !isOpen && setEditing(null)}
      >
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Chỉnh sửa hội viên</DialogTitle>
            <DialogDescription>
              Cập nhật hồ sơ của {editing?.name}. Mã hội viên được giữ nguyên.
            </DialogDescription>
          </DialogHeader>
          {editing && (
            <form action={edit} className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="edit-name">Họ và tên</Label>
                <Input
                  id="edit-name"
                  name="fullName"
                  defaultValue={editing.name}
                  required
                  minLength={2}
                  maxLength={150}
                  pattern="[^<>]*"
                  title="Họ tên không được chứa thẻ HTML"
                />
              </div>
              <div>
                <Label htmlFor="edit-phone">Số điện thoại</Label>
                <Input
                  id="edit-phone"
                  name="phone"
                  type="tel"
                  inputMode="numeric"
                  autoComplete="tel"
                  defaultValue={editing.phone}
                  required
                  pattern="0[0-9]{9}"
                  minLength={10}
                  maxLength={10}
                  title="Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0"
                />
              </div>
              <div>
                <Label htmlFor="edit-email">Email</Label>
                <Input
                  id="edit-email"
                  name="email"
                  type="email"
                  defaultValue={editing.email}
                />
              </div>
              <div>
                <Label htmlFor="edit-dob">Ngày sinh</Label>
                <Input
                  id="edit-dob"
                  name="dateOfBirth"
                  type="date"
                  defaultValue={editing.dateOfBirth}
                />
              </div>
              <div>
                <Label htmlFor="edit-gender">Giới tính</Label>
                <select
                  id="edit-gender"
                  name="gender"
                  defaultValue={editing.gender}
                  className="h-10 w-full rounded-lg border bg-background px-3"
                >
                  <option value="">Chưa chọn</option>
                  <option value="Nam">Nam</option>
                  <option value="Nữ">Nữ</option>
                  <option value="Khác">Khác</option>
                </select>
              </div>
              <div>
                <Label htmlFor="edit-emergency">Liên hệ khẩn cấp</Label>
                <Input
                  id="edit-emergency"
                  name="emergencyContact"
                  defaultValue={editing.emergencyContact}
                  maxLength={250}
                  pattern="[^<>]*"
                  title="Liên hệ khẩn cấp không được chứa thẻ HTML"
                />
              </div>
              <div className="sm:col-span-2">
                <Label htmlFor="edit-address">Địa chỉ</Label>
                <Input
                  id="edit-address"
                  name="address"
                  defaultValue={editing.address}
                  maxLength={500}
                  pattern="[^<>]*"
                  title="Địa chỉ không được chứa thẻ HTML"
                />
              </div>
              <div className="sm:col-span-2">
                <Label htmlFor="edit-notes">Ghi chú</Label>
                <textarea
                  id="edit-notes"
                  name="notes"
                  defaultValue={editing.notes}
                  rows={3}
                  className="w-full rounded-lg border bg-background px-3 py-2 text-sm"
                />
              </div>
              <div className="flex justify-end gap-2 sm:col-span-2">
                <Button
                  id="member-edit-cancel-button"
                  type="button"
                  variant="outline"
                  onClick={() => setEditing(null)}
                >
                  Hủy
                </Button>
                <Button
                  id="member-edit-submit-button"
                  type="submit"
                  disabled={saving}
                >
                  {saving ? 'Đang lưu…' : 'Lưu thay đổi'}
                </Button>
              </div>
            </form>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
function Plans({
  list,
  onCreated,
  notice,
  manager,
}: {
  list: Plan[];
  onCreated: () => Promise<void>;
  notice: (message: string) => void;
  manager: boolean;
}) {
  const [open, setOpen] = useState(false);
  const createPlan = async (formData: FormData) => {
    const response = await apiFetch('/api/plans', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: formData.get('name'),
        price: Number(formData.get('price')),
        durationDays: Number(formData.get('durationDays')),
        visitLimit: formData.get('visitLimit')
          ? Number(formData.get('visitLimit'))
          : null,
      }),
    });
    if (!response.ok)
      return notice(await responseError(response, 'Không thể tạo gói tập.'));
    setOpen(false);
    await onCreated();
    notice('Đã tạo gói tập');
  };
  const togglePlan = async (plan: Plan) => {
    const response = await apiFetch(`/api/plans/${plan.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ isActive: !plan.isActive }),
    });
    notice(
      response.ok
        ? 'Đã cập nhật trạng thái gói'
        : await responseError(response, 'Không thể cập nhật gói.'),
    );
    if (response.ok) await onCreated();
  };
  return (
    <>
      <Head
        top="SẢN PHẨM"
        title="Gói tập đang bán"
        action={
          manager ? (
            <Dialog open={open} onOpenChange={setOpen}>
              <DialogTrigger
                render={<Button id="plan-create-open-button" type="button" />}
              >
                + Tạo gói tập
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Tạo gói tập</DialogTitle>
                  <DialogDescription>
                    Thiết lập giá, thời hạn và số lượt tập.
                  </DialogDescription>
                </DialogHeader>
                <form action={createPlan} className="space-y-4">
                  <div>
                    <Label htmlFor="plan-name">Tên gói</Label>
                    <Input
                      id="plan-name"
                      name="name"
                      className="mt-2"
                      minLength={2}
                      maxLength={150}
                      pattern="[^<>]*"
                      title="Tên gói không được chứa thẻ HTML"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label htmlFor="plan-price">Giá (VNĐ)</Label>
                      <Input
                        id="plan-price"
                        name="price"
                        type="number"
                        min="0"
                        className="mt-2"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="plan-days">Số ngày</Label>
                      <Input
                        id="plan-days"
                        name="durationDays"
                        type="number"
                        min="1"
                        className="mt-2"
                        required
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="plan-visits">
                      Giới hạn lượt (để trống nếu không giới hạn)
                    </Label>
                    <Input
                      id="plan-visits"
                      name="visitLimit"
                      type="number"
                      min="1"
                      className="mt-2"
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button
                      id="plan-create-cancel-button"
                      type="button"
                      variant="outline"
                      onClick={() => setOpen(false)}
                    >
                      Hủy
                    </Button>
                    <Button id="plan-create-submit-button" type="submit">
                      Tạo gói
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          ) : (
            <Badge variant="outline">Chỉ xem</Badge>
          )
        }
      />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {list.map((plan) => (
          <article className="panel" key={plan.id}>
            <div className={`mb-6 h-2 w-14 rounded-full ${plan.color}`} />
            <h3 className="text-xl font-bold">{plan.name}</h3>
            <Badge variant="outline" className="mt-2">
              {plan.isActive ? 'Đang bán' : 'Ngừng bán'}
            </Badge>
            <p className="text-sm text-muted-foreground">
              Hiệu lực {plan.durationDays} ngày ·{' '}
              {plan.visitLimit
                ? `${plan.visitLimit} lượt`
                : 'Không giới hạn lượt'}
            </p>
            <p className="mt-8 text-2xl font-bold">{money(plan.price)}</p>
            <div className="mt-5 flex justify-between border-t pt-4 text-sm">
              <span className="text-muted-foreground">Đang sử dụng</span>
              <b>{plan.members} hội viên</b>
            </div>
            {manager && (
              <Button
                id={`plan-toggle-${plan.id}`}
                type="button"
                className="mt-4 w-full"
                variant="outline"
                onClick={() => togglePlan(plan)}
              >
                {plan.isActive ? 'Ngừng bán' : 'Mở bán'}
              </Button>
            )}
          </article>
        ))}
        {!list.length && (
          <p className="panel col-span-full py-12 text-center text-muted-foreground">
            Chưa có gói tập. Hãy tạo gói đầu tiên.
          </p>
        )}
      </div>
    </>
  );
}
function Checkin({
  qr,
  setQr,
  result,
  reason,
  submit,
}: {
  qr: string;
  setQr: (x: string) => void;
  result: 'ok' | 'error' | null;
  reason: string;
  submit: (token?: string) => void;
}) {
  const [cameraOpen, setCameraOpen] = useState(false);
  const [cameraError, setCameraError] = useState('');
  const [cameraLoading, setCameraLoading] = useState(false);
  const scannerRef = useRef<{
    stop: () => Promise<void>;
    clear: () => void;
  } | null>(null);
  const submitRef = useRef(submit);
  const scanLockedRef = useRef(false);

  useEffect(() => {
    submitRef.current = submit;
  }, [submit]);

  useEffect(() => {
    if (!cameraOpen) return;
    let disposed = false;

    const startCamera = async () => {
      setCameraError('');
      setCameraLoading(true);
      scanLockedRef.current = false;
      try {
        if (
          !window.isSecureContext &&
          window.location.hostname !== 'localhost'
        ) {
          throw new Error('INSECURE_CONTEXT');
        }
        const { Html5Qrcode, Html5QrcodeSupportedFormats } =
          await import('html5-qrcode');
        if (disposed) return;
        const scanner = new Html5Qrcode('checkin-camera-reader', {
          formatsToSupport: [Html5QrcodeSupportedFormats.QR_CODE],
          verbose: false,
        });
        scannerRef.current = scanner;
        await scanner.start(
          { facingMode: 'environment' },
          {
            fps: 10,
            qrbox: (width, height) => {
              const size = Math.floor(Math.min(width, height) * 0.72);
              return { width: size, height: size };
            },
          },
          (decodedText) => {
            if (scanLockedRef.current) return;
            scanLockedRef.current = true;
            setQr(decodedText.trim());
            setCameraOpen(false);
            submitRef.current(decodedText);
          },
          () => undefined,
        );
      } catch (error) {
        if (disposed) return;
        const name = error instanceof Error ? error.name : '';
        const message = error instanceof Error ? error.message : '';
        setCameraError(
          message === 'INSECURE_CONTEXT'
            ? 'Camera chỉ hoạt động trên HTTPS hoặc localhost.'
            : name === 'NotAllowedError' ||
                message.toLowerCase().includes('permission')
              ? 'Bạn chưa cấp quyền camera. Hãy cho phép camera trong cài đặt trình duyệt rồi thử lại.'
              : 'Không mở được camera. Hãy kiểm tra quyền camera hoặc nhập mã hội viên thủ công.',
        );
      } finally {
        if (!disposed) setCameraLoading(false);
      }
    };

    void startCamera();
    return () => {
      disposed = true;
      const scanner = scannerRef.current;
      scannerRef.current = null;
      if (scanner) {
        void scanner
          .stop()
          .catch(() => undefined)
          .finally(() => scanner.clear());
      }
    };
  }, [cameraOpen, setQr]);

  return (
    <>
      <Head top="LỄ TÂN" title="Check-in hội viên" />
      <div className="mx-auto grid max-w-4xl gap-6 md:grid-cols-2">
        <article className="panel text-center">
          <div className="mx-auto mb-5 grid size-24 place-items-center rounded-3xl bg-slate-950 text-primary">
            <QrCode size={48} />
          </div>
          <h3 className="panel-title">Quét hoặc nhập mã QR</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Nhập mã hội viên hoặc mã QR tại quầy.
          </p>
          <Input
            value={qr}
            onChange={(e) => setQr(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && submit()}
            className="mt-6 text-center uppercase"
            placeholder="Nhập mã hội viên"
          />
          <Button
            id="check-in-submit-button"
            type="button"
            className="mt-3 w-full"
            onClick={() => submit()}
          >
            Xác nhận check-in
          </Button>
          <Dialog open={cameraOpen} onOpenChange={setCameraOpen}>
            <DialogTrigger
              render={
                <Button
                  id="check-in-camera-open-button"
                  type="button"
                  className="mt-3 w-full"
                  variant="outline"
                />
              }
            >
              <Camera /> Quét bằng camera
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Quét QR hội viên</DialogTitle>
                <DialogDescription>
                  Hướng camera sau vào mã QR trên điện thoại hoặc thẻ hội viên.
                </DialogDescription>
              </DialogHeader>
              <div className="overflow-hidden rounded-xl bg-slate-950">
                <div id="checkin-camera-reader" className="min-h-72 w-full" />
              </div>
              {cameraLoading && (
                <p className="text-center text-sm text-muted-foreground">
                  Đang mở camera…
                </p>
              )}
              {cameraError && (
                <p className="text-center text-sm text-destructive">
                  {cameraError}
                </p>
              )}
              <p className="text-center text-xs text-muted-foreground">
                Mã sẽ được xác nhận tự động ngay khi quét thành công.
              </p>
            </DialogContent>
          </Dialog>
        </article>
        <article className="panel grid place-items-center text-center">
          {!result ? (
            <div>
              <Activity className="mx-auto mb-4 size-12 text-muted-foreground/30" />
              <b>Chờ mã hội viên</b>
            </div>
          ) : result === 'ok' ? (
            <div>
              <CheckCircle2 className="mx-auto mb-4 size-16 text-emerald-500" />
              <h3 className="text-xl font-bold">Check-in thành công</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Gói tập còn hiệu lực.
              </p>
            </div>
          ) : (
            <div>
              <XCircle className="mx-auto mb-4 size-16 text-rose-500" />
              <h3 className="text-xl font-bold">Không thể check-in</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {(
                  {
                    INVALID_QR: 'Không tìm thấy mã hội viên.',
                    MEMBER_INACTIVE: 'Hội viên đã ngừng hoạt động.',
                    SUBSCRIPTION_FROZEN: 'Gói tập đang đóng băng.',
                    SUBSCRIPTION_NOT_STARTED: 'Gói tập chưa bắt đầu.',
                    NO_VALID_SUBSCRIPTION: 'Không có gói còn hiệu lực.',
                    NO_VISITS_LEFT: 'Gói tập đã hết lượt.',
                    DUPLICATE: 'Đã check-in trong 10 phút gần nhất.',
                  } as Record<string, string>
                )[reason] ?? 'Không thể thực hiện check-in.'}
              </p>
            </div>
          )}
        </article>
      </div>
    </>
  );
}
function Payments({
  list,
  members,
  plans,
  onCreated,
  notice,
}: {
  list: Payment[];
  members: Member[];
  plans: Plan[];
  onCreated: () => Promise<void>;
  notice: (s: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const recordPayment = async (formData: FormData) => {
    const response = await apiFetch('/api/subscriptions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        memberId: formData.get('memberId'),
        planId: formData.get('planId'),
        method: formData.get('method'),
        startDate: formData.get('startDate'),
      }),
    });
    const payload = (await response.json()) as { ok?: boolean };
    if (!response.ok || !payload.ok)
      return notice(
        errorMessage(
          (payload as { error?: string; reason?: string }).error ??
            (payload as { reason?: string }).reason,
          'Không thể ghi nhận thanh toán.',
        ),
      );
    setOpen(false);
    await onCreated();
    notice('Đã ghi nhận thanh toán và kích hoạt gói');
  };
  return (
    <>
      <Head
        top="TÀI CHÍNH"
        title="Thanh toán"
        action={
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger
              render={
                <Button
                  id="payment-create-open-button"
                  type="button"
                  disabled={!members.length || !plans.length}
                />
              }
            >
              + Ghi nhận
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Ghi nhận thanh toán</DialogTitle>
                <DialogDescription>
                  Nếu còn gói hiệu lực, lần mua này sẽ tự động nối tiếp để không
                  mất ngày tập.
                </DialogDescription>
              </DialogHeader>
              <form action={recordPayment} className="space-y-4">
                <div>
                  <Label htmlFor="payment-member">Hội viên</Label>
                  <select
                    id="payment-member"
                    name="memberId"
                    className="mt-2 h-10 w-full rounded-lg border bg-background px-3 text-sm"
                    required
                  >
                    <option value="">Chọn hội viên</option>
                    {members.map((member) => (
                      <option key={member.databaseId} value={member.databaseId}>
                        {member.name} · {member.id}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label htmlFor="payment-plan">Gói tập</Label>
                  <select
                    id="payment-plan"
                    name="planId"
                    className="mt-2 h-10 w-full rounded-lg border bg-background px-3 text-sm"
                    required
                  >
                    <option value="">Chọn gói tập</option>
                    {plans.map((plan) => (
                      <option key={plan.id} value={plan.id}>
                        {plan.name} · {money(plan.price)}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label htmlFor="payment-method">Phương thức</Label>
                  <select
                    id="payment-method"
                    name="method"
                    className="mt-2 h-10 w-full rounded-lg border bg-background px-3 text-sm"
                    defaultValue="cash"
                  >
                    <option value="cash">Tiền mặt</option>
                    <option value="bank_transfer">Chuyển khoản</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="payment-start">
                    Ngày bắt đầu (nếu gia hạn, hệ thống tự nối tiếp)
                  </Label>
                  <Input
                    id="payment-start"
                    name="startDate"
                    type="date"
                    defaultValue={new Date().toISOString().slice(0, 10)}
                    className="mt-2"
                    required
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    id="payment-create-cancel-button"
                    type="button"
                    variant="outline"
                    onClick={() => setOpen(false)}
                  >
                    Hủy
                  </Button>
                  <Button id="payment-create-submit-button" type="submit">
                    Xác nhận
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        }
      />
      <div className="panel overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Mã phiếu</TableHead>
              <TableHead>Hội viên</TableHead>
              <TableHead>Nội dung</TableHead>
              <TableHead>Phương thức</TableHead>
              <TableHead>Ngày</TableHead>
              <TableHead className="text-right">Số tiền</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {list.map((payment) => (
              <TableRow key={payment.id}>
                <TableCell className="font-mono text-xs">
                  {payment.receiptCode}
                </TableCell>
                <TableCell className="font-semibold">
                  {payment.member}
                </TableCell>
                <TableCell>{payment.description}</TableCell>
                <TableCell>
                  <Badge variant="outline">{payment.method}</Badge>
                </TableCell>
                <TableCell>
                  {new Intl.DateTimeFormat('vi-VN').format(
                    new Date(payment.paidAt),
                  )}
                </TableCell>
                <TableCell className="text-right font-bold">
                  {money(payment.amount)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {!list.length && (
          <p className="py-12 text-center text-muted-foreground">
            Chưa có giao dịch thanh toán.
          </p>
        )}
      </div>
    </>
  );
}

type StaffItem = {
  id: string;
  username: string | null;
  full_name: string;
  role: 'manager' | 'staff';
  status: 'active' | 'inactive';
};
function Staff({ notice }: { notice: (x: string) => void }) {
  const [list, setList] = useState<StaffItem[]>([]);
  const [open, setOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const load = useCallback(async () => {
    const r = await apiFetch('/api/staff');
    if (r.ok) setList(await r.json());
  }, []);
  useEffect(() => {
    // oxlint-disable-next-line react/react-compiler -- initial API hydration
    void load();
  }, [load]);
  async function create(fd: FormData) {
    if (creating) return;
    setCreating(true);
    try {
      const r = await apiFetch('/api/staff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: fd.get('username'),
          fullName: fd.get('fullName'),
        }),
      });
      notice(
        r.ok
          ? 'Đã tạo nhân viên. Mật khẩu mặc định: admin123'
          : await responseError(r, 'Không thể tạo nhân viên.'),
      );
      if (r.ok) {
        setOpen(false);
        await load();
      }
    } catch {
      notice('Không thể kết nối máy chủ. Vui lòng thử lại.');
    } finally {
      setCreating(false);
    }
  }
  async function toggle(item: StaffItem) {
    const r = await apiFetch(`/api/staff/${item.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status: item.status === 'active' ? 'inactive' : 'active',
      }),
    });
    notice(
      r.ok
        ? 'Đã cập nhật tài khoản'
        : await responseError(r, 'Không thể cập nhật tài khoản.'),
    );
    if (r.ok) await load();
  }
  return (
    <>
      <Head
        top="PHÂN QUYỀN"
        title="Danh sách nhân viên"
        action={
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger
              render={<Button id="staff-create-open-button" type="button" />}
            >
              + Thêm nhân viên
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Thêm nhân viên</DialogTitle>
                <DialogDescription>
                  Nhân viên đăng nhập bằng tên tài khoản và mật khẩu mặc định
                  admin123.
                </DialogDescription>
              </DialogHeader>
              <form action={create} className="space-y-4">
                <div>
                  <Label htmlFor="staff-username">
                    Tên tài khoản đăng nhập
                  </Label>
                  <Input
                    id="staff-username"
                    name="username"
                    minLength={3}
                    maxLength={32}
                    pattern="[a-zA-Z0-9._-]+"
                    autoCapitalize="none"
                    autoComplete="off"
                    className="mt-2"
                    placeholder="Ví dụ: nguyenvana"
                    required
                  />
                  <p className="mt-2 text-xs text-muted-foreground">
                    Dùng 3–32 ký tự: chữ không dấu, số, dấu chấm, gạch ngang
                    hoặc gạch dưới.
                  </p>
                </div>
                <div>
                  <Label htmlFor="staff-full-name">Họ tên nhân viên</Label>
                  <Input
                    id="staff-full-name"
                    name="fullName"
                    className="mt-2"
                    required
                  />
                </div>
                <p className="rounded-xl border border-primary/15 bg-primary/8 p-3 text-sm text-muted-foreground">
                  Mật khẩu mặc định: <b className="text-primary">admin123</b>.
                  Nhân viên bắt buộc đổi mật khẩu trong lần đăng nhập đầu tiên.
                </p>
                <Button
                  id="staff-create-submit-button"
                  type="submit"
                  className="w-full"
                  disabled={creating}
                >
                  {creating && <Spinner />}
                  {creating ? 'Đang tạo nhân viên…' : 'Tạo nhân viên'}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        }
      />
      <div className="panel overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Họ tên</TableHead>
              <TableHead>Tên đăng nhập</TableHead>
              <TableHead>Vai trò</TableHead>
              <TableHead>Trạng thái</TableHead>
              <TableHead>Thao tác</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {list.map((x) => (
              <TableRow key={x.id}>
                <TableCell className="font-semibold">{x.full_name}</TableCell>
                <TableCell className="font-mono text-xs">
                  {x.username ?? '—'}
                </TableCell>
                <TableCell>
                  {x.role === 'manager' ? 'Quản lý' : 'Nhân viên'}
                </TableCell>
                <TableCell>
                  <Badge variant="outline">
                    {x.status === 'active' ? 'Hoạt động' : 'Đã khóa'}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Button
                    id={`staff-toggle-${x.id}`}
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => toggle(x)}
                  >
                    {x.status === 'active' ? 'Khóa' : 'Mở khóa'}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </>
  );
}

function Reports({
  csv,
  members,
  payments,
  renderedAt,
}: {
  csv: () => void;
  members: Member[];
  payments: Payment[];
  renderedAt: string;
}) {
  const validPayments = payments.filter(
    (payment) => payment.status === 'valid',
  );
  const revenue = validPayments.reduce(
    (sum, payment) => sum + payment.amount,
    0,
  );
  return (
    <>
      <Head
        top="PHÂN TÍCH"
        title="Báo cáo kinh doanh"
        action={
          <Button
            id="reports-export-button"
            type="button"
            variant="outline"
            onClick={csv}
          >
            <Download /> Tải báo cáo
          </Button>
        }
      />
      <div className="grid gap-4 md:grid-cols-3">
        {[
          [
            'Doanh thu tháng',
            money(revenue),
            `${validPayments.length} giao dịch hợp lệ`,
          ],
          [
            'Gói đã bán',
            String(validPayments.length),
            `${members.length} hội viên`,
          ],
          [
            'Doanh thu trung bình',
            money(validPayments.length ? revenue / validPayments.length : 0),
            'Mỗi giao dịch',
          ],
        ].map(([a, b, c]) => (
          <article className="metric-card" key={a}>
            <p className="text-sm text-muted-foreground">{a}</p>
            <p className="mt-4 text-3xl font-bold">{b}</p>
            <p className="mt-2 text-sm text-emerald-600">{c}</p>
          </article>
        ))}
      </div>
      <div className="mt-6">
        <Revenue payments={payments} renderedAt={renderedAt} />
      </div>
    </>
  );
}
