'use client';

import { useCallback, useEffect, useState } from 'react';
import Image from 'next/image';
import QRCode from 'qrcode';
import {
  CalendarClock,
  Dumbbell,
  History,
  LogOut,
  ReceiptText,
  UserRound,
} from 'lucide-react';
import { createClient } from '@/lib/supabase/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { AppToast } from '@/components/app-toast';
import { apiFetch } from '@/lib/api-fetch';

type PortalData = {
  actor: { fullName: string };
  member: {
    full_name: string;
    member_code: string;
    phone: string;
    address: string | null;
    emergency_contact: string | null;
    qr_token: string;
    subscriptions: Array<{
      id: string;
      plan_name_snapshot: string | null;
      start_date: string;
      end_date: string;
      remaining_visits: number | null;
      status: string;
      membership_plans?: { name: string } | null;
    }>;
    payments: Array<{
      id: string;
      receipt_code: string;
      amount: number;
      method: string;
      status: string;
      paid_at: string;
      subscriptions?: { plan_name_snapshot: string } | null;
    }>;
    check_ins: Array<{
      id: string;
      checked_in_at: string;
      subscriptions?: { plan_name_snapshot: string } | null;
    }>;
  };
};
const money = (n: number) =>
  new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    maximumFractionDigits: 0,
  }).format(n);
