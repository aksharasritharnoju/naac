// naac_app/static/login_bg.js
(() => {
  const canvas = document.getElementById("ai-bg");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  let w, h, dpr;

  function resize() {
    dpr = Math.max(1, window.devicePixelRatio || 1);
    w = canvas.clientWidth;
    h = canvas.clientHeight;
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function rand(min, max) {
    return Math.random() * (max - min) + min;
  }

  // ------- Particle Network -------
  const nodes = [];
  const NODE_COUNT = 75;
  const MAX_DIST = 150;
  const SPEED = 0.35;

  function initNodes() {
    nodes.length = 0;
    for (let i = 0; i < NODE_COUNT; i++) {
      nodes.push({
        x: rand(0, w),
        y: rand(0, h),
        vx: rand(-SPEED, SPEED),
        vy: rand(-SPEED, SPEED),
        r: rand(1.2, 2.6),
      });
    }
  }

  // ------- Glowing Orbs -------
  const orbs = [];
  const ORB_COUNT = 5;

  function initOrbs() {
    orbs.length = 0;
    for (let i = 0; i < ORB_COUNT; i++) {
      orbs.push({
        x: rand(0, w),
        y: rand(0, h),
        r: rand(120, 220),
        vx: rand(-0.18, 0.18),
        vy: rand(-0.18, 0.18),
        a: rand(0.08, 0.16),
      });
    }
  }

  function drawOrbs() {
    for (const o of orbs) {
      o.x += o.vx;
      o.y += o.vy;

      if (o.x < -o.r || o.x > w + o.r) o.vx *= -1;
      if (o.y < -o.r || o.y > h + o.r) o.vy *= -1;

      const g = ctx.createRadialGradient(o.x, o.y, 0, o.x, o.y, o.r);
      g.addColorStop(0, `rgba(13,110,253,${o.a})`);
      g.addColorStop(0.6, `rgba(0,200,255,${o.a * 0.55})`);
      g.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(o.x, o.y, o.r, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // ------- Hex Grid Overlay -------
  function drawHexGrid() {
    const size = 28; // hex size
    const dx = size * 1.5;
    const dy = Math.sqrt(3) * size / 2;

    ctx.save();
    ctx.globalAlpha = 0.09;
    ctx.strokeStyle = "rgba(255,255,255,0.8)";
    ctx.lineWidth = 1;

    for (let y = -size; y < h + size; y += dy * 2) {
      for (let x = -size; x < w + size; x += dx) {
        const offset = ((Math.floor(y / (dy * 2)) % 2) * (dx / 2));
        drawHex(x + offset, y, size);
      }
    }
    ctx.restore();
  }

  function drawHex(cx, cy, s) {
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const ang = (Math.PI / 3) * i;
      const x = cx + Math.cos(ang) * s;
      const y = cy + Math.sin(ang) * s;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
  }

  // ------- Particle draw -------
  function step() {
    ctx.clearRect(0, 0, w, h);

    // Base gradient
    const bg = ctx.createLinearGradient(0, 0, w, h);
    bg.addColorStop(0, "rgba(8,12,24,1)");
    bg.addColorStop(1, "rgba(5,8,18,1)");
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, w, h);

    // Orbs under everything
    drawOrbs();

    // Hex overlay
    drawHexGrid();

    // Move nodes
    for (const n of nodes) {
      n.x += n.vx;
      n.y += n.vy;

      if (n.x < 0 || n.x > w) n.vx *= -1;
      if (n.y < 0 || n.y > h) n.vy *= -1;
    }

    // Lines
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i], b = nodes[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < MAX_DIST) {
          const alpha = (1 - dist / MAX_DIST) * 0.45;
          ctx.strokeStyle = `rgba(255,255,255,${alpha})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    }

    // Nodes
    for (const n of nodes) {
      ctx.fillStyle = "rgba(255,255,255,0.85)";
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(step);
  }

  // Boot
  resize();
  initNodes();
  initOrbs();
  step();

  window.addEventListener("resize", () => {
    resize();
    initNodes();
    initOrbs();
  });

  // ------- Typing effect (left panel) -------
  const el = document.getElementById("type-line");
  if (el) {
    const text = el.getAttribute("data-text") || "AI-powered NAAC / IQAC Documentation Management";
    let i = 0;
    function type() {
      el.textContent = text.slice(0, i);
      i++;
      if (i <= text.length) setTimeout(type, 28);
    }
    type();
  }
})();