import { redirect } from 'next/navigation';
import { currentActor } from '@/lib/authz';

export default async function Home() {
  const actor = await currentActor();
  if (!actor) redirect('/login');
  if (actor.mustChangePassword) redirect('/update-password');
  redirect(actor.role === 'member' ? '/portal' : '/admin');
}
