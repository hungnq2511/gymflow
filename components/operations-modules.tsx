'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  CircleDollarSign,
  ClipboardCheck,
  Plus,
  RefreshCw,
  XCircle,
} from 'lucide-react';
import { apiFetch } from '@/lib/api-fetch';
import { responseError } from '@/lib/error-messages';
import { vietnamDateTimeLocal } from '@/lib/http';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { NativeSelect } from '@/components/ui/native-select';
import { Textarea } from '@/components/ui/textarea';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

const money = (value: number) =>
  new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(value);
const dateTime = (value: string) =>
  new Date(value).toLocaleString('vi-VN', {
    dateStyle: 'short',
    timeStyle: 'short',
  });

type Notice = (message: string) => void;

type FollowUpData = {
  candidates: Array<{
    id: string;
    member_code: string;
    full_name: string;
    phone: string;
    subscription: { end_date: string; remaining_visits: number | null };
  }>;
  followUps: Array<{
    id: string;
    status: string;
    note: string | null;
    next_contact_at: string | null;
    members?: { full_name: string; member_code: string; phone: string };
    profiles?: { full_name: string };
  }>;
  staff: Array<{ id: string; full_name: string }>;
  actorRole: 'manager' | 'staff';
};

export function FollowUpsModule({
  notice,
  manager,
}: {
  notice: Notice;
  manager: boolean;
}) {
  const [data, setData] = useState<FollowUpData | null>(null);
  const [minimumContactTime] = useState(() =>
    vietnamDateTimeLocal(new Date(Date.now() + 60_000)),
  );
  const load = useCallback(async () => {
    const response = await apiFetch('/api/follow-ups');
    if (!response.ok)
      return notice(
        await responseError(response, 'Không thể tải danh sách chăm sóc.'),
      );
    setData(await response.json());
  }, [notice]);
  useEffect(() => {
    // oxlint-disable-next-line react/react-compiler -- hydrate API-backed state on mount
    void load();
  }, [load]);
  async function create(formData: FormData) {
    const response = await apiFetch('/api/follow-ups', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        memberId: formData.get('memberId'),
        assignedTo: formData.get('assignedTo'),
        note: formData.get('note'),
        nextContactAt: formData.get('nextContactAt') || null,
      }),
    });
    notice(
      response.ok
        ? 'Đã tạo lịch chăm sóc.'
        : await responseError(response, 'Không thể tạo lịch chăm sóc.'),
    );
    if (response.ok) await load();
  }
  async function update(id: string, status: string) {
    const response = await apiFetch(`/api/follow-ups/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    notice(
      response.ok
        ? 'Đã cập nhật kết quả chăm sóc.'
        : await responseError(response, 'Không thể cập nhật.'),
    );
    if (response.ok) await load();
  }
  if (!data) return <Loading />;
  return (
    <div className="space-y-6">
      <PageHead
        eyebrow="GIỮ CHÂN HỘI VIÊN"
        title={manager ? 'Chăm sóc và nhắc gia hạn' : 'Lịch chăm sóc của tôi'}
        action={
          <Button
            id="follow-ups-refresh-button"
            type="button"
            variant="outline"
            onClick={load}
          >
            <RefreshCw /> Làm mới
          </Button>
        }
      />
      {manager && (
        <div className="grid gap-6 xl:grid-cols-[.9fr_1.6fr]">
          <form action={create} className="panel space-y-4">
            <h3 className="panel-title">Tạo lịch chăm sóc</h3>
            <Field label="Hội viên cần liên hệ">
              <NativeSelect
                name="memberId"
                className="w-full"
                required
                defaultValue=""
              >
                <option value="" disabled>
                  Chọn hội viên
                </option>
                {data.candidates.map((x) => (
                  <option key={x.id} value={x.id}>
                    {x.full_name} · hết hạn {x.subscription.end_date}
                  </option>
                ))}
              </NativeSelect>
            </Field>
            <Field label="Người phụ trách">
              <NativeSelect
                name="assignedTo"
                className="w-full"
                defaultValue=""
                required
              >
                <option value="" disabled>
                  Chọn nhân viên
                </option>
                {data.staff.map((x) => (
                  <option key={x.id} value={x.id}>
                    {x.full_name}
                  </option>
                ))}
              </NativeSelect>
            </Field>
            <Field label="Nhắc lại lúc">
              <Input
                name="nextContactAt"
                type="datetime-local"
                min={minimumContactTime}
              />
            </Field>
            <Field label="Ghi chú">
              <Textarea
                name="note"
                placeholder="Nội dung trao đổi hoặc nhu cầu của hội viên"
              />
            </Field>
            <Button
              id="follow-up-create-button"
              type="submit"
              className="w-full"
            >
              <Plus /> Tạo lịch
            </Button>
          </form>
          <section className="panel overflow-hidden">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="panel-title">Cần liên hệ trong 30 ngày</h3>
              <Badge variant="outline">{data.candidates.length} hội viên</Badge>
            </div>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Hội viên</TableHead>
                  <TableHead>Liên hệ</TableHead>
                  <TableHead>Gói</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.candidates.map((x) => (
                  <TableRow key={x.id}>
                    <TableCell>
                      <b>{x.full_name}</b>
                      <small className="block text-muted-foreground">
                        {x.member_code}
                      </small>
                    </TableCell>
                    <TableCell>{x.phone}</TableCell>
                    <TableCell>
                      <span className="block">
                        Hết hạn {x.subscription.end_date}
                      </span>
                      <small className="text-muted-foreground">
                        {x.subscription.remaining_visits == null
                          ? 'Không giới hạn lượt'
                          : `Còn ${x.subscription.remaining_visits} lượt`}
                      </small>
                    </TableCell>
                  </TableRow>
                ))}
                {!data.candidates.length && (
                  <EmptyRow
                    columns={3}
                    text="Không có hội viên cần cảnh báo."
                  />
                )}
              </TableBody>
            </Table>
          </section>
        </div>
      )}
      <section className="panel overflow-hidden">
        <h3 className="panel-title mb-4">
          {manager ? 'Lịch sử chăm sóc' : 'Công việc được quản lý giao'}
        </h3>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Hội viên</TableHead>
              {manager && <TableHead>Phụ trách</TableHead>}
              <TableHead>Nhắc lại</TableHead>
              <TableHead>Ghi chú</TableHead>
              <TableHead>Kết quả</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.followUps.map((x) => (
              <TableRow key={x.id}>
                <TableCell>
                  <b>{x.members?.full_name}</b>
                  <small className="block text-muted-foreground">
                    {x.members?.phone}
                  </small>
                </TableCell>
                {manager && (
                  <TableCell>{x.profiles?.full_name ?? '—'}</TableCell>
                )}
                <TableCell>
                  {x.next_contact_at ? dateTime(x.next_contact_at) : '—'}
                </TableCell>
                <TableCell className="max-w-64 truncate">
                  {x.note || '—'}
                </TableCell>
                <TableCell>
                  <NativeSelect
                    value={x.status}
                    onChange={(event) => void update(x.id, event.target.value)}
                  >
                    <option value="pending">Chờ liên hệ</option>
                    <option value="contacted">Đã liên hệ</option>
                    <option value="scheduled">Hẹn gia hạn</option>
                    <option value="renewed">Đã gia hạn</option>
                    <option value="not_interested">Không quan tâm</option>
                  </NativeSelect>
                </TableCell>
              </TableRow>
            ))}
            {!data.followUps.length && (
              <EmptyRow
                columns={manager ? 5 : 4}
                text={
                  manager
                    ? 'Chưa có lịch sử chăm sóc.'
                    : 'Bạn chưa được giao lịch chăm sóc nào.'
                }
              />
            )}
          </TableBody>
        </Table>
      </section>
    </div>
  );
}

type ExpenseData = {
  expenses: Array<{
    id: string;
    description: string;
    amount: number;
    expense_date: string;
    receipt_number: string | null;
    recurring: boolean;
    status: string;
    expense_categories?: { name: string };
  }>;
  categories: Array<{ id: string; name: string }>;
  summary: { revenue: number; expenses: number; profit: number };
  from: string;
  to: string;
};

export function ExpensesModule({ notice }: { notice: Notice }) {
  const [data, setData] = useState<ExpenseData | null>(null);
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const load = useCallback(async () => {
    const query = new URLSearchParams();
    if (from) query.set('from', from);
    if (to) query.set('to', to);
    const response = await apiFetch(`/api/expenses?${query}`);
    if (!response.ok)
      return notice(await responseError(response, 'Không thể tải chi phí.'));
    setData(await response.json());
  }, [from, notice, to]);
  useEffect(() => {
    // oxlint-disable-next-line react/react-compiler -- hydrate API-backed state on mount
    void load();
  }, [load]);
  async function create(fd: FormData) {
    const response = await apiFetch('/api/expenses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'create',
        categoryId: fd.get('categoryId'),
        description: fd.get('description'),
        amount: fd.get('amount'),
        expenseDate: fd.get('expenseDate'),
        receiptNumber: fd.get('receiptNumber'),
        recurring: fd.get('recurring') === 'on',
      }),
    });
    notice(
      response.ok
        ? 'Đã ghi nhận chi phí.'
        : await responseError(response, 'Không thể ghi nhận chi phí.'),
    );
    if (response.ok) await load();
  }
  async function cancel(id: string) {
    const response = await apiFetch('/api/expenses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'cancel', expenseId: id }),
    });
    notice(
      response.ok
        ? 'Đã hủy khoản chi.'
        : await responseError(response, 'Không thể hủy khoản chi.'),
    );
    if (response.ok) await load();
  }
  const grouped = useMemo(
    () =>
      data?.expenses
        .filter((x) => x.status === 'valid')
        .reduce<Record<string, number>>(
          (result, item) => ({
            ...result,
            [item.expense_categories?.name ?? 'Khác']:
              (result[item.expense_categories?.name ?? 'Khác'] ?? 0) +
              Number(item.amount),
          }),
          {},
        ) ?? {},
    [data],
  );
  if (!data) return <Loading />;
  return (
    <div className="space-y-6">
      <PageHead
        eyebrow="TÀI CHÍNH"
        title="Chi phí và lợi nhuận"
        action={
          <div className="flex gap-2">
            <Input
              aria-label="Từ ngày"
              type="date"
              value={from || data.from}
              onChange={(e) => setFrom(e.target.value)}
            />
            <Input
              aria-label="Đến ngày"
              type="date"
              value={to || data.to}
              onChange={(e) => setTo(e.target.value)}
            />
          </div>
        }
      />
      <div className="grid gap-4 md:grid-cols-3">
        <Metric
          label="Doanh thu"
          value={money(data.summary.revenue)}
          icon={<CircleDollarSign />}
        />
        <Metric
          label="Chi phí"
          value={money(data.summary.expenses)}
          icon={<ClipboardCheck />}
        />
        <Metric
          label="Lợi nhuận"
          value={money(data.summary.profit)}
          icon={<CircleDollarSign />}
          accent={data.summary.profit >= 0}
        />
      </div>
      <div className="grid gap-6 xl:grid-cols-[.8fr_1.5fr]">
        <form action={create} className="panel space-y-4">
          <h3 className="panel-title">Ghi nhận khoản chi</h3>
          <Field label="Danh mục">
            <NativeSelect name="categoryId" className="w-full" required>
              {data.categories.map((x) => (
                <option key={x.id} value={x.id}>
                  {x.name}
                </option>
              ))}
            </NativeSelect>
          </Field>
          <Field label="Nội dung">
            <Input name="description" required />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Số tiền">
              <Input name="amount" type="number" min="1" required />
            </Field>
            <Field label="Ngày chi">
              <Input
                name="expenseDate"
                type="date"
                defaultValue={new Date().toISOString().slice(0, 10)}
                required
              />
            </Field>
          </div>
          <Field label="Số hóa đơn">
            <Input name="receiptNumber" />
          </Field>
          <label className="flex items-center gap-2 text-sm">
            <input name="recurring" type="checkbox" /> Chi phí định kỳ
          </label>
          <Button id="expense-create-button" type="submit" className="w-full">
            <Plus /> Lưu khoản chi
          </Button>
          <div className="border-t border-white/8 pt-4">
            <p className="text-sm font-medium">Theo danh mục</p>
            {Object.entries(grouped).map(([name, amount]) => (
              <div
                key={name}
                className="mt-2 flex justify-between text-sm text-muted-foreground"
              >
                <span>{name}</span>
                <b>{money(amount)}</b>
              </div>
            ))}
          </div>
        </form>
        <section className="panel overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Ngày</TableHead>
                <TableHead>Nội dung</TableHead>
                <TableHead>Danh mục</TableHead>
                <TableHead>Số tiền</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.expenses.map((x) => (
                <TableRow
                  key={x.id}
                  className={x.status === 'cancelled' ? 'opacity-45' : ''}
                >
                  <TableCell>{x.expense_date}</TableCell>
                  <TableCell>
                    <b>{x.description}</b>
                    {x.receipt_number && (
                      <small className="block text-muted-foreground">
                        HĐ: {x.receipt_number}
                      </small>
                    )}
                  </TableCell>
                  <TableCell>{x.expense_categories?.name}</TableCell>
                  <TableCell>{money(Number(x.amount))}</TableCell>
                  <TableCell>
                    {x.status === 'valid' && (
                      <Button
                        id={`expense-cancel-${x.id}`}
                        type="button"
                        size="icon"
                        variant="ghost"
                        aria-label="Hủy khoản chi"
                        onClick={() => void cancel(x.id)}
                      >
                        <XCircle />
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
              {!data.expenses.length && (
                <EmptyRow columns={5} text="Chưa có chi phí trong kỳ." />
              )}
            </TableBody>
          </Table>
        </section>
      </div>
    </div>
  );
}

function PageHead({
  eyebrow,
  title,
  action,
}: {
  eyebrow: string;
  title: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h2 className="mt-2 text-3xl font-semibold tracking-tight">{title}</h2>
      </div>
      {action}
    </div>
  );
}
function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <Label className="mb-2 block">{label}</Label>
      {children}
    </div>
  );
}
function Metric({
  label,
  value,
  icon,
  accent,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
  accent?: boolean;
}) {
  return (
    <article className="metric-card">
      <div className="flex justify-between">
        <p className="text-sm text-muted-foreground">{label}</p>
        <span className="icon-chip">{icon}</span>
      </div>
      <p
        className={`mt-5 text-3xl font-semibold ${accent ? 'text-primary' : ''}`}
      >
        {value}
      </p>
    </article>
  );
}
function Loading() {
  return (
    <div className="panel animate-pulse text-muted-foreground">
      Đang tải dữ liệu…
    </div>
  );
}
function EmptyRow({ columns, text }: { columns: number; text: string }) {
  return (
    <TableRow>
      <TableCell
        colSpan={columns}
        className="py-10 text-center text-muted-foreground"
      >
        {text}
      </TableCell>
    </TableRow>
  );
}
