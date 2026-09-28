'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Dumbbell } from 'lucide-react';
import { createClient } from '@/lib/supabase/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AppToast } from '@/components/app-toast';
import { errorMessage, responseError } from '@/lib/error-messages';
import { apiFetch } from '@/lib/api-fetch';

export function AuthForm({
  mode = 'login',
  initialMessage = '',
  firstLogin = false,
}: {
  mode?: 'login' | 'forgot' | 'update';
  initialMessage?: string;
  firstLogin?: boolean;
}) {
  const router = useRouter();
  const [message, setMessage] = useState(initialMessage);
  const [loading, setLoading] = useState(false);
  const [sessionReady, setSessionReady] = useState(mode !== 'update');

  useEffect(() => {
    if (mode !== 'update') return;
    let active = true;
    const initializeInviteSession = async () => {
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (!active) return;
      setSessionReady(Boolean(session));
      if (!session) setMessage(errorMessage('RECOVERY_SESSION_MISSING'));
    };
    void initializeInviteSession();
    return () => {
      active = false;
    };
  }, [mode]);
  async function submit(formData: FormData) {
    try {
      setLoading(true);
      setMessage('');
      const emailValue = formData.get('email');
      const identifierValue = formData.get('identifier');
      const passwordValue = formData.get('password');
      const confirmPasswordValue = formData.get('confirmPassword');
      const email = typeof emailValue === 'string' ? emailValue.trim() : '';
      const identifier =
        typeof identifierValue === 'string' ? identifierValue.trim() : '';
      const password = typeof passwordValue === 'string' ? passwordValue : '';
      const confirmPassword =
        typeof confirmPasswordValue === 'string' ? confirmPasswordValue : '';
      if (mode === 'forgot') {
        const supabase = createClient();
        const { error } = await supabase.auth.resetPasswordForEmail(email, {
          redirectTo: `${location.origin}/auth/callback?next=/update-password`,
        });
        setMessage(
          error
            ? 'Không thể gửi email lúc này.'
            : 'Nếu email tồn tại, liên kết đặt lại mật khẩu đã được gửi.',
        );
      } else if (mode === 'update') {
        if (password !== confirmPassword) {
          setMessage(errorMessage('PASSWORD_MISMATCH'));
          return;
        }
        const response = await apiFetch('/api/auth/update-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ password }),
        });
        setMessage(
          response.ok
            ? 'Đổi mật khẩu thành công.'
            : await responseError(response, 'Không thể đổi mật khẩu.'),
        );
        if (response.ok)
          setTimeout(() => {
            router.replace('/');
            router.refresh();
          }, 800);
      } else {
        const supabase = createClient();
        const loginEmail = identifier.includes('@')
          ? identifier
          : `${identifier.toLowerCase()}@staff.gymflow.local`;
        const { error } = await supabase.auth.signInWithPassword({
          email: loginEmail,
          password,
        });
        if (error)
          setMessage(
            'Tên đăng nhập hoặc mật khẩu không đúng, hoặc tài khoản đã bị khóa.',
          );
        else {
          router.replace('/');
          router.refresh();
        }
      }
    } catch {
      setMessage('Không thể kết nối dịch vụ đăng nhập. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  }
  async function logout() {
    await createClient().auth.signOut();
    router.replace('/login');
    router.refresh();
  }
  return (
    <main className="app-shell surface-grid relative grid min-h-screen place-items-center overflow-hidden bg-background p-4 before:absolute before:left-1/2 before:top-[-12rem] before:size-[32rem] before:-translate-x-1/2 before:rounded-full before:bg-primary/10 before:blur-3xl">
      <section className="relative w-full max-w-md rounded-3xl border border-white/10 bg-card/90 p-7 shadow-[0_30px_100px_rgb(0_0_0/45%)] backdrop-blur-2xl sm:p-9">
        <div className="mb-8 flex items-center gap-3">
          <span className="grid size-12 place-items-center rounded-full bg-primary text-primary-foreground shadow-[0_0_32px_oklch(0.86_0.2_125/20%)]">
            <Dumbbell />
          </span>
          <div>
            <h1 className="text-xl font-black tracking-tight">GymFlow</h1>
            <p className="text-sm text-muted-foreground">
              Vận hành mạnh mẽ. Tăng trưởng bền vững.
            </p>
          </div>
        </div>
        <p className="eyebrow">CHÀO MỪNG TRỞ LẠI</p>
        <h2 className="text-3xl font-semibold tracking-tight">
          {mode === 'login'
            ? 'Đăng nhập'
            : mode === 'forgot'
              ? 'Quên mật khẩu'
              : firstLogin
                ? 'Đổi mật khẩu lần đầu'
                : 'Đặt mật khẩu mới'}
        </h2>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            void submit(new FormData(event.currentTarget));
          }}
          className="mt-6 space-y-4"
        >
          {mode === 'login' && (
            <div>
              <Label htmlFor="identifier">Tên đăng nhập hoặc email</Label>
              <Input
                id="identifier"
                name="identifier"
                className="mt-2"
                required
                autoComplete="username"
                autoCapitalize="none"
              />
            </div>
          )}
          {mode === 'forgot' && (
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                className="mt-2"
                required
                autoComplete="email"
              />
            </div>
          )}
          {mode !== 'forgot' && (
            <div>
              <Label htmlFor="password">Mật khẩu</Label>
              <Input
                id="password"
                name="password"
                type="password"
                minLength={8}
                maxLength={72}
                pattern={mode === 'update' ? '[^<>]*' : undefined}
                title={
                  mode === 'update'
                    ? 'Mật khẩu không được chứa thẻ HTML'
                    : undefined
                }
                className="mt-2"
                required
                autoComplete={
                  mode === 'login' ? 'current-password' : 'new-password'
                }
              />
            </div>
          )}
          {mode === 'update' && (
            <>
              {firstLogin && (
                <p className="rounded-xl border border-primary/15 bg-primary/8 p-3 text-sm text-muted-foreground">
                  Đây là lần đăng nhập đầu tiên. Hãy đặt mật khẩu mới để tiếp
                  tục sử dụng hệ thống.
                </p>
              )}
              <div>
                <Label htmlFor="confirmPassword">Xác nhận mật khẩu</Label>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  minLength={8}
                  maxLength={72}
                  pattern="[^<>]*"
                  title="Mật khẩu không được chứa thẻ HTML"
                  className="mt-2"
                  required
                  autoComplete="new-password"
                />
              </div>
            </>
          )}
          <Button
            id="auth-submit-button"
            type="submit"
            className="w-full"
            disabled={loading || !sessionReady}
          >
            {loading || (mode === 'update' && !sessionReady)
              ? 'Đang xác minh…'
              : mode === 'login'
                ? 'Đăng nhập'
                : mode === 'forgot'
                  ? 'Gửi liên kết'
                  : 'Lưu mật khẩu'}
          </Button>
          {mode === 'update' && firstLogin && (
            <Button
              id="auth-switch-account-button"
              type="button"
              variant="ghost"
              className="w-full"
              onClick={logout}
            >
              Đăng xuất và đổi tài khoản
            </Button>
          )}
        </form>
        {mode === 'login' && (
          <Link
            href="/forgot-password"
            className="mt-4 block text-center text-sm text-primary hover:underline"
          >
            Quên mật khẩu?
          </Link>
        )}
      </section>
      <AppToast message={message} />
    </main>
  );
}
