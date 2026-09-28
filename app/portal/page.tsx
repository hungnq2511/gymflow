import { redirect } from 'next/navigation';
import { currentActor } from '@/lib/authz';
import MemberPortal from '@/components/member-portal';
export default async function PortalPage() {
  const actor = await currentActor();
  if (!actor) redirect('/login');
  if (actor.mustChangePassword) redirect('/update-password');
  if (actor.role !== 'member') redirect('/admin');
  return <MemberPortal />;
}
