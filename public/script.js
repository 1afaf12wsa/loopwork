function setupWaitlistForm(form) {
  const emailInput = form.querySelector('input[type="email"]');
  const button = form.querySelector('button');
  const buttonLabel = button.querySelector('.btn-label');
  const note = form.nextElementSibling;
  const honeypot = form.querySelector('input[name="website"]');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim();

    note.classList.remove('is-error', 'is-success');

    button.disabled = true;
    buttonLabel.textContent = 'Joining…';

    try {
      const res = await fetch('/api/waitlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, website: honeypot.value }),
      });
      const data = await res.json();

      if (!res.ok || !data.ok) {
        throw new Error(data.error || 'Something went wrong.');
      }

      emailInput.value = '';
      buttonLabel.textContent = "You're in";
      note.textContent = data.duplicate
        ? "You're already on the list — we'll email you when it's your turn."
        : `You're #${data.position} on the waitlist. We'll email you when it's your turn.`;
      note.classList.add('is-success');
    } catch (err) {
      button.disabled = false;
      buttonLabel.textContent = 'Join the waitlist';
      note.textContent = err.message || 'Something went wrong. Please try again.';
      note.classList.add('is-error');
    }
  });
}

document.querySelectorAll('.waitlist-form').forEach(setupWaitlistForm);
