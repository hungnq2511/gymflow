import { AuthForm } from '@/components/auth-form';
import { errorMessage } from '@/lib/error-messages';
export default async function ForgotPasswordPage({ searchParams }: { searchParams: Promise<{ error?: string }> }) {
  const { error } = await searchParams;
  return <AuthForm mode="forgot" initialMessage={error ? errorMessage(error) : ''} />;
}
