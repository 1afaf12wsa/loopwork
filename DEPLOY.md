# Deploying the site

The site runs on **Cloudflare Pages**. Static pages are served from Cloudflare's
edge, so there is no server to wake up and nothing to pay for. The signup form
runs as a Pages Function in `functions/api/waitlist.js`.

## Why not Render

Render runs one machine in one region. On the free plan it sleeps after about
15 minutes idle, and a visitor pays 30 to 60 seconds for the wake up. Pages has
no origin to wake, serves from the city nearest the visitor, and does not care
how much traffic a creator's launch post sends at once.

## One time setup in the Cloudflare dashboard

1. **Workers & Pages** → Create → Pages → Connect to Git → pick the `loopwork` repo.
2. Build settings:
   - Framework preset: **None**
   - Build command: **leave empty**
   - Build output directory: **`public`**
3. **Custom domains** → add `loopworkbooks.com` and `www.loopworkbooks.com`.
   Cloudflare updates the DNS records itself, so the old CNAMEs pointing at
   Render can go.
4. **Settings → Variables and secrets**, add:
   - `RESEND_API_KEY` — from resend.com, free tier
   - `NOTIFY_EMAIL` — where signups land (default loopworkinfos@gmail.com)
   - `NOTIFY_FROM` — e.g. `Loopwork website <hello@loopworkbooks.com>`, must be
     a domain verified in Resend
5. **Settings → Bindings → KV namespace**, bind a namespace as `SIGNUPS`.
   This is what remembers who already signed up.

Both the key and the binding are optional. Without them the form still returns
a clean success, it just cannot email or deduplicate, so do not leave them out.

## Why Resend rather than Gmail

Workers cannot open raw TCP connections, so SMTP is impossible. Email has to go
out over an HTTP API. Resend's free tier is 3,000 a month, far beyond what this
form will ever do.

## What stayed behind

`server.js` still holds the Twilio missed call webhooks from the earlier agent
product. They are not deployed anywhere. If a real phone number is ever pointed
at them again they need porting to Functions first, including the signature
check, which uses HMAC SHA1 and works fine with Web Crypto.

## Local preview

`npx wrangler pages dev public` runs the pages and the Functions together.
