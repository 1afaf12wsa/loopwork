// Bookshelf.
// Desktop (a mouse): hovering a book opens it, zooms it forward and shows its info card (all CSS).
// Phones and touch screens: a tap on a book or its plaque opens a sheet from the bottom of the
// screen with the cover, an inside page and the same info card. A book's link is then one tap away.
(function setupShelf() {
  const sheet = document.querySelector('.shelf-sheet');
  const books = document.querySelectorAll('.book3d');
  if (!books.length || !sheet || typeof sheet.showModal !== 'function') return;
  const sheetMode = window.matchMedia('(hover: none), (max-width: 600px)');
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
  sheet.querySelector('.ss-close').addEventListener('click', () => sheet.close());
  sheet.addEventListener('click', (e) => {
    if (e.target === sheet) {                              // tap on the dimmed backdrop (outside the panel)
      const r = sheet.getBoundingClientRect();
      if (e.clientY < r.top || e.clientY > r.bottom || e.clientX < r.left || e.clientX > r.right) sheet.close();
    }
    if (e.target.closest('a')) sheet.close();               // following a link closes it first
  });
})();
