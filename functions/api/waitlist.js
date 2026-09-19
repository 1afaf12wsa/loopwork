// Cloudflare Pages Function. Replaces the Express /api/waitlist route.
//
// Workers cannot open raw TCP, so there is no SMTP here. Email goes out over
// Resend's HTTP API instead. Both the store and the email are optional: if a
// binding or key is missing the visitor still gets a clean success, because
// losing their signup silently is bad but showing them an error is worse.

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });

async function sendNotification(env, entry) {
  if (!env.RESEND_API_KEY) {
    console.warn('Signup not emailed: RESEND_API_KEY is not set');
    return false;
  }

  const handle = (entry.company || '').trim().replace(/^@/, '');
  const lines = [
    'Someone asked for a free sample chapter on loopworkbooks.com.',
    '',
    `Handle: ${entry.company || '(not given)'}`,
    handle ? `Instagram: https://www.instagram.com/${encodeURIComponent(handle)}/` : null,
    `Email: ${entry.email}`,
    `When: ${entry.createdAt}`,
    '',
    'Reply to this email to answer them directly.',
  ].filter((line) => line !== null);

  try {
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: env.NOTIFY_FROM || 'Loopwork website <hello@loopworkbooks.com>',
        to: [env.NOTIFY_EMAIL || 'loopworkinfos@gmail.com'],
        reply_to: entry.email,
        subject: `Free chapter request: ${entry.company || entry.email}`,
        text: lines.join('\n'),
      }),
    });
    if (!res.ok) {
      console.error('Signup email failed:', res.status, await res.text());
      return false;
    }
    return true;
  } catch (err) {
    console.error('Signup email failed:', err.message);
    return false;
  }
}

export async function onRequestPost({ request, env }) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ ok: false, error: 'Something went wrong. Please try again.' }, 400);
  }

  const { email, company, website } = body || {};

  // Honeypot: hidden via CSS, so only a bot filling every field trips it.
  // Answer as if it worked, so the bot has nothing to learn.
  if (website) return json({ ok: true, position: 0 });

  if (typeof email !== 'string' || !EMAIL_RE.test(email.trim())) {
    return json({ ok: false, error: 'Please enter a valid email address.' }, 400);
  }

  const entry = {
    email: email.trim().toLowerCase(),
    company: typeof company === 'string' ? company.trim().slice(0, 200) : '',
    createdAt: new Date().toISOString(),
  };

  let duplicate = false;
  if (env.SIGNUPS) {
    try {
      const key = `signup:${entry.email}`;
      duplicate = (await env.SIGNUPS.get(key)) !== null;
      if (!duplicate) await env.SIGNUPS.put(key, JSON.stringify(entry));
    } catch (err) {
      console.error('Signup store failed:', err.message);
    }
  }

  if (!duplicate) {
    console.log(`New signup: ${entry.email} ${entry.company}`);
    await sendNotification(env, entry);
  }

  return json({ ok: true, duplicate });
}

// Anything other than POST on this path is a mistake, not a visitor.
export const onRequest = async (context) =>
  context.request.method === 'POST'
    ? onRequestPost(context)
    : new Response('Method not allowed', { status: 405 });
