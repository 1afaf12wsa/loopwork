// Bookshelf. Touch screens can't hover, so the first tap on a book opens it (.is-open)
// and a second tap follows its link. Tapping anywhere else closes it.
// The plaques under the books act like the books themselves.
(function setupShelf() {
  const books = document.querySelectorAll('.book3d');
  if (!books.length) return;
  const touch = window.matchMedia('(hover: none)');
  const label = (b) => document.querySelector('.slot-label[data-k="' + b.dataset.k + '"]');
  const setHint = (b, on) => {
    const l = label(b);
    if (!l || !l.dataset.open) return;
    if (on && !l.dataset.orig) { l.dataset.orig = l.innerHTML; l.innerHTML = l.dataset.open; }
    if (!on && l.dataset.orig) { l.innerHTML = l.dataset.orig; delete l.dataset.orig; }
  };
  const closeAll = (except) => books.forEach((b) => { if (b !== except) { b.classList.remove('is-open'); setHint(b, false); } });
  books.forEach((book) => {
    book.addEventListener('click', (e) => {
      if (!touch.matches || book.classList.contains('is-open')) return;
      e.preventDefault();
      closeAll(book);
      book.classList.add('is-open');
      setHint(book, true);
    });
  });
  document.querySelectorAll('.slot-label.is-link').forEach((label) => {
    label.addEventListener('click', () => {
      const book = document.querySelector('.book3d[data-k="' + label.dataset.k + '"]');
      if (book) book.click();
    });
  });
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.book3d, .slot-label.is-link')) closeAll(null);
  });
})();
