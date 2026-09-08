// K4DIA. Two small jobs: the menu on narrow screens, and the dial.

(function () {
  "use strict";

  // -- menu ---------------------------------------------------------------
  var head = document.querySelector(".masthead");
  var toggle = document.querySelector(".menu-toggle");
  var mobile = document.getElementById("mainnav-mobile");

  if (head && toggle && mobile) {
    toggle.addEventListener("click", function () {
      var open = head.classList.toggle("menu-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
    mobile.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        head.classList.remove("menu-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && head.classList.contains("menu-open")) {
        head.classList.remove("menu-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  // -- the dial -----------------------------------------------------------
  // The knob is decoration, but decoration that lies is worse than none, so
  // it points at whichever row is live. Four rows across the sweep of the
  // scale, the way a four-position selector actually sits.
  var rows = Array.prototype.slice.call(document.querySelectorAll(".index-row"));
  var face = document.querySelector(".knob-face");

  if (rows.length && face) {
    var SWEEP = 184;                        // degrees between the end stops
    var START = -92;                        // where position zero sits

    function pointAt(i) {
      var step = rows.length > 1 ? SWEEP / (rows.length - 1) : 0;
      face.style.transform = "rotate(" + (START + i * step) + "deg)";
    }

    function makeLive(i) {
      rows.forEach(function (r, n) { r.classList.toggle("is-active", n === i); });
      pointAt(i);
    }

    rows.forEach(function (row, i) {
      row.addEventListener("mouseenter", function () { pointAt(i); });
      row.addEventListener("focus", function () { makeLive(i); });
      row.addEventListener("click", function () { makeLive(i); });
    });

    var current = 0;
    document.querySelector(".panel").addEventListener("mouseleave", function () {
      pointAt(current);
    });

    // Scrolling past a section turns the dial to it, so the panel keeps
    // saying where you are rather than where you last clicked.
    var targets = rows.map(function (r) {
      return document.querySelector(r.getAttribute("href"));
    });

    if ("IntersectionObserver" in window) {
      var seen = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var i = targets.indexOf(entry.target);
          if (i >= 0) {
            current = i;
            makeLive(i);
            var top = document.querySelector(".mainnav a[href='#" +
                                             entry.target.id + "']");
            document.querySelectorAll(".mainnav a").forEach(function (a) {
              a.classList.toggle("is-here", a === top);
            });
          }
        });
      }, { rootMargin: "-45% 0px -45% 0px" });
      targets.forEach(function (t) { if (t) seen.observe(t); });
    }
  }
})();
