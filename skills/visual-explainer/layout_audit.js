// layout_audit.js — paste this whole file inside a <script> at the end of <body>.
// It runs once after load and reports layout defects a reader would see:
//   * text that spills outside its box (HTML boxes and SVG <text> inside a <g> with a shape)
//   * two visible boxes that overlap without one containing the other
// It repeats the checks for every scene when the page has a [data-scene] stage
// (scene count from data-scenes="N" on the stage, else from .scene-dots children).
// Findings go to console.warn and to a hidden pre element with id layout-audit, so a headless
// `chrome --dump-dom` run can read them. Add ?audit=show to the URL to see the <pre>.
// Open the page with #scene=N to land on scene N (used by render_check.sh screenshots).
(function () {
  const LINES = [];
  const SEEN = new Set(); // a static defect is reported once, for the first scene that shows it
  const warn = (state, text) => {
    if (SEEN.has(text)) return;
    SEEN.add(text);
    LINES.push("layout-audit: " + state + ": " + text);
    console.warn("layout-audit: " + state + ": " + text);
  };
  const TOL = 2; // px of slack for borders and antialiasing
  const stage = document.querySelector("[data-scene]");

  const label = (el) => {
    const source = el instanceof SVGElement && !(el instanceof SVGTextElement) ? el.parentNode.querySelector(":scope > text") || el : el;
    const text = (source.textContent || "").trim().replace(/\s+/g, " ").slice(0, 40);
    const id = el.id ? "#" + el.id : el.classList && el.classList.length ? "." + el.classList[0] : "";
    return el.tagName.toLowerCase() + id + (text ? ' "' + text + '"' : "");
  };
  const shown = (el) => {
    for (let node = el; node && node.nodeType === 1 && node !== document.body; node = node.parentNode) {
      const cs = getComputedStyle(node);
      if (cs.display === "none" || cs.visibility === "hidden" || parseFloat(cs.opacity) < 0.05) return false;
    }
    const r = el.getBoundingClientRect();
    return r.width > 1 && r.height > 1;
  };
  const isBox = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === "inline" || cs.position === "fixed") return false;
    const bg = cs.backgroundColor;
    const hasBg = bg && bg !== "transparent" && !/rgba\(\s*\d+,\s*\d+,\s*\d+,\s*0\)/.test(bg);
    const hasBorder = ["Top", "Right", "Bottom", "Left"].some(
      (side) => parseFloat(cs["border" + side + "Width"]) > 0 && cs["border" + side + "Style"] !== "none");
    return hasBg || hasBorder;
  };
  const SKIP = new Set(["HTML", "BODY", "SCRIPT", "STYLE", "NOSCRIPT"]);

  function audit(state) {
    const htmlBoxes = [...document.body.querySelectorAll("*")].filter((el) =>
      !(el instanceof SVGElement) && !SKIP.has(el.tagName) && el.id !== "layout-audit" && shown(el) && isBox(el));
    // Only labeled SVG shapes count as boxes: a rect/ellipse/circle with a sibling <text>
    // whose center lies inside it. Decorative shapes and the parts of a multi-shape actor
    // overlap by design and are skipped.
    const svgShapes = [...document.querySelectorAll("svg g > rect, svg g > ellipse, svg g > circle")].filter((shape) => {
      if (!shown(shape) || parseFloat(getComputedStyle(shape).opacity) < 0.3) return false;
      const c = shape.getBoundingClientRect();
      return [...shape.parentNode.querySelectorAll(":scope > text")].some((text) => {
        const t = text.getBoundingClientRect(), cx = (t.left + t.right) / 2, cy = (t.top + t.bottom) / 2;
        return cx >= c.left && cx <= c.right && cy >= c.top && cy <= c.bottom;
      });
    });

    for (const box of htmlBoxes) {
      const cs = getComputedStyle(box);
      if (cs.overflowX === "auto" || cs.overflowX === "scroll" || cs.overflowY === "auto" || cs.overflowY === "scroll") continue;
      if (box.scrollWidth > box.clientWidth + TOL || box.scrollHeight > box.clientHeight + TOL) {
        warn(state, "text spills out of " + label(box) +
          " (content " + box.scrollWidth + "x" + box.scrollHeight + ", box " + box.clientWidth + "x" + box.clientHeight + ")");
      }
    }
    for (const text of document.querySelectorAll("svg text")) {
      if (!shown(text)) continue;
      const group = text.parentNode;
      if (!group || group.tagName === "svg") continue;
      const t = text.getBoundingClientRect();
      const cx = (t.left + t.right) / 2, cy = (t.top + t.bottom) / 2;
      // The shape the text sits in is the sibling shape that contains the text's center.
      // A caption beside a shape has no such sibling and is skipped.
      const shape = [...group.querySelectorAll(":scope > rect, :scope > ellipse, :scope > circle")].find((candidate) => {
        const c = candidate.getBoundingClientRect();
        return shown(candidate) && cx >= c.left && cx <= c.right && cy >= c.top && cy <= c.bottom;
      });
      if (!shape) continue;
      const s = shape.getBoundingClientRect();
      if (t.left < s.left - TOL || t.right > s.right + TOL || t.top < s.top - TOL || t.bottom > s.bottom + TOL) {
        warn(state, "SVG text spills out of its shape: " + label(text));
      }
    }
    const boxes = htmlBoxes.concat(svgShapes).map((el) => ({ el, r: el.getBoundingClientRect() }));
    for (let i = 0; i < boxes.length; i++) {
      for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i], b = boxes[j];
        if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
        const w = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
        const h = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
        if (w <= TOL * 2 || h <= TOL * 2) continue;
        const inside = (x, y) => x.r.left >= y.r.left - TOL && x.r.right <= y.r.right + TOL && x.r.top >= y.r.top - TOL && x.r.bottom <= y.r.bottom + TOL;
        if (inside(a, b) || inside(b, a)) continue; // a badge on a card, a label on a shape
        warn(state, label(a.el) + " overlaps " + label(b.el) + " by " + Math.round(w) + "x" + Math.round(h) + "px");
      }
    }
  }

  function sceneCount() {
    const declared = parseInt(stage.getAttribute("data-scenes"), 10);
    if (declared > 0) return declared;
    const dots = document.querySelectorAll(".scene-dots > *, #scene-dots > *");
    return dots.length || 1;
  }

  function run() {
    const freeze = document.createElement("style");
    freeze.textContent = "*,*::before,*::after{transition:none!important;animation:none!important}";
    document.head.appendChild(freeze);
    const original = stage ? stage.getAttribute("data-scene") : null;
    const count = stage ? sceneCount() : 1;
    // ponytail: scenes are switched by setting data-scene directly, so text that the
    // deck's own JS rewrites per scene is measured only for the scene shown at load.
    for (let n = 1; n <= count; n++) {
      if (stage) stage.setAttribute("data-scene", String(n));
      audit(stage ? "scene " + n : "page");
    }
    const wanted = (location.hash.match(/scene=(\d+)/) || [])[1];
    if (stage) stage.setAttribute("data-scene", wanted || original);
    if (stage && wanted) {
      // Bring the stage to the top of the viewport for a headless screenshot. A real scroll
      // leaves a headless capture blank, so the page is shifted with a transform instead.
      const top = Math.max(0, stage.getBoundingClientRect().top + window.scrollY - 16);
      document.body.style.transform = "translateY(-" + top + "px)";
    }
    freeze.remove();
    const warnings = LINES.length;
    LINES.push("layout-audit: done (" + count + " state" + (count === 1 ? "" : "s") + ", " + warnings + " warning" + (warnings === 1 ? "" : "s") + ")");
    const pre = document.createElement("pre");
    pre.id = "layout-audit";
    pre.hidden = !/audit=show/.test(location.search);
    pre.textContent = LINES.join("\n");
    document.body.appendChild(pre);
  }
  window.addEventListener("load", () => setTimeout(run, 300));
})();
