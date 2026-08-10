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

  /* ---- Floating WhatsApp button (all pages) ---- */
  var wa = document.createElement("a");
  wa.className = "wa-float";
  wa.href = "https://wa.me/256775377245?text=Hello%20Solumed%2C%20I%27m%20interested%20in%20Business%20Manager";
  wa.setAttribute("aria-label", "Chat with us on WhatsApp");
  wa.target = "_blank"; wa.rel = "noopener";
  wa.innerHTML = '<svg viewBox="0 0 32 32"><path d="M16 3C9.4 3 4 8.4 4 15c0 2.1.6 4.2 1.6 6L4 29l8.2-1.5c1.7.9 3.7 1.5 5.8 1.5 6.6 0 12-5.4 12-12S22.6 3 16 3zm0 21.8c-1.8 0-3.5-.5-5-1.3l-.4-.2-4.9.9.9-4.7-.2-.4c-1-1.6-1.6-3.4-1.6-5.1 0-5.4 4.5-9.8 10-9.8s10 4.4 10 9.8-4.5 9.8-9.8 9.8zm5.4-7.3c-.3-.2-1.8-.9-2-1-.3-.1-.5-.2-.7.2-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.2-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.5-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.6-.1-.2-.7-1.7-1-2.3-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.1 1.1-1.1 2.7s1.2 3.1 1.3 3.3c.2.2 2.3 3.6 5.7 5 .8.3 1.4.5 1.9.7.8.2 1.5.2 2.1.1.6-.1 1.8-.8 2.1-1.5.3-.7.3-1.3.2-1.5-.1-.1-.3-.2-.6-.4z"/></svg>';
  document.body.appendChild(wa);

  /* ---- Live till toasts over the hero visual (SBM page) ---- */
  var hv = document.getElementById("heroVisual");
  if (hv && !reduced) {
    var toasts = [
      ["🧾", "Receipt printed", "Sale S-0231 · UGX 12,500"],
      ["📲", "MTN MoMo received", "UGX 45,000 · auto-recorded"],
      ["📦", "Stock updated", "Sugar 1kg · 2 sold, 23 left"],
      ["📊", "Day report ready", "Sent to the owner on WhatsApp"],
      ["🖨", "Kitchen ticket sent", "Table 4 · 2 items"],
      ["☁", "Cloud backup done", "Whole shop backed up online"]
    ];
    var t = document.createElement("div");
    t.className = "tilltoast";
    hv.appendChild(t);
    var ti = 0;
    function showToast() {
      var m = toasts[ti % toasts.length]; ti++;
      t.innerHTML = '<span class="tico">' + m[0] + '</span><span>' + m[1] +
                    "<small>" + m[2] + "</small></span>";
      t.classList.add("show");
      setTimeout(function () { t.classList.remove("show"); }, 3400);
    }
    setTimeout(showToast, 1200);
    setInterval(showToast, 4600);
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
