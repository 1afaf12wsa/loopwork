// Each form posts to /api/waitlist. The handle field rides along as `company`
// so the server keeps storing entries in exactly the shape it always has.
function setupApplyForm(form) {
  const emailInput = form.querySelector('input[type="email"]');
  const handleInput = form.querySelector('input[name="handle"]');
  const button = form.querySelector('button');
  const buttonLabel = button.querySelector('.btn-label');
  const note = form.nextElementSibling;
  const honeypot = form.querySelector('input[name="hp_note"]');
  const originalLabel = buttonLabel.textContent;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim();

    note.classList.remove('is-error', 'is-success');
    button.disabled = true;
    buttonLabel.textContent = 'Sending…';

    try {
      const res = await fetch('/api/waitlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          company: handleInput ? handleInput.value.trim() : '',
          website: honeypot.value,
        }),
      });
      const data = await res.json();

      if (!res.ok || !data.ok) {
        throw new Error(data.error || 'Something went wrong.');
      }

      emailInput.value = '';
      if (handleInput) handleInput.value = '';
      buttonLabel.textContent = 'Got it';
      note.textContent = data.duplicate
        ? "You're already on our list, we'll be in touch shortly."
        : "Thanks. We'll read your posts and come back with a book idea and a free chapter.";
      note.classList.add('is-success');
    } catch (err) {
      button.disabled = false;
      buttonLabel.textContent = originalLabel;
      note.textContent = err.message || 'Something went wrong. Please try again.';
      note.classList.add('is-error');
    }
  });
}

document.querySelectorAll('.apply-form').forEach(setupApplyForm);

// Sample pages open in a lightbox on the page instead of a new tab.
// Arrows / swipe move between pages; Esc, the X or a click outside closes it.
(function setupLightbox() {
  const links = [...document.querySelectorAll('.inside-pages a')];
  if (!links.length || typeof HTMLDialogElement !== 'function') return;

  const box = document.createElement('dialog');
  box.className = 'lightbox';
  box.innerHTML =
    '<figure><img alt=""><figcaption></figcaption></figure>' +
    '<button class="lb-close" type="button" aria-label="Close">&times;</button>' +
    '<button class="lb-prev" type="button" aria-label="Previous page">&#8249;</button>' +
    '<button class="lb-next" type="button" aria-label="Next page">&#8250;</button>';
  document.body.appendChild(box);
  const img = box.querySelector('img');
  const count = box.querySelector('figcaption');
  let i = 0;

  function show(n) {
    i = (n + links.length) % links.length;
    const thumb = links[i].querySelector('img');
    img.src = links[i].href;
    img.alt = thumb ? thumb.alt : '';
    count.textContent = (i + 1) + ' / ' + links.length;
  }

  links.forEach((a, n) => a.addEventListener('click', (e) => {
    e.preventDefault();
    show(n);
    box.showModal();
  }));
  box.querySelector('.lb-close').addEventListener('click', () => box.close());
  box.querySelector('.lb-prev').addEventListener('click', () => show(i - 1));
  box.querySelector('.lb-next').addEventListener('click', () => show(i + 1));
  box.addEventListener('click', (e) => { if (e.target === box) box.close(); });
  box.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') show(i - 1);
    if (e.key === 'ArrowRight') show(i + 1);
  });
  let x0 = null;
  box.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; }, { passive: true });
  box.addEventListener('touchend', (e) => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 40) show(dx < 0 ? i + 1 : i - 1);
    x0 = null;
  });
})();

