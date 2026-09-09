import { checkSupabaseConnection } from '@/lib/supabase/admin';
export async function GET() {
  try {
    return Response.json({
      database: (await checkSupabaseConnection()) ? 'connected' : 'unavailable',
    });
  } catch {
    return Response.json({ database: 'not_configured' }, { status: 503 });
  }
}
