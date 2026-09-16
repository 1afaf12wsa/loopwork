const nodemailer = require('nodemailer');

// Render's free tier wipes the local disk on restart, so data/waitlist.json is
// not a reliable record. Every new signup is emailed out as it arrives, and the
// inbox becomes the record that survives.
let transport = null;

function getTransport() {
  if (!process.env.SMTP_USER || !process.env.SMTP_PASS) return null;
  if (!transport) {
    const port = Number(process.env.SMTP_PORT || 465);
    transport = nodemailer.createTransport({
      host: process.env.SMTP_HOST || 'smtp.gmail.com',
      port,
      secure: port === 465,
      auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS.split(' ').join('') },
    });
  }
  return transport;
}

// Never throws: a failed notification must not break the visitor's signup.
async function notifySignup(entry) {
  const t = getTransport();
  if (!t) {
    console.warn('Signup not emailed: SMTP_USER / SMTP_PASS are not set');
    return false;
  }

  const handle = (entry.company || '').trim().replace(/^@/, '');
  const lines = [
    'Someone asked for a free sample chapter on loopwork.onrender.com.',
    '',
    `Handle: ${entry.company || '(not given)'}`,
    handle ? `Instagram: https://www.instagram.com/${encodeURIComponent(handle)}/` : null,
    `Email: ${entry.email}`,
    `When: ${entry.createdAt}`,
    '',
    'Reply to this email to answer them directly.',
  ].filter((line) => line !== null);

  try {
    await t.sendMail({
      from: `"Loopwork website" <${process.env.SMTP_USER}>`,
      to: process.env.NOTIFY_EMAIL || process.env.SMTP_USER,
      replyTo: entry.email,
      subject: `Free chapter request: ${entry.company || entry.email}`,
      text: lines.join('\n'),
    });
    return true;
  } catch (err) {
    console.error('Signup email failed:', err.message);
    return false;
  }
}

module.exports = { notifySignup };
