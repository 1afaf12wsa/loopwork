// Each form posts to /api/waitlist. The handle field rides along as `company`
// so the server keeps storing entries in exactly the shape it always has.
function setupApplyForm(form) {
  const emailInput = form.querySelector('input[type="email"]');
  const handleInput = form.querySelector('input[name="handle"]');
  const button = form.querySelector('button');
  const buttonLabel = button.querySelector('.btn-label');
  const note = form.nextElementSibling;
  const honeypot = form.querySelector('input[name="website"]');
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
