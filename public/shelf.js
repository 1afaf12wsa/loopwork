// Bookshelf. Touch screens can't hover, so the first tap on a book opens it (.is-open)
// and a second tap follows its link. Tapping anywhere else closes it.
// The plaques under the books act like the books themselves.
(function setupShelf() {
  const books = document.querySelectorAll('.book3d');
  if (!books.length) return;
  const touch = window.matchMedia('(hover: none)');
  const closeAll = (except) => books.forEach((b) => { if (b !== except) b.classList.remove('is-open'); });
  books.forEach((book) => {
    book.addEventListener('click', (e) => {
      if (!touch.matches || book.classList.contains('is-open')) return;
      e.preventDefault();
      closeAll(book);
      book.classList.add('is-open');
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
