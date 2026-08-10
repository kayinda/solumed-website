/* Solumed site motion: scroll reveals, count-up numbers, rotating messages.
   Progressive enhancement only - with JS off or reduced motion requested,
   every element stays fully visible and static. */
(function () {
  var reduced = window.matchMedia
    && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- Scroll reveal ---- */
  if (!reduced && "IntersectionObserver" in window) {
    var targets = document.querySelectorAll(
      ".card, .stat, .qt, .pcard, .tstat, .sec-head, .fcard, .price-table, .foot .wrap > div");
    targets.forEach(function (el, i) {
      el.classList.add("rv");
      el.style.transitionDelay = (Math.min(i % 6, 4) * 70) + "ms";
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    targets.forEach(function (el) { io.observe(el); });
  }

  /* ---- Count-up numbers (hero stats and dashboard mock) ---- */
  function countUp(el) {
    var txt = el.textContent;
    var m = txt.match(/([\d,]+)/);
    if (!m) return;
    var target = parseInt(m[1].replace(/,/g, ""), 10);
    if (!target || target > 5000000) return;
    var pre = txt.slice(0, m.index), post = txt.slice(m.index + m[1].length);
    var t0 = null, DUR = 900;
    function frame(ts) {
      if (!t0) t0 = ts;
      var p = Math.min((ts - t0) / DUR, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      var val = Math.round(target * eased);
      el.textContent = pre + val.toLocaleString("en-US") + post;
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  if (!reduced && "IntersectionObserver" in window) {
    var nums = document.querySelectorAll(".stat .n, .pcard .v, .tstat .v");
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { countUp(e.target); cio.unobserve(e.target); }
      });
    }, { threshold: 0.6 });
    nums.forEach(function (el) { cio.observe(el); });
  }

  /* ---- Rotating message bar ---- */
  var bar = document.querySelector("[data-msgs]");
  if (bar) {
    var msgs;
    try { msgs = JSON.parse(bar.getAttribute("data-msgs")); } catch (e) { msgs = null; }
    if (msgs && msgs.length) {
      var span = bar.querySelector(".rotmsg") || bar;
      var idx = 0;
      span.textContent = msgs[0];
      if (!reduced && msgs.length > 1) {
        setInterval(function () {
          span.classList.add("fade");
          setTimeout(function () {
            idx = (idx + 1) % msgs.length;
            span.textContent = msgs[idx];
            span.classList.remove("fade");
          }, 350);
        }, 3800);
      }
    }
  }
})();
