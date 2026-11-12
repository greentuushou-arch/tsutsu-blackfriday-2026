<script>
/* BF REDESIGN：FVではじけ飛ぶ紙吹雪（タイトルの中心から放射状に飛び散る） */
(function () {
  var hero = document.querySelector('.hero');
  var title = hero && hero.querySelector('h1');
  if (!hero || !title) return;
  var motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (motion.matches) return;
  var canvas = document.createElement('canvas');
  canvas.className = 'rd-burst';
  canvas.setAttribute('aria-hidden', 'true');
  hero.insertBefore(canvas, hero.firstChild);
  var ctx = canvas.getContext && canvas.getContext('2d');
  if (!ctx) return;

  var COLORS = ['#e7a1a4', '#ffdcdc', '#f06e82', '#f8c3cc', '#fdf5e1', '#c47f88'];
  var GRAVITY = 620;
  var BIG_BURST = 150;
  var SMALL_BURST = 55;
  var REPEAT_MS = 5200;
  var width = 0, height = 0, parts = [], raf = 0, last = 0, inView = true, timer = 0;
  var rand = function (a, b) { return a + Math.random() * (b - a); };

  function fit() {
    var ratio = Math.min(window.devicePixelRatio || 1, 2);
    width = hero.clientWidth; height = hero.clientHeight;
    canvas.width = Math.round(width * ratio); canvas.height = Math.round(height * ratio);
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  }
  function origin() {
    var h = hero.getBoundingClientRect(), t = title.getBoundingClientRect();
    return { x: t.left - h.left + t.width / 2, y: t.top - h.top + t.height / 2 };
  }
  function burst(count, x, y, power) {
    for (var i = 0; i < count; i++) {
      var angle = rand(0, Math.PI * 2);
      var speed = rand(220, 820) * power;
      var r = Math.random();
      parts.push({
        kind: r < 0.5 ? 'heart' : (r < 0.85 ? 'ribbon' : 'dot'),
        x: x + rand(-20, 20), y: y + rand(-10, 10),
        vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed - rand(80, 260),
        size: rand(7, 17), rot: rand(0, 6.28), spin: rand(-9, 9), flip: rand(0, 6.28),
        color: COLORS[(Math.random() * COLORS.length) | 0],
        life: 0, max: rand(1.6, 2.8)
      });
    }
    start();
  }
  function drawHeart(s) {
    var z = s / 20;
    ctx.scale(z, z);
    ctx.beginPath(); ctx.moveTo(0, 9);
    ctx.bezierCurveTo(-3, 6, -11, 1, -10, -5); ctx.bezierCurveTo(-9, -12, -2, -11, 0, -6);
    ctx.bezierCurveTo(3, -12, 10, -11, 10, -5); ctx.bezierCurveTo(11, 0, 4, 7, 0, 9);
    ctx.fill();
  }
  function frame(now) {
    raf = 0;
    var dt = last ? Math.min((now - last) / 1000, 0.05) : 0; last = now;
    ctx.clearRect(0, 0, width, height);
    var drag = Math.pow(0.18, dt);
    parts = parts.filter(function (p) {
      p.life += dt;
      if (p.life > p.max || p.y > height + 40) return false;
      p.vx *= drag; p.vy = p.vy * drag + GRAVITY * dt;
      p.x += p.vx * dt; p.y += p.vy * dt; p.rot += p.spin * dt; p.flip += dt * 7;
      var fade = p.life > p.max * 0.7 ? 1 - (p.life - p.max * 0.7) / (p.max * 0.3) : 1;
      ctx.save(); ctx.globalAlpha = fade; ctx.fillStyle = p.color;
      ctx.translate(p.x, p.y); ctx.rotate(p.rot);
      if (p.kind === 'heart') drawHeart(p.size * 1.2);
      else if (p.kind === 'ribbon') { ctx.scale(1, Math.max(0.2, Math.abs(Math.cos(p.flip)))); ctx.fillRect(-p.size / 4, -p.size / 2, p.size / 2, p.size); }
      else { ctx.beginPath(); ctx.arc(0, 0, p.size / 4, 0, 6.28); ctx.fill(); }
      ctx.restore();
      return true;
    });
    if (parts.length) raf = requestAnimationFrame(frame); else last = 0;
  }
  function start() { if (!raf) raf = requestAnimationFrame(frame); }
  function bump() { title.classList.remove('is-bump'); void title.offsetWidth; title.classList.add('is-bump'); }
  function loop() {
    clearTimeout(timer);
    timer = setTimeout(function () {
      if (inView && !document.hidden) { var o = origin(); burst(SMALL_BURST, o.x + rand(-60, 60), o.y, 0.75); bump(); }
      loop();
    }, REPEAT_MS);
  }

  fit();
  if ('ResizeObserver' in window) new ResizeObserver(fit).observe(hero); else window.addEventListener('resize', fit);
  if ('IntersectionObserver' in window) new IntersectionObserver(function (e) { inView = e[e.length - 1].isIntersecting; }).observe(hero);
  var opened = false;
  function openingBurst() {
    if (opened) return;
    opened = true;
    var o = origin(); burst(BIG_BURST, o.x, o.y, 1); loop();
  }
  title.addEventListener('animationend', function (ev) { if (ev.animationName === 'rdPop') openingBurst(); });
  setTimeout(openingBurst, 1200);
  hero.addEventListener('click', function (ev) {
    if (ev.target.closest('a,button')) return;
    var h = hero.getBoundingClientRect(); burst(SMALL_BURST, ev.clientX - h.left, ev.clientY - h.top, 0.7);
  });
})();

