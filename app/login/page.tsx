import { redirect } from 'next/navigation';
import { currentActor } from '@/lib/authz';
import { AuthForm } from '@/components/auth-form';

export default async function LoginPage() {
  const actor = await currentActor();
  if (actor) redirect(actor.mustChangePassword ? '/update-password' : '/');
  return <AuthForm />;
}
