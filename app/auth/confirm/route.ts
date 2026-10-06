import type { EmailOtpType } from '@supabase/supabase-js';
import { createServerClient } from '@supabase/ssr';
import { NextResponse } from 'next/server';
import {
  PASSWORD_SETUP_COOKIE,
  passwordSetupCookieOptions,
} from '@/lib/password-setup';

export async function GET(request: Request) {
  const url = new URL(request.url);
  const tokenHash = url.searchParams.get('token_hash');
  const type = url.searchParams.get('type') as EmailOtpType | null;
  const requestedNext = url.searchParams.get('next');
  const next =
    requestedNext?.startsWith('/') && !requestedNext.startsWith('//')
      ? requestedNext
      : '/update-password';
  if (tokenHash && (type === 'invite' || type === 'recovery')) {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
    if (!supabaseUrl || !supabaseKey)
      return NextResponse.redirect(
        new URL('/forgot-password?error=SUPABASE_NOT_CONFIGURED', url.origin),
      );

    const response = NextResponse.redirect(new URL(next, url.origin));
    // The invite must be verified without inheriting the administrator session
    // that may already exist in this browser. Only the invited user's new
    // session is written to the redirect response.
    const supabase = createServerClient(supabaseUrl, supabaseKey, {
      cookies: {
        getAll: () => [],
        setAll(items) {
          items.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options),
          );
        },
      },
    });
    const { data, error } = await supabase.auth.verifyOtp({
      token_hash: tokenHash,
      type,
    });
    if (!error && data.user) {
      response.cookies.set(
        PASSWORD_SETUP_COOKIE,
        data.user.id,
        passwordSetupCookieOptions(url.protocol === 'https:'),
      );
      return response;
    }
  }
  const response = NextResponse.redirect(
    new URL('/forgot-password?error=RECOVERY_LINK_INVALID', url.origin),
  );
  response.cookies.delete(PASSWORD_SETUP_COOKIE);
  return response;
}
