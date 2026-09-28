import { z } from 'zod';
import { apiError, requireActor } from '@/lib/authz';
import { createAdminClient } from '@/lib/supabase/admin';
import { todayVietnam, unwrap } from '@/lib/http';
import { calculateFinancialSummary } from '@/lib/operations';
import { databaseIdSchema } from '@/lib/validation';

const schema = z.discriminatedUnion('action', [
  z.object({
    action: z.literal('create'),
    categoryId: databaseIdSchema,
    description: z.string().trim().min(2).max(1000),
    amount: z.coerce.number().positive(),
    expenseDate: z.string(),
    receiptNumber: z.string().trim().max(100).optional(),
    recurring: z.boolean().optional(),
  }),
  z.object({
    action: z.literal('createCategory'),
    name: z.string().trim().min(2).max(100),
  }),
  z.object({ action: z.literal('cancel'), expenseId: databaseIdSchema }),
]);

export async function GET(request: Request) {
  try {
    await requireActor(['manager']);
    const url = new URL(request.url);
    const today = todayVietnam();
    const from = url.searchParams.get('from') ?? `${today.slice(0, 7)}-01`;
    const to = url.searchParams.get('to') ?? today;
    const db = createAdminClient();
    const [expenses, categories, payments] = await Promise.all([
      db
        .from('expenses')
        .select(
          '*,expense_categories(name),profiles!expenses_created_by_fkey(full_name)',
        )
        .gte('expense_date', from)
        .lte('expense_date', to)
        .order('expense_date', { ascending: false }),
      db
        .from('expense_categories')
        .select('*')
        .eq('is_active', true)
        .order('name'),
      db
        .from('payments')
        .select('amount,status,paid_at')
        .gte('paid_at', `${from}T00:00:00+07:00`)
        .lte('paid_at', `${to}T23:59:59+07:00`),
    ]);
    const summary = calculateFinancialSummary(
      unwrap(payments),
      unwrap(expenses),
    );
    return Response.json({
      expenses: unwrap(expenses),
      categories: unwrap(categories),
      summary,
      from,
      to,
    });
  } catch (error) {
    return apiError(error);
  }
}

export async function POST(request: Request) {
  try {
    const actor = await requireActor(['manager']);
    const parsed = schema.safeParse(await request.json());
    if (!parsed.success)
      return Response.json(
        { error: 'INVALID_INPUT', issues: parsed.error.issues },
        { status: 400 },
      );
    const db = createAdminClient();
    const i = parsed.data;
    if (i.action === 'createCategory')
      return Response.json(
        unwrap(
          await db
            .from('expense_categories')
            .insert({ name: i.name })
            .select()
            .single(),
        ),
        { status: 201 },
      );
    if (i.action === 'cancel') {
      const row = unwrap(
        await db
          .from('expenses')
          .update({
            status: 'cancelled',
            cancelled_at: new Date().toISOString(),
            cancelled_by: actor.id,
          })
          .eq('id', i.expenseId)
          .eq('status', 'valid')
          .select()
          .single(),
      );
      unwrap(
        await db
          .from('audit_logs')
          .insert({
            actor_id: actor.id,
            action: 'cancel_expense',
            entity_type: 'expense',
            entity_id: i.expenseId,
          })
          .select()
          .single(),
      );
      return Response.json(row);
    }
    const row = unwrap(
      await db
        .from('expenses')
        .insert({
          category_id: i.categoryId,
          description: i.description,
          amount: i.amount,
          expense_date: i.expenseDate,
          receipt_number: i.receiptNumber || null,
          recurring: i.recurring ?? false,
          created_by: actor.id,
        })
        .select()
        .single(),
    );
    unwrap(
      await db
        .from('audit_logs')
        .insert({
          actor_id: actor.id,
          action: 'create_expense',
          entity_type: 'expense',
          entity_id: row.id,
          details: { amount: i.amount },
        })
        .select()
        .single(),
    );
    return Response.json(row, { status: 201 });
  } catch (error) {
    return apiError(error);
  }
}