export default function MemberPortal() {
  const [data, setData] = useState<PortalData | null>(null);
  const [error, setError] = useState('');
  const [qr, setQr] = useState('');
  const load = useCallback(async () => {
    const r = await apiFetch('/api/portal');
    if (!r.ok) {
      setError('Không thể tải hồ sơ.');
      return;
    }
    const d = (await r.json()) as PortalData;
    setData(d);
    setQr(
      await QRCode.toDataURL(d.member.qr_token, {
        width: 260,
        margin: 2,
        color: { dark: '#111812', light: '#dafa74' },
      }),
    );
  }, []);
  useEffect(() => {
    // oxlint-disable-next-line react/react-compiler -- initial API hydration
    void load();
  }, [load]);
  async function save(fd: FormData) {
    const r = await apiFetch('/api/portal', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        phone: fd.get('phone'),
        address: fd.get('address'),
        emergencyContact: fd.get('emergencyContact'),
      }),
    });
    setError(r.ok ? 'Đã cập nhật hồ sơ.' : 'Dữ liệu chưa hợp lệ.');
    if (r.ok) await load();
  }
  async function logout() {
    await createClient().auth.signOut();
    location.href = '/login';
  }
  if (error && !data) return <p className="p-8">{error}</p>;
  if (!data) return <p className="p-8">Đang tải hồ sơ…</p>;
  const current = data.member.subscriptions.find((s) =>
    ['active', 'frozen'].includes(s.status),
  );
  const next = data.member.subscriptions.find((s) => s.status === 'scheduled');
  return (
    <main className="app-shell surface-grid min-h-screen bg-background">
      <header className="sticky top-0 z-20 border-b border-white/8 bg-background/75 text-white backdrop-blur-2xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between p-5">
          <div className="flex items-center gap-3">
            <span className="grid size-11 place-items-center rounded-full bg-primary text-primary-foreground">
              <Dumbbell />
            </span>
            <div>
              <b className="text-lg tracking-tight">GymFlow</b>
              <p className="text-xs text-white/45">Cổng hội viên</p>
            </div>
          </div>
          <Button
            id="member-logout-button"
            type="button"
            variant="outline"
            onClick={logout}
          >
            <LogOut />
            Đăng xuất
          </Button>
        </div>
      </header>
      <div className="mx-auto max-w-7xl p-4 py-8 md:p-8">
        <div className="mb-8">
          <p className="eyebrow">HỒ SƠ CỦA BẠN</p>
          <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
            Chào {data.member.full_name.split(' ').at(-1)}, hôm nay cùng bứt
            phá.
          </h1>
        </div>
        <div className="grid gap-6 lg:grid-cols-[.85fr_1.5fr]">
          <section className="space-y-6">
            <article className="panel text-center">
              <div className="mx-auto grid size-20 place-items-center rounded-full border border-primary/20 bg-primary/10">
                <UserRound className="size-9 text-primary" />
              </div>
              <h2 className="mt-4 text-2xl font-semibold">
                {data.member.full_name}
              </h2>
              <p className="text-muted-foreground">{data.member.member_code}</p>
              {qr && (
                <div className="mx-auto mt-6 w-fit rounded-2xl bg-primary p-3 shadow-[0_0_45px_oklch(0.86_0.2_125/13%)]">
                  <Image
                    src={qr}
                    width={220}
                    height={220}
                    unoptimized
                    alt="Mã QR hội viên"
                    className="rounded-xl"
                  />
                </div>
              )}
              <p className="mt-4 text-xs text-muted-foreground">
                Trình mã này tại quầy để check-in
              </p>
            </article>
            <article className="panel">
              <h2 className="panel-title">Thông tin liên hệ</h2>
              <form action={save} className="mt-5 space-y-4">
                <div>
                  <Label htmlFor="profile-phone">Số điện thoại</Label>
                  <Input
                    id="profile-phone"
                    name="phone"
                    type="tel"
                    inputMode="numeric"
                    autoComplete="tel"
                    className="mt-2"
                    defaultValue={data.member.phone}
                    pattern="0[0-9]{9}"
                    minLength={10}
                    maxLength={10}
                    title="Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="profile-address">Địa chỉ</Label>
                  <Input
                    id="profile-address"
                    name="address"
                    className="mt-2"
                    defaultValue={data.member.address ?? ''}
                    maxLength={500}
                    pattern="[^<>]*"
                    title="Địa chỉ không được chứa thẻ HTML"
                  />
                </div>
                <div>
                  <Label htmlFor="profile-emergency">Liên hệ khẩn cấp</Label>
                  <Input
                    id="profile-emergency"
                    name="emergencyContact"
                    className="mt-2"
                    defaultValue={data.member.emergency_contact ?? ''}
                    maxLength={250}
                    pattern="[^<>]*"
                    title="Liên hệ khẩn cấp không được chứa thẻ HTML"
                  />
                </div>
                <Button
                  id="member-save-profile-button"
                  type="submit"
                  className="w-full"
                >
                  Lưu thay đổi
                </Button>
              </form>
            </article>
          </section>
          <section className="space-y-6">
            <article className="panel overflow-hidden">
              <div className="flex items-center justify-between">
                <h2 className="panel-title">Gói đang sử dụng</h2>
                {current && (
                  <Badge
                    className="border-primary/20 bg-primary/10 text-primary"
                    variant="outline"
                  >
                    {current.status === 'frozen'
                      ? 'Đang đóng băng'
                      : '● Đang hoạt động'}
                  </Badge>
                )}
              </div>
              {current ? (
                <div className="mt-6 grid gap-4 sm:grid-cols-3">
                  <div className="rounded-2xl bg-white/4 p-4">
                    <p className="text-xs text-muted-foreground">Tên gói</p>
                    <b className="mt-2 block text-lg">
                      {current.plan_name_snapshot ??
                        current.membership_plans?.name}
                    </b>
                  </div>
                  <div className="rounded-2xl bg-white/4 p-4">
                    <p className="text-xs text-muted-foreground">Hết hạn</p>
                    <b className="mt-2 block text-lg">{current.end_date}</b>
                  </div>
                  <div className="rounded-2xl bg-white/4 p-4">
                    <p className="text-xs text-muted-foreground">
                      Lượt còn lại
                    </p>
                    <b className="mt-2 block text-lg text-primary">
                      {current.remaining_visits ?? 'Không giới hạn'}
                    </b>
                  </div>
                </div>
              ) : (
                <p className="mt-4 text-muted-foreground">
                  Bạn chưa có gói đang hoạt động.
                </p>
              )}
              {next && (
                <p className="mt-5 rounded-xl bg-primary/8 p-3 text-sm text-primary">
                  Gói kế tiếp bắt đầu ngày <b>{next.start_date}</b>.
                </p>
              )}
            </article>
            <article className="panel">
              <h2 className="panel-title flex items-center gap-2">
                <History className="text-primary" />
                Check-in gần đây
              </h2>
              <div className="mt-4 divide-y divide-white/8">
                {data.member.check_ins.slice(0, 10).map((x) => (
                  <div
                    key={x.id}
                    className="flex justify-between gap-4 py-4 text-sm"
                  >
                    <span>
                      {x.subscriptions?.plan_name_snapshot ?? 'Gói tập'}
                    </span>
                    <time className="text-muted-foreground">
                      {new Date(x.checked_in_at).toLocaleString('vi-VN')}
                    </time>
                  </div>
                ))}
                {!data.member.check_ins.length && (
                  <p className="py-5 text-muted-foreground">Chưa có lịch sử.</p>
                )}
              </div>
            </article>
            <div className="grid gap-6 xl:grid-cols-2">
              <article className="panel">
                <h2 className="panel-title flex items-center gap-2">
                  <ReceiptText className="text-primary" />
                  Thanh toán
                </h2>
                <div className="mt-4 divide-y divide-white/8">
                  {data.member.payments.map((x) => (
                    <div
                      key={x.id}
                      className="flex items-center justify-between gap-3 py-4"
                    >
                      <div>
                        <b className="text-sm">{x.receipt_code}</b>
                        <p className="text-xs text-muted-foreground">
                          {new Date(x.paid_at).toLocaleDateString('vi-VN')}
                        </p>
                      </div>
                      <div className="text-right">
                        <b>{money(Number(x.amount))}</b>
                        <p className="text-xs text-muted-foreground">
                          {x.status === 'valid' ? 'Hợp lệ' : 'Đã hủy'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </article>
              <article className="panel">
                <h2 className="panel-title flex items-center gap-2">
                  <CalendarClock className="text-primary" />
                  Lịch sử gói
                </h2>
                <div className="mt-4 divide-y divide-white/8">
                  {data.member.subscriptions.map((x) => (
                    <div key={x.id} className="py-4 text-sm">
                      <b>{x.plan_name_snapshot ?? x.membership_plans?.name}</b>
                      <p className="mt-1 text-muted-foreground">
                        {x.start_date} → {x.end_date}
                      </p>
                    </div>
                  ))}
                </div>
              </article>
            </div>
          </section>
        </div>
      </div>
      <AppToast message={error} />
    </main>
  );
}
