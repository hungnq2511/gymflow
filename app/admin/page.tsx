import { redirect } from 'next/navigation';
import GymApp from '@/components/gym-app';
import { currentActor } from '@/lib/authz';

export default async function AdminPage() {
  const actor = await currentActor();
  if (!actor) redirect('/login');
  if (actor.mustChangePassword) redirect('/update-password');
  if (actor.role === 'member') redirect('/portal');
  return (
    <GymApp renderedAt={new Date().toISOString()} userName={actor.fullName} />
  );
}
