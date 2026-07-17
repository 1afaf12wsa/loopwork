const fs = require('fs');
const path = require('path');
const express = require('express');

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_FILE = path.join(__dirname, 'data', 'waitlist.json');
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function ensureDataFile() {
  const dir = path.dirname(DATA_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  if (!fs.existsSync(DATA_FILE)) fs.writeFileSync(DATA_FILE, '[]', 'utf8');
}
ensureDataFile();

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

app.listen(PORT, () => {
  console.log(`Loopwork landing page running at http://localhost:${PORT}`);
});