/* BF REDESIGN：カレンダーの表示アニメ・いまココ・もっと見る */
(function () {
  var cal = document.getElementById('bf-cal');
  if (cal) {
    var start = new Date(cal.dataset.start).getTime();
    var end = new Date(cal.dataset.end).getTime();
    var nowLine = cal.querySelector('.bf-cal-now');
    var updateNow = function () {
      var t = Date.now();
      var inRange = t >= start && t < end;
      nowLine.hidden = !inRange;
      if (inRange) nowLine.style.setProperty('--now', ((t - start) / (end - start) * 100).toFixed(2) + '%');
    };
    updateNow();
    setInterval(updateNow, 60000);
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { if (e.isIntersecting) { cal.classList.add('is-in'); io.disconnect(); } });
      }, { threshold: 0.35 });
      io.observe(cal);
    } else {
      cal.classList.add('is-in');
    }
  }

  var isSp = window.matchMedia('(max-width: 767px)').matches;
  function collapse(grid, visible, label) {
    if (!grid) return;
    var items = Array.prototype.slice.call(grid.children);
    if (items.length <= visible) return;
    var hidden = items.slice(visible);
    hidden.forEach(function (el) { el.classList.add('rd-more-item'); });
    grid.classList.add('rd-more-wrap', 'is-collapsed');
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'rd-more-btn';
    btn.setAttribute('aria-expanded', 'false');
    var closedText = label.replace('{n}', hidden.length);
    btn.textContent = closedText;
    btn.addEventListener('click', function () {
      var open = grid.classList.toggle('is-collapsed') === false;
      btn.setAttribute('aria-expanded', String(open));
      btn.textContent = open ? '閉じる' : closedText;
      if (!open) grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    grid.insertAdjacentElement('afterend', btn);
  }
  collapse(document.querySelector('.point5-product-grid'), isSp ? 4 : 10, 'ほかの{n}商品も見る');
  collapse(document.getElementById('popular-product-grid'), isSp ? 8 : 12, '人気商品をもっと見る（あと{n}件）');
})();
</script>
<script>
/* BF REDESIGN：価格の「円」「〜」を小さくして数字を目立たせる */
(function () {
  document.querySelectorAll('.popular-product-price, .pokkiri-price').forEach(function (el) {
    if (el.querySelector('.rd-yen')) return;
    var m = el.textContent.trim().match(/^(.*?)(円〜?)$/);
    if (!m) return;
    el.textContent = m[1];
    var yen = document.createElement('span');
    yen.className = 'rd-yen';
    yen.textContent = m[2];
    el.appendChild(yen);
  });
})();
</script>
<script>
/* BF REDESIGN：流れる商品の速度を少しゆっくりにする（元の計算値 × SLOW） */
(function () {
  var SLOW = 1.35;
  document.querySelectorAll('.hero-product-track').forEach(function (track) {
    var lastSet = '';
    function adjust() {
      var raw = track.style.getPropertyValue('--product-scroll-duration');
      if (!raw || raw === lastSet) return;
      lastSet = (parseFloat(raw) * SLOW).toFixed(2) + 's';
      track.style.setProperty('--product-scroll-duration', lastSet);
    }
    adjust();
    new MutationObserver(adjust).observe(track, { attributes: true, attributeFilter: ['style'] });
  });
})();
</script>
