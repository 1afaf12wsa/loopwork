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
