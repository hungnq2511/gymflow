import { AuthForm } from '@/components/auth-form';
import { currentActor } from '@/lib/authz';

export default async function UpdatePasswordPage() {
  const actor = await currentActor();
  return (
    <AuthForm mode="update" firstLogin={actor?.mustChangePassword ?? false} />
  );
}
