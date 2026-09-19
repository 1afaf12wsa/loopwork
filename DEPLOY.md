# Deploying the site

The site runs as a **Cloudflare Worker with static assets**. Everything in
`public/` is served from Cloudflare's edge without running any code. The worker
in `worker.js` wakes only for the signup form, so there is nothing to pay for
and nothing to wake up.

## Why not Render

Render runs one machine in one region. On the free plan it sleeps after about
15 minutes idle, and a visitor pays 30 to 60 seconds for the wake up. Cloudflare
has no origin to wake, serves from the city nearest the visitor, and does not
care how much traffic a creator's launch post sends at once.

## One time setup in the Cloudflare dashboard

1. **Workers & Pages** → **Create** → **Import a repository** → pick the
   `loopwork` repo.
2. Project name `loopwork`. Build command: leave **empty**. Deploy command:
   `npx wrangler deploy`. Everything else is read from `wrangler.jsonc`.
3. **Deploy**, then open the `.workers.dev` URL it gives you and check the site
   looks right. Do not touch the domain yet.
4. **Settings → Variables and Secrets** → add a secret named `RESEND_API_KEY`,
   from resend.com. Redeploy afterwards: secrets only reach new deployments.
5. **Settings → Domains & Routes** → add `loopworkbooks.com` and
   `www.loopworkbooks.com`. This is the moment traffic leaves Render.

`NOTIFY_EMAIL` and `NOTIFY_FROM` live in `wrangler.jsonc` rather than the
dashboard, because a deploy overwrites plain variables set in the dashboard.
Secrets are left alone by deploys, which is why the API key is one.

### Optional: duplicate detection

Create a KV namespace, add its id to `wrangler.jsonc` under `kv_namespaces`,
and redeploy. Without it the form still works, it just cannot tell a repeat
signup from a new one.

## Why Resend rather than Gmail

Workers cannot open raw TCP connections, so SMTP is impossible. Email has to go
out over an HTTP API. Resend's free tier is 3,000 a month, far beyond what this
form will ever do.

## What stayed behind

`server.js` still holds the Twilio missed call webhooks from the earlier agent
product, and is no longer deployed anywhere. If a real phone number is ever
pointed at them again they need porting into `worker.js` first, including the
signature check, which uses HMAC SHA1 and works fine with Web Crypto.

## Local preview

`npx wrangler dev` runs the worker and the static assets together.
