export const PASSWORD_SETUP_COOKIE = 'gymflow-password-setup-user';

export const passwordSetupCookieOptions = (secure: boolean) => ({
  httpOnly: true,
  sameSite: 'lax' as const,
  secure,
  path: '/',
  maxAge: 15 * 60,
});
