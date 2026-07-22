require('dotenv').config();
const fs = require('fs');
const path = require('path');
const express = require('express');
const twilio = require('twilio');

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_FILE = path.join(__dirname, 'data', 'waitlist.json');
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const twilioClient = process.env.TWILIO_ACCOUNT_SID
  ? twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN)
  : null;

function ensureDataFile(file) {
  const dir = path.dirname(file);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  if (!fs.existsSync(file)) fs.writeFileSync(file, '[]', 'utf8');
}
ensureDataFile(DATA_FILE);

// Customer config lives in an env var (BUSINESSES_JSON), not a file, because
// Render's free tier wipes the local disk on every restart/redeploy — an
// env var is the one thing that reliably survives that.
function getBusinesses() {
  try {
    return JSON.parse(process.env.BUSINESSES_JSON || '[]');
  } catch (err) {
    console.error('BUSINESSES_JSON is not valid JSON:', err);
    return [];
  }
}

// Looks up which customer a Twilio number belongs to, so the same server
// can run the missed-call agent for multiple businesses at once.
function getBusinessByTwilioNumber(twilioNumber) {
  return getBusinesses().find((b) => b.twilioNumber === twilioNumber);
}

// Signups are appended through a promise chain so concurrent requests
// can't interleave reads/writes of the JSON file and clobber each other.
let writeChain = Promise.resolve();
function appendSignup(entry) {
  writeChain = writeChain.then(() => {
    const list = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
    const existingIndex = list.findIndex((e) => e.email === entry.email);
    if (existingIndex !== -1) {
      return { duplicate: true, position: existingIndex + 1 };
    }
    list.push(entry);
    fs.writeFileSync(DATA_FILE, JSON.stringify(list, null, 2), 'utf8');
    return { duplicate: false, position: list.length };
  });
  return writeChain;
}

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.post('/api/waitlist', async (req, res) => {
  try {
    const { email, company, website } = req.body || {};

    // Honeypot field: real users never fill this in (it's hidden via CSS).
    // Bots that blindly fill every form field will trip it.
    if (website) {
      return res.json({ ok: true, position: 0 });
    }

    if (typeof email !== 'string' || !EMAIL_RE.test(email.trim())) {
      return res.status(400).json({ ok: false, error: 'Please enter a valid email address.' });
    }

    const entry = {
      email: email.trim().toLowerCase(),
      company: typeof company === 'string' ? company.trim().slice(0, 200) : '',
      createdAt: new Date().toISOString(),
    };

    const result = await appendSignup(entry);
    res.json({ ok: true, position: result.position, duplicate: result.duplicate });
  } catch (err) {
    console.error('waitlist signup failed:', err);
    res.status(500).json({ ok: false, error: 'Something went wrong. Please try again.' });
  }
});

// Twilio posts webhooks as form-encoded data, and signs each request so we
// can verify it actually came from Twilio and not a forged POST.
const twilioForm = express.urlencoded({ extended: false });
const validateTwilioRequest = twilio.webhook({ validate: Boolean(process.env.TWILIO_AUTH_TOKEN) });

// Step 1: a call comes in to a business's Twilio number. Forward it to the
// business's real phone. If nobody picks up within 20s, Twilio calls back
// into /twilio/voice/status below with the outcome.
app.post('/twilio/voice', twilioForm, validateTwilioRequest, (req, res) => {
  const twiml = new twilio.twiml.VoiceResponse();
  const business = getBusinessByTwilioNumber(req.body.To);

  if (!business) {
    twiml.say('This number is not set up yet. Goodbye.');
    return res.type('text/xml').send(twiml.toString());
  }

  twiml.dial({ timeout: 20, action: '/twilio/voice/status', method: 'POST' }, business.forwardTo);
  res.type('text/xml').send(twiml.toString());
});

// Step 2: the dial finished. If it wasn't answered, text the caller back
// immediately and let the business owner know they missed a lead.
// Voice TwiML has no verb for sending SMS (that's Messaging-webhook-only),
// so both texts go out through the REST API instead, and the voice
// response itself just ends the call quietly.
app.post('/twilio/voice/status', twilioForm, validateTwilioRequest, async (req, res) => {
  const twiml = new twilio.twiml.VoiceResponse();
  const business = getBusinessByTwilioNumber(req.body.To);
  const wasAnswered = req.body.DialCallStatus === 'completed';

  if (business && !wasAnswered && twilioClient) {
    const message =
      business.textBackMessage ||
      `Hey, sorry we missed your call! Someone from ${business.name} will get back to you shortly.`;
    try {
      await twilioClient.messages.create({ to: req.body.From, from: business.twilioNumber, body: message });
      await twilioClient.messages.create({
        to: business.forwardTo,
        from: business.twilioNumber,
        body: `Missed call from ${req.body.From}. We texted them back automatically.`,
      });
    } catch (err) {
      console.error('failed to send missed-call texts:', err);
    }
  }

  res.type('text/xml').send(twiml.toString());
});

app.listen(PORT, () => {
  console.log(`Loopwork landing page running at http://localhost:${PORT}`);
});
