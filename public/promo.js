// Black Week offer: until 30 Nov 2026, 23:59 Polish time (plus a few hours' grace for the Americas).
// After that, remove every .bw-only element. Delete this file and the .bw-only markup after 1 Dec.
(function () {
  if (Date.now() < Date.parse('2026-12-01T08:00:00Z')) return;
  document.querySelectorAll('.bw-only').forEach(function (el) { el.remove(); });
})();
