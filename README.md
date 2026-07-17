# Loopwork landing page

Landing page + waitlist for Loopwork, an AI automation agents product.

## Run it

```
npm install
npm start
```

Then open http://localhost:3000

## How the waitlist works

- `POST /api/waitlist` validates the email and appends it to `data/waitlist.json` (created automatically, git-ignored).
- Duplicate emails are detected and handled gracefully instead of double-counted.
- A hidden honeypot field filters out basic bots.
- There's no public "list all signups" endpoint by design, to avoid exposing emails. To see signups, open `data/waitlist.json` directly on the server, or write a small authenticated script when you need to export them (e.g. for a real ESP like Mailchimp/Loops/Resend).

## Before going live

- Swap the placeholder `hello@loopwork.ai` footer email for a real inbox.
- Point DNS / deploy (Vercel, Render, Railway, a small VPS — anything that runs Node works).
- Consider moving `data/waitlist.json` to a real database once volume grows past what a flat file comfortably handles.
- Optionally wire signups into an email service (Mailchimp, Loops, Resend, etc.) by calling their API inside `appendSignup` in `server.js`.

## Missed-call text-back agent

This is the actual product: a Twilio number that forwards to a business's real phone, and if nobody answers within 20 seconds, automatically texts the caller back and alerts the business owner.

### One-time setup (per deployment, not per customer)

1. Sign up at [twilio.com](https://www.twilio.com) (you do this, not Claude, it needs your payment details).
2. Get your **Account SID** and **Auth Token** from the Twilio Console dashboard.
3. Copy `.env.example` to `.env` and fill in those two values. On Render, set them instead under the service's **Environment** tab (no `.env` file needed there).

### Onboarding a new customer

1. In the Twilio Console, buy a phone number in the customer's area code.
2. Under that number's configuration, set **"A call comes in"** to a webhook pointing at `https://<your-deployed-url>/twilio/voice`, method POST.
3. Add an entry to `data/businesses.json` (create the file with `[]` if it doesn't exist yet):

```json
[
  {
    "twilioNumber": "+15551234567",
    "name": "Trent Valley Plumbing",
    "forwardTo": "+15559876543",
    "textBackMessage": "Hey, sorry we missed your call! Someone from Trent Valley Plumbing will call you back shortly."
  }
]
```

- `twilioNumber` — the number you just bought, in E.164 format (`+1...`).
- `forwardTo` — the business owner's real cell/office number that calls should ring.
- `textBackMessage` — optional; falls back to a generic message if omitted.

That's it — no redeploy needed, the server reads this file on every call.

### How it works

- `POST /twilio/voice` — incoming call webhook. Looks up the business by the Twilio number that was dialed, forwards the call with a 20-second timeout.
- `POST /twilio/voice/status` — fires after the dial attempt finishes. If it wasn't answered, sends two texts via the Twilio REST API: one to the caller (the text-back), one to the business owner (missed-call alert).
- Both webhook routes verify Twilio's request signature (skipped automatically if `TWILIO_AUTH_TOKEN` isn't set, e.g. in local dev).