// Earnings example, worked out at a real rate: Bridget's reel got 2,102 views and 6 people bought her book.
// Earnings use the deal note's ratios: $17.80 of $19 with the one-time fee, $8.90 on 50/50 (store fees about 6%).
// The one-time fee is $199 for anyone starting by 31 Dec 2026, then $290. It is shown as a fee, not subtracted.
(function setupEarn() {
  const f = document.getElementById('earn-f');
  const c = document.getElementById('earn-c');
  const customBox = c ? c.closest('.earn-custom') : null;
  const p = document.getElementById('earn-p');
  const pc = document.getElementById('earn-pc');
  const priceBox = pc ? pc.closest('.earn-custom') : null;
  const rows = document.querySelectorAll('#earn-rows tr');
  const even = document.getElementById('earn-even');
  if (!f || !p || !rows.length) return;
  const RATE = 6 / 2102;
  const FEE = Date.now() < Date.parse('2027-01-01T12:00:00Z') ? 199 : 290;
  const OWN = 17.80 / 19, SPLIT = 8.90 / 19;
  document.querySelectorAll('.earn-fee').forEach((el) => { el.textContent = '$' + FEE; });
  const money = (n) => '$' + Math.round(n).toLocaleString('en-US');
  const priceText = (n) => '$' + (Number.isInteger(n) ? n : n.toFixed(2));
  const blank = (msg) => {
    rows.forEach((tr) => tr.querySelectorAll('td').forEach((td) => { td.textContent = '-'; }));
    if (even) even.textContent = msg;
  };
  function render() {
    const custom = f.value === 'custom';
    if (customBox) customBox.hidden = !custom;
    const customPrice = p.value === 'custom';
    if (priceBox) priceBox.hidden = !customPrice;
    const views = custom ? parseInt((c.value || '').replace(/[^0-9]/g, ''), 10) : parseInt(f.value, 10);
    if (!views || views < 1) return blank('Enter your follower count to see the math.');
    const price = customPrice ? parseFloat(pc.value) : parseFloat(p.value);
    if (!price || price <= 0) return blank('Enter your book price to see the math.');
    rows.forEach((tr) => {
      const sales = Math.round(views * parseInt(tr.dataset.n, 10) * RATE);
      const td = tr.querySelectorAll('td');
      td[0].textContent = sales.toLocaleString('en-US');
      const own = sales * price * OWN - FEE;
      const split = sales * price * SPLIT;
      // Below the break-even the 50/50 deal pays more, so say that instead of showing a fee-less figure.
      const splitWins = own <= split;
      td[1].textContent = money(split);
      td[1].className = splitWins ? 'win' : '';
      td[2].innerHTML = splitWins ? '50/50 pays more here' : money(own) + '<small>after the $' + FEE + '</small>';
      td[2].className = splitWins ? 'tip' : 'win';
    });
    const n = Math.ceil(FEE / (price * (OWN - SPLIT)));
    if (even) even.textContent = 'At ' + priceText(price) + ' a book, the $' + FEE + ' option comes out ahead from ' + n + (n === 1 ? ' sale.' : ' sales.');
  }
  f.addEventListener('change', render);
  if (c) c.addEventListener('input', () => {
    const digits = c.value.replace(/[^0-9]/g, '').slice(0, 9);
    const num = digits ? Math.min(Number(digits), 10000000) : 0;
    c.value = num ? num.toLocaleString('en-US') : '';
    render();
  });
  f.addEventListener('change', () => { if (f.value === 'custom' && c) setTimeout(() => c.focus(), 0); });
  p.addEventListener('change', () => { render(); if (p.value === 'custom' && pc) setTimeout(() => pc.focus(), 0); });
  if (pc) pc.addEventListener('input', () => {
    let v = pc.value.replace(/[^0-9.]/g, '');
    const dot = v.indexOf('.');
    if (dot !== -1) v = v.slice(0, dot + 1) + v.slice(dot + 1).replace(/\./g, '').slice(0, 2);
    if (parseFloat(v) > 999) v = '999';
    pc.value = v;
    render();
  });
  render();
})();

// Phone header button: while the hero form is on screen (or above), go to it instead of the form at the bottom.
(function headerCta() {
  const cta = document.querySelector('.nav .btn-small, header .btn-small');
  const hero = document.querySelector('.hero .apply-form');
  if (!cta || !hero) return;
  cta.addEventListener('click', (e) => {
    if (hero.getBoundingClientRect().bottom > 0) {
      e.preventDefault();
      hero.scrollIntoView({ behavior: 'smooth', block: 'center' });
      const first = hero.querySelector('input[name="handle"]');
      if (first) setTimeout(() => first.focus({ preventScroll: true }), 400);
    }
  });
})();
