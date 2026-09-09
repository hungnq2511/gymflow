import { apiError, requireActor } from '@/lib/authz';
import { supabaseAdmin } from '@/lib/supabase/admin';
export async function GET() {
  try {
    await requireActor(['manager', 'staff']);
    return Response.json(
      await supabaseAdmin('members?select=*&order=created_at.desc'),
    );
  } catch (e) {
    return apiError(e);
  }
}
export async function POST(request: Request) {
  try {
    await requireActor(['manager', 'staff']);
    const input = (await request.json()) as {
      fullName?: string;
      phone?: string;
      email?: string;
    };
    if (!input.fullName?.trim() || !input.phone?.trim())
      return Response.json({ error: 'INVALID_INPUT' }, { status: 400 });
    const id = crypto.randomUUID(),
      code = `GF-${Date.now().toString().slice(-6)}`;
    const rows = await supabaseAdmin('members', {
      method: 'POST',
      body: {
        id,
        member_code: code,
        qr_token: crypto.randomUUID(),
        full_name: input.fullName.trim(),
        phone: input.phone.trim(),
        email: input.email?.trim() || null,
        status: 'active',
      },
    });
    return Response.json(rows, { status: 201 });
  } catch (e) {
    return apiError(e);
  }
}
