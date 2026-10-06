import { NextResponse } from 'next/server';
import {
  PASSWORD_SETUP_COOKIE,
  passwordSetupCookieOptions,
} from '@/lib/password-setup';
import { createClient } from '@/lib/supabase/server';

export async function GET(request: Request) {
  const url = new URL(request.url);
  const code = url.searchParams.get('code');
  const requestedNext = url.searchParams.get('next');
  const next =
    requestedNext?.startsWith('/') && !requestedNext.startsWith('//')
      ? requestedNext
      : '/';
  if (!code) {
    const response = NextResponse.redirect(
      new URL('/forgot-password?error=RECOVERY_LINK_INVALID', url.origin),
    );
    response.cookies.delete(PASSWORD_SETUP_COOKIE);
    return response;
  }
  // PKCE recovery needs the verifier cookie created when the reset email was
  // requested, so this flow intentionally uses the request's cookie store.
  const supabase = await createClient();
  const { data, error } = await supabase.auth.exchangeCodeForSession(code);
  if (error || !data.user) {
    const invalidResponse = NextResponse.redirect(
      new URL('/forgot-password?error=RECOVERY_LINK_INVALID', url.origin),
    );
    invalidResponse.cookies.delete(PASSWORD_SETUP_COOKIE);
    return invalidResponse;
  }
  const response = NextResponse.redirect(new URL(next, url.origin));
  response.cookies.set(
    PASSWORD_SETUP_COOKIE,
    data.user.id,
    passwordSetupCookieOptions(url.protocol === 'https:'),
  );
  return response;
}
