import { env } from 'cloudflare:workers';

type Method = 'GET' | 'POST' | 'PATCH' | 'DELETE';
type Options = { method?: Method; body?: unknown; prefer?: string };

function config() {
  const runtime = env as unknown as Record<string, string | undefined>;
  const url = runtime.SUPABASE_URL ?? process.env.SUPABASE_URL;
  const anonKey = runtime.SUPABASE_ANON_KEY ?? process.env.SUPABASE_ANON_KEY;
  const serviceKey =
    runtime.SUPABASE_SERVICE_ROLE_KEY ?? process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !anonKey || !serviceKey)
    throw new Error('SUPABASE_NOT_CONFIGURED');
  return { url: url.replace(/\/$/, ''), anonKey, serviceKey };
}

export async function supabaseAdmin<T>(
  path: string,
  options: Options = {},
): Promise<T> {
  const { url, serviceKey } = config();
  const response = await fetch(`${url}/rest/v1/${path}`, {
    method: options.method ?? 'GET',
    headers: {
      apikey: serviceKey,
      Authorization: `Bearer ${serviceKey}`,
      'Content-Type': 'application/json',
      Prefer: options.prefer ?? 'return=representation',
    },
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });
  if (!response.ok)
    throw new Error(`SUPABASE_${response.status}:${await response.text()}`);
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export async function supabaseRpc<T>(fn: string, body: unknown): Promise<T> {
  return supabaseAdmin<T>(`rpc/${fn}`, { method: 'POST', body });
}

export async function checkSupabaseConnection() {
  const { url, anonKey } = config();
  const response = await fetch(`${url}/rest/v1/`, {
    headers: { apikey: anonKey, Authorization: `Bearer ${anonKey}` },
  });
  return response.ok;
}
