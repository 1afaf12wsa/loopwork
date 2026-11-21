// "In production" stack on the bookshelf: hover (or tap) plays a clip of its twine untying; leaving plays it backwards,
// then hides the clip so the photo underneath shows again. The clip is encoded all-intra, so seeking frame by frame is smooth.
(function () {
  document.querySelectorAll('.untie').forEach(function (box) {
    var v = box.querySelector('video');
    if (!v) return;
    var raf = null;
    function stopRewind() { if (raf) { cancelAnimationFrame(raf); raf = null; } }
    function forward() {
      stopRewind();
      box.classList.add('on');
      v.playbackRate = 0.85;
      var p = v.play();
      if (p && p.catch) p.catch(function () {});
    }
    function backward() {
      v.pause();
      stopRewind();
      var last = performance.now();
      function step(now) {
        var dt = (now - last) / 1000; last = now;
        var t = Math.max(0, v.currentTime - dt * 1.6);
        v.currentTime = t;
        if (t > 0) { raf = requestAnimationFrame(step); }
        else { raf = null; box.classList.remove('on'); }
      }
      raf = requestAnimationFrame(step);
    }
    box.addEventListener('mouseenter', forward);
    box.addEventListener('mouseleave', backward);
    box.addEventListener('click', function () {
      if (box.classList.contains('on') && (v.paused || v.ended) && v.currentTime > 0.2) backward(); else forward();
    });
  });
})();
