import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { AuthForm } from '@/components/auth-form';
import { currentActor } from '@/lib/authz';
import { PASSWORD_SETUP_COOKIE } from '@/lib/password-setup';

export default async function UpdatePasswordPage() {
  const actor = await currentActor();
  const cookieStore = await cookies();
  const setupUserId = cookieStore.get(PASSWORD_SETUP_COOKIE)?.value;

  // Never render a password form for an unrelated session (for example, an
  // administrator who opens an expired member invite in the same browser).
  if (
    !actor ||
    (!actor.mustChangePassword && setupUserId !== actor.authUserId)
  )
    redirect('/forgot-password?error=RECOVERY_SESSION_MISSING');

  return (
    <AuthForm mode="update" firstLogin={actor.mustChangePassword} />
  );
}
