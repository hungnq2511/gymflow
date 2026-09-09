'use client';
import { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  CalendarClock,
  CheckCircle2,
  CircleDollarSign,
  Download,
  Dumbbell,
  LayoutDashboard,
  Menu,
  Package,
  QrCode,
  ReceiptText,
  Search,
  Settings,
  UserRoundPlus,
  Users,
  XCircle,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
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
import { supabase } from '@/utils/supabase';
type Page =
  | 'Tổng quan'
  | 'Hội viên'
  | 'Gói tập'
  | 'Check-in'
  | 'Thanh toán'
  | 'Báo cáo';
type Member = {
  id: string;
  name: string;
  phone: string;
  plan: string;
  expiry: string;
  status: 'Đang tập' | 'Sắp hết hạn' | 'Hết hạn';
  remaining: string;
};
const initialMembers: Member[] = [
  {
    id: 'GF-1042',
    name: 'Nguyễn Minh Anh',
    phone: '090 812 3456',
    plan: 'Gói 12 tháng',
    expiry: '18/05/2027',
    status: 'Đang tập',
    remaining: 'Không giới hạn',
  },
  {
    id: 'GF-1038',
    name: 'Trần Quốc Huy',
    phone: '091 234 8877',
    plan: 'Gói 3 tháng',
    expiry: '15/09/2026',
    status: 'Sắp hết hạn',
    remaining: 'Không giới hạn',
  },
  {
    id: 'GF-1029',
    name: 'Lê Hoàng Nam',
    phone: '098 771 2200',
    plan: 'Gói 30 lượt',
    expiry: '30/11/2026',
    status: 'Đang tập',
    remaining: '18 lượt',
  },
  {
    id: 'GF-1011',
    name: 'Phạm Thu Hà',
    phone: '093 566 4402',
    plan: 'Gói 6 tháng',
    expiry: '02/09/2026',
    status: 'Hết hạn',
    remaining: '0 lượt',
  },
  {
    id: 'GF-1007',
    name: 'Võ Gia Bảo',
    phone: '090 332 1199',
    plan: 'Gói 12 tháng',
    expiry: '21/03/2027',
    status: 'Đang tập',
    remaining: 'Không giới hạn',
  },
];
const plans = [
  ['Gói 1 tháng', 650000, '30 ngày', 48, 'bg-sky-500'],
  ['Gói 3 tháng', 1650000, '90 ngày', 102, 'bg-violet-500'],
  ['Gói 6 tháng', 2900000, '180 ngày', 96, 'bg-emerald-500'],
  ['Gói 12 tháng', 4900000, '365 ngày', 164, 'bg-orange-500'],
  ['Gói 30 lượt', 1200000, '120 ngày', 18, 'bg-pink-500'],
] as const;
const payments = [
  [
    'PT-260909-018',
    'Nguyễn Minh Anh',
    'Gói 12 tháng',
    4900000,
    'Chuyển khoản',
    '09/09/2026',
  ],
  [
    'PT-260908-041',
    'Trần Quốc Huy',
    'Gia hạn 3 tháng',
    1650000,
    'Tiền mặt',
    '08/09/2026',
  ],
  [
    'PT-260908-022',
    'Lê Hoàng Nam',
    'Gói 30 lượt',
    1200000,
    'Chuyển khoản',
    '08/09/2026',
  ],
  [
    'PT-260907-009',
    'Võ Gia Bảo',
    'Gói 12 tháng',
    4900000,
    'Tiền mặt',
    '07/09/2026',
  ],
] as const;
const money = (n: number) =>
  new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(n);
export default function GymApp() {
  const [page, setPage] = useState<Page>('Tổng quan'),
    [members, setMembers] = useState(initialMembers),
    [search, setSearch] = useState(''),
    [status, setStatus] = useState('Tất cả'),
    [open, setOpen] = useState(false),
    [mobile, setMobile] = useState(false),
    [toast, setToast] = useState(''),
    [database, setDatabase] = useState<'demo' | 'connected'>('demo'),
    [livePlans, setLivePlans] = useState<
      Array<[string, number, string, number, string]>
    >(plans.map((plan) => [...plan])),
    [qr, setQr] = useState(''),
    [result, setResult] = useState<'ok' | 'error' | null>(null);
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
  useEffect(() => {
    if (!supabase) return;
    void supabase
      .from('membership_plans')
      .select('name,price,duration_days')
      .eq('is_active', true)
      .order('price')
      .then(({ data }) => {
        if (!data?.length) return;
        const colors = [
          'bg-sky-500',
          'bg-violet-500',
          'bg-emerald-500',
          'bg-orange-500',
          'bg-pink-500',
        ];
        setLivePlans(
          data.map((plan, index) => [
            plan.name,
            Number(plan.price),
            `${plan.duration_days} ngày`,
            0,
            colors[index % colors.length],
          ]),
        );
      });
  }, []);
  useEffect(() => {
    void fetch('/api/bootstrap')
      .then(async (response) => {
        if (!response.ok) return;
        const data = (await response.json()) as {
          members: Array<{
            member_code: string;
            full_name: string;
            phone: string;
            status: string;
            subscriptions?: Array<{
              end_date: string;
              remaining_visits: number | null;
              status: string;
              membership_plans?: { name: string } | null;
            }>;
          }>;
        };
        setMembers(
          data.members.map((member) => {
            const subscription = member.subscriptions?.find(
              (item) => item.status === 'active',
            );
            const expired = subscription
              ? subscription.end_date < new Date().toISOString().slice(0, 10)
              : true;
            return {
              id: member.member_code,
              name: member.full_name,
              phone: member.phone,
              plan: subscription?.membership_plans?.name ?? 'Chưa có gói',
              expiry: subscription?.end_date ?? '—',
              status: expired ? 'Hết hạn' : 'Đang tập',
              remaining:
                subscription?.remaining_visits == null
                  ? 'Không giới hạn'
                  : `${subscription.remaining_visits} lượt`,
            };
          }),
        );
        setDatabase('connected');
      })
      .catch(() => undefined);
  }, []);
  useEffect(() => {
    const c = (
      document as Document & {
        modelContext?: { registerTool: (t: unknown, o?: unknown) => unknown };
      }
    ).modelContext;
    if (!c?.registerTool) return;
    const a = new AbortController();
    void Promise.resolve(
      c.registerTool(
        {
          name: 'search_members',
          title: 'Tìm hội viên',
          description: 'Tìm hội viên theo tên, mã hoặc số điện thoại.',
          inputSchema: {
            type: 'object',
            properties: { query: { type: 'string' } },
            required: ['query'],
            additionalProperties: false,
          },
          annotations: { readOnlyHint: true, untrustedContentHint: false },
          execute: (i: unknown) => {
            const q = String((i as { query?: string }).query ?? '').trim();
            if (!q) throw Error('Vui lòng nhập từ khóa');
            setPage('Hội viên');
            setSearch(q);
            return {
              query: q,
              count: initialMembers.filter((m) =>
                `${m.name} ${m.id} ${m.phone}`
                  .toLowerCase()
                  .includes(q.toLowerCase()),
              ).length,
            };
          },
        },
        { signal: a.signal },
      ),
    );
    return () => a.abort();
  }, []);
  const notice = (s: string) => {
      setToast(s);
      setTimeout(() => setToast(''), 2500);
    },
    add = async (d: FormData) => {
      const rawName = d.get('name'),
        rawPhone = d.get('phone'),
        name = typeof rawName === 'string' ? rawName.trim() : '',
        phone = typeof rawPhone === 'string' ? rawPhone.trim() : '';
      if (!name || !phone) return;
      if (database === 'connected') {
        const response = await fetch('/api/members', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fullName: name, phone }),
        });
        if (!response.ok) {
          notice('Không thể lưu hội viên');
          return;
        }
      }
      setMembers((v) => [
        {
          id: `GF-${1050 + v.length}`,
          name,
          phone,
          plan: 'Chưa có gói',
          expiry: '—',
          status: 'Hết hạn',
          remaining: '—',
        },
        ...v,
      ]);
      setOpen(false);
      notice('Đã thêm hội viên mới');
    },
    checkin = async () => {
      if (database === 'connected') {
        const response = await fetch('/api/check-ins', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: qr.trim() }),
        });
        const payload = (await response.json()) as { ok?: boolean };
        setResult(response.ok && payload.ok ? 'ok' : 'error');
        if (response.ok && payload.ok) notice('Check-in thành công');
        return;
      }
      const m = members.find(
        (x) => x.id.toLowerCase() === qr.trim().toLowerCase(),
      );
      setResult(m && m.status !== 'Hết hạn' ? 'ok' : 'error');
      if (m && m.status !== 'Hết hạn') notice(`Check-in thành công: ${m.name}`);
    },
    csv = () => {
      const rows = [
        ['Mã', 'Họ tên', 'Điện thoại', 'Gói', 'Hết hạn', 'Trạng thái'],
        ...members.map((m) => [
          m.id,
          m.name,
          m.phone,
          m.plan,
          m.expiry,
          m.status,
        ]),
      ];
      const b = new Blob(['\uFEFF' + rows.map((r) => r.join(',')).join('\n')], {
          type: 'text/csv',
        }),
        a = document.createElement('a');
      a.href = URL.createObjectURL(b);
      a.download = 'danh-sach-hoi-vien.csv';
      a.click();
      notice('Đã xuất danh sách CSV');
    };
  const nav: [[Page, typeof LayoutDashboard]][number][] = [
    ['Tổng quan', LayoutDashboard],
    ['Hội viên', Users],
    ['Gói tập', Package],
    ['Check-in', QrCode],
    ['Thanh toán', ReceiptText],
    ['Báo cáo', Activity],
  ];
  return (
    <main className="min-h-screen bg-background">
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 border-r border-white/8 bg-sidebar px-4 py-6 transition-transform lg:translate-x-0 ${mobile ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="mb-9 flex items-center gap-3 px-3">
          <span className="grid size-10 place-items-center rounded-xl bg-primary">
            <Dumbbell size={22} />
          </span>
          <div>
            <p className="font-heading text-lg font-bold text-white">GYMFLOW</p>
            <p className="text-xs text-white/45">
              Quận 7 · {database === 'connected' ? 'Supabase' : 'Dữ liệu mẫu'}
            </p>
          </div>
        </div>
        <nav className="space-y-1">
          {nav.map(([n, I]) => (
            <button
              key={n}
              onClick={() => {
                setPage(n);
                setMobile(false);
              }}
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium ${page === n ? 'bg-primary text-primary-foreground' : 'text-white/60 hover:bg-white/6 hover:text-white'}`}
            >
              <I size={18} />
              {n}
            </button>
          ))}
        </nav>
        <button className="absolute inset-x-4 bottom-5 flex items-center gap-3 rounded-2xl border border-white/8 bg-white/4 p-4 text-left">
          <Avatar name="Quang Hùng" />
          <span>
            <b className="block text-sm text-white">Quang Hùng</b>
            <small className="text-white/45">Quản lý</small>
          </span>
          <Settings className="ml-auto size-4 text-white/40" />
        </button>
      </aside>
      {mobile && (
        <button
          aria-label="Đóng menu"
          className="fixed inset-0 z-30 bg-slate-950/40 lg:hidden"
          onClick={() => setMobile(false)}
        />
      )}
      <section className="lg:ml-64">
        <header className="flex h-20 items-center justify-between border-b bg-white px-4 md:px-8">
          <div className="flex items-center gap-3">
            <Button
              className="lg:hidden"
              variant="outline"
              size="icon"
              onClick={() => setMobile(true)}
            >
              <Menu />
            </Button>
            <div>
              <p className="hidden text-sm text-muted-foreground sm:block">
                Thứ Tư, 09 tháng 09
              </p>
              <h1 className="text-lg font-bold">{page}</h1>
            </div>
          </div>
          <AddDialog open={open} setOpen={setOpen} add={add} />
        </header>
        <div className="mx-auto max-w-7xl p-4 md:p-8">
          {page === 'Tổng quan' && <Dashboard />}
          {page === 'Hội viên' && (
            <Members
              list={filtered}
              search={search}
              setSearch={setSearch}
              status={status}
              setStatus={setStatus}
              csv={csv}
            />
          )}{' '}
          {page === 'Gói tập' && <Plans list={livePlans} />}
          {page === 'Check-in' && (
            <Checkin qr={qr} setQr={setQr} result={result} submit={checkin} />
          )}{' '}
          {page === 'Thanh toán' && <Payments notice={notice} />}{' '}
          {page === 'Báo cáo' && <Reports csv={csv} />}
        </div>
      </section>
      {toast && (
        <output className="fixed bottom-5 right-5 z-50 rounded-xl bg-slate-900 px-4 py-3 text-sm font-medium text-white shadow-xl">
          {toast}
        </output>
      )}
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
      <DialogTrigger render={<Button />}>
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
            <Input id="name" name="name" className="mt-2" required />
          </div>
          <div>
            <Label htmlFor="phone">Số điện thoại</Label>
            <Input id="phone" name="phone" className="mt-2" required />
          </div>
          <div>
            <Label htmlFor="email">Email</Label>
            <Input id="email" name="email" type="email" className="mt-2" />
          </div>
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
            >
              Hủy
            </Button>
            <Button type="submit">Lưu hội viên</Button>
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
    <div className="mb-7 flex items-end justify-between gap-3">
      <div>
        <p className="eyebrow">{top}</p>
        <h2 className="text-2xl font-bold md:text-3xl">{title}</h2>
      </div>
      {action}
    </div>
  );
}
function Avatar({ name }: { name: string }) {
  return (
    <span className="grid size-10 shrink-0 place-items-center rounded-full bg-secondary font-bold text-primary">
      {name.split(' ').at(-1)?.[0]}
    </span>
  );
}
function Dashboard() {
  const ci = [
    ['Nguyễn Minh Anh', 'Gói 12 tháng', '07:42'],
    ['Trần Quốc Huy', 'Gói 3 tháng', '08:15'],
    ['Lê Hoàng Nam', 'Gói 30 lượt', '08:38'],
    ['Phạm Thu Hà', 'Gói 6 tháng', '09:03'],
  ];
  return (
    <>
      <Head
        top="TÌNH HÌNH HÔM NAY"
        title="Tổng quan vận hành"
        action={<Badge variant="outline">Cập nhật 09:12</Badge>}
      />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          ['Hội viên hoạt động', '428', '+12 tháng này', Users],
          ['Check-in hôm nay', '64', 'Đỉnh điểm 18:00', Activity],
          [
            'Doanh thu tháng',
            '128,4 tr',
            '+8,2% tháng trước',
            CircleDollarSign,
          ],
          ['Sắp hết hạn', '18', 'Trong 7 ngày tới', CalendarClock],
        ].map(([l, v, n, I]) => (
          <article key={l as string} className="metric-card">
            <div className="mb-6 flex justify-between">
              <p className="text-sm text-muted-foreground">{l as string}</p>
              <span className="icon-chip">
                <I size={18} />
              </span>
            </div>
            <p className="text-3xl font-bold">{v as string}</p>
            <p className="mt-2 text-xs text-muted-foreground">{n as string}</p>
          </article>
        ))}
      </div>
      <div className="mt-6 grid gap-6 xl:grid-cols-[1.55fr_1fr]">
        <Revenue />
        <article className="panel">
          <h3 className="panel-title mb-4">Check-in gần đây</h3>
          <div className="divide-y">
            {ci.map(([n, p, t]) => (
              <div key={n} className="flex items-center gap-3 py-3">
                <Avatar name={n} />
                <div className="min-w-0 flex-1">
                  <b className="block truncate text-sm">{n}</b>
                  <small className="text-muted-foreground">{p}</small>
                </div>
                <time className="text-sm">{t}</time>
              </div>
            ))}
          </div>
        </article>
      </div>
    </>
  );
}
function Revenue() {
  return (
    <article className="panel min-h-[340px]">
      <div className="mb-7 flex justify-between">
        <div>
          <h3 className="panel-title">Doanh thu 7 ngày</h3>
          <p className="text-sm text-muted-foreground">26,8 triệu đồng</p>
        </div>
        <Badge className="bg-emerald-100 text-emerald-700">+14,2%</Badge>
      </div>
      <div className="flex h-52 items-end gap-3 border-b border-l px-3">
        {[42, 62, 49, 78, 68, 92, 82].map((h, i) => (
          <div key={i} className="flex h-full flex-1 items-end">
            <div
              className="w-full rounded-t-md bg-primary/85 hover:bg-primary"
              style={{ height: `${h}%` }}
            />
          </div>
        ))}
      </div>
      <div className="mt-3 grid grid-cols-7 text-center text-xs text-muted-foreground">
        {['T4', 'T5', 'T6', 'T7', 'CN', 'T2', 'T3'].map((x) => (
          <span key={x}>{x}</span>
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
}: {
  list: Member[];
  search: string;
  setSearch: (x: string) => void;
  status: string;
  setStatus: (x: string) => void;
  csv: () => void;
}) {
  return (
    <>
      <Head
        top="DANH SÁCH"
        title={`${list.length} hội viên`}
        action={
          <Button variant="outline" onClick={csv}>
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
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Hội viên</TableHead>
                <TableHead>Liên hệ</TableHead>
                <TableHead>Gói tập</TableHead>
                <TableHead>Hết hạn</TableHead>
                <TableHead>Trạng thái</TableHead>
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
                  <TableCell>{m.phone}</TableCell>
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
    </>
  );
}
function Plans({
  list,
}: {
  list: Array<[string, number, string, number, string]>;
}) {
  return (
    <>
      <Head
        top="SẢN PHẨM"
        title="Gói tập đang bán"
        action={<Button>+ Tạo gói tập</Button>}
      />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {list.map(([n, p, d, m, c]) => (
          <article className="panel" key={n}>
            <div className={`mb-6 h-2 w-14 rounded-full ${c}`} />
            <h3 className="text-xl font-bold">{n}</h3>
            <p className="text-sm text-muted-foreground">Hiệu lực {d}</p>
            <p className="mt-8 text-2xl font-bold">{money(p)}</p>
            <div className="mt-5 flex justify-between border-t pt-4 text-sm">
              <span className="text-muted-foreground">Đang sử dụng</span>
              <b>{m} hội viên</b>
            </div>
            <Button variant="outline" className="mt-4 w-full">
              Chỉnh sửa gói
            </Button>
          </article>
        ))}
      </div>
    </>
  );
}
function Checkin({
  qr,
  setQr,
  result,
  submit,
}: {
  qr: string;
  setQr: (x: string) => void;
  result: 'ok' | 'error' | null;
  submit: () => void;
}) {
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
            Nhập mã hội viên để mô phỏng máy quét.
          </p>
          <Input
            value={qr}
            onChange={(e) => setQr(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && submit()}
            className="mt-6 text-center uppercase"
            placeholder="GF-1042"
          />
          <Button className="mt-3 w-full" onClick={submit}>
            Xác nhận check-in
          </Button>
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
                Mã sai hoặc gói đã hết hạn.
              </p>
            </div>
          )}
        </article>
      </div>
    </>
  );
}
function Payments({ notice }: { notice: (s: string) => void }) {
  return (
    <>
      <Head
        top="TÀI CHÍNH"
        title="Thanh toán"
        action={
          <Button onClick={() => notice('Đã mở phiếu thu mới')}>
            + Ghi nhận
          </Button>
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
            {payments.map((p) => (
              <TableRow key={p[0]}>
                <TableCell className="font-mono text-xs">{p[0]}</TableCell>
                <TableCell className="font-semibold">{p[1]}</TableCell>
                <TableCell>{p[2]}</TableCell>
                <TableCell>
                  <Badge variant="outline">{p[4]}</Badge>
                </TableCell>
                <TableCell>{p[5]}</TableCell>
                <TableCell className="text-right font-bold">
                  {money(p[3])}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </>
  );
}
function Reports({ csv }: { csv: () => void }) {
  return (
    <>
      <Head
        top="PHÂN TÍCH"
        title="Báo cáo kinh doanh"
        action={
          <Button variant="outline" onClick={csv}>
            <Download /> Tải báo cáo
          </Button>
        }
      />
      <div className="grid gap-4 md:grid-cols-3">
        {[
          ['Doanh thu tháng 9', '128,4 tr', 'Tăng 8,2%'],
          ['Gói đã bán', '42', '16 lượt gia hạn'],
          ['Doanh thu trung bình', '3,06 tr', 'Trên mỗi giao dịch'],
        ].map(([a, b, c]) => (
          <article className="metric-card" key={a}>
            <p className="text-sm text-muted-foreground">{a}</p>
            <p className="mt-4 text-3xl font-bold">{b}</p>
            <p className="mt-2 text-sm text-emerald-600">{c}</p>
          </article>
        ))}
      </div>
      <div className="mt-6">
        <Revenue />
      </div>
    </>
  );
}
