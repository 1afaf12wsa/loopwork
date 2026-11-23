// Bookshelf.
// Desktop (a mouse): hovering a book opens it, zooms it forward and shows its info card (all CSS).
// Phones, touch screens and windows under 1000px: a tap on a book or its plaque opens a sheet from the bottom of the
// screen with the cover, an inside page and the same info card. A book's link is then one tap away.
(function setupShelf() {
  const sheet = document.querySelector('.shelf-sheet');
  const books = document.querySelectorAll('.book3d');
  if (!books.length || !sheet || typeof sheet.showModal !== 'function') return;
  const sheetMode = window.matchMedia('(hover: none), (max-width: 999px)');
  const art = sheet.querySelector('.ss-art');
  const body = sheet.querySelector('.ss-body');

  function openSheet(k) {
    const card = document.querySelector('.shelf-card[data-k="' + k + '"]');
    if (!card) return false;
    art.textContent = '';
    if (card.dataset.cover) {
      [card.dataset.cover, card.dataset.page].forEach((src, i) => {
        if (!src) return;
        const img = document.createElement('img');
        img.src = src; img.alt = i === 0 ? 'Cover of ' + card.querySelector('.sc-title').textContent : '';
        art.appendChild(img);
      });
    } else {
      const y = document.createElement('div');
      y.className = 'ss-yours'; y.textContent = 'Your book';
      art.appendChild(y);
    }
    body.innerHTML = card.innerHTML;
    sheet.showModal();
    return true;
  }

  books.forEach((book) => {
    book.addEventListener('click', (e) => {
      if (!sheetMode.matches) return;
      if (openSheet(book.dataset.k)) e.preventDefault();
    });
  });
  document.querySelectorAll('.slot-label.is-link').forEach((label) => {
    label.addEventListener('click', () => {
      const k = label.dataset.k;
      if (sheetMode.matches) { openSheet(k); return; }
      const book = document.querySelector('.book3d[data-k="' + k + '"]');
      if (book) book.click();
    });
  });
  // Desktop: CSS :hover only covers the book's small spot on the shelf, but the open book is almost twice as big.
  // So the script keeps a book open (.is-open) while the mouse is anywhere over the open book or its card,
  // and closes it only once the mouse has left both.
  const zoomMode = window.matchMedia('(hover: hover) and (min-width: 1000px)');
  let openBook = null, closeTimer = null;
  // On desktop the script alone decides which book is open (CSS :hover is switched off under .js-shelf),
  // so two books can never be open at once.
  document.querySelectorAll('.bookcase').forEach((bc) => bc.classList.add('js-shelf'));
  const cardOf = (b) => document.querySelector('.shelf-card[data-k="' + b.dataset.k + '"]');
  function rectsOf(b) {
    // Only what you can see: the pages, the open cover and the card. (The book's own box is bigger
    // than its visible pages once it is scaled, so it is left out.)
    const parts = [cardOf(b), ...b.querySelectorAll('.b3-page, .b3-inner, .yours-page')];
    return parts.filter(Boolean).map((el) => el.getBoundingClientRect()).filter((r) => r.width > 0);
  }
  function setOpen(b) {
    if (openBook && openBook !== b) openBook.classList.remove('is-open');
    openBook = b;
    if (b) b.classList.add('is-open');
  }
  books.forEach((book) => {
    book.addEventListener('pointerenter', (e) => {
      if (!zoomMode.matches || e.pointerType === 'touch') return;
      clearTimeout(closeTimer);
      setOpen(book);
    });
  });
  document.addEventListener('pointermove', (e) => {
    if (!zoomMode.matches || e.pointerType === 'touch') return;
    if (!openBook) {                                        // e.g. after a scroll closed it while the mouse stayed on a book
      const b = e.target.closest && e.target.closest('.book3d');
      if (b) setOpen(b);
      return;
    }
    const pad = 10;
    const inside = rectsOf(openBook).some((r) => e.clientX >= r.left - pad && e.clientX <= r.right + pad && e.clientY >= r.top - pad && e.clientY <= r.bottom + pad);
    if (inside) { clearTimeout(closeTimer); closeTimer = null; return; }
    if (!closeTimer) closeTimer = setTimeout(() => { closeTimer = null; setOpen(null); }, 120);
  });
  document.addEventListener('pointerleave', () => { clearTimeout(closeTimer); setOpen(null); });
  window.addEventListener('scroll', () => { if (openBook && zoomMode.matches) { clearTimeout(closeTimer); setOpen(null); } }, { passive: true });

  sheet.querySelector('.ss-close').addEventListener('click', () => sheet.close());
  sheet.addEventListener('click', (e) => {
    if (e.target === sheet) {                              // tap on the dimmed backdrop (outside the panel)
      const r = sheet.getBoundingClientRect();
      if (e.clientY < r.top || e.clientY > r.bottom || e.clientX < r.left || e.clientX > r.right) sheet.close();
    }
    if (e.target.closest('a')) sheet.close();               // following a link closes it first
  });
})();
