/* ══════════════════════════════════════════════════════
   NG Hive — интерактив сайта
   ══════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (sel) { return document.querySelector(sel); };
  var $$ = function (sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); };

  /* ─────────── год в подвале ─────────── */
  $('#year').textContent = new Date().getFullYear();

  /* ─────────── тема ─────────── */
  var root = document.documentElement;
  var savedTheme = null;
  try { savedTheme = localStorage.getItem('nghive-theme'); } catch (e) {}
  if (savedTheme) {
    root.setAttribute('data-theme', savedTheme);
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    root.setAttribute('data-theme', 'dark');
  }
  $('#themeToggle').addEventListener('click', function () {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('nghive-theme', next); } catch (e) {}
  });

  /* ─────────── язык: RU ⇄ EN ─────────── */
  var langBtn = $('#langToggle');
  var lang = 'ru';
  try { lang = localStorage.getItem('nghive-lang') || 'ru'; } catch (e) {}

  var translatable = $$('[data-en]');
  translatable.forEach(function (el) { el.setAttribute('data-ru', el.innerHTML.trim()); });

  function applyLang(next) {
    lang = next;
    translatable.forEach(function (el) {
      el.innerHTML = next === 'en' ? el.getAttribute('data-en') : el.getAttribute('data-ru');
    });
    root.setAttribute('lang', next);
    langBtn.textContent = next === 'en' ? 'EN' : 'RU';
    try { localStorage.setItem('nghive-lang', next); } catch (e) {}
  }
  applyLang(lang);
  langBtn.addEventListener('click', function () { applyLang(lang === 'ru' ? 'en' : 'ru'); });

  /* ─────────── меню и «прилипшая» шапка ─────────── */
  var header = $('#siteHeader');
  var nav = $('#siteNav');
  var burger = $('#burger');
  burger.addEventListener('click', function () {
    nav.classList.toggle('open');
    burger.classList.toggle('open');
  });
  $$('#siteNav a').forEach(function (a) {
    a.addEventListener('click', function () {
      nav.classList.remove('open');
      burger.classList.remove('open');
    });
  });

  /* ─────────── прогресс прокрутки + кнопка наверх ─────────── */
  var bar = $('#progressBar');
  var toTop = $('#toTop');
  function onScroll() {
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    var pct = max > 0 ? (h.scrollTop / max) * 100 : 0;
    bar.style.width = pct + '%';
    header.classList.toggle('stuck', h.scrollTop > 12);
    toTop.classList.toggle('show', h.scrollTop > 600);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  toTop.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' });
  });

  /* ─────────── появление блоков при прокрутке ─────────── */
  var revealables = $$('.reveal');
  if ('IntersectionObserver' in window && !reduced) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry, i) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        setTimeout(function () { el.classList.add('in'); }, i * 70);
        io.unobserve(el);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
    revealables.forEach(function (el) { io.observe(el); });
  } else {
    revealables.forEach(function (el) { el.classList.add('in'); });
  }

  /* ─────────── счётчики ─────────── */
  var counters = $$('.count');
  if ('IntersectionObserver' in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var target = parseInt(el.getAttribute('data-target'), 10) || 0;
        var start = performance.now();
        (function step(now) {
          var p = Math.min((now - start) / 1100, 1);
          el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3)));
          if (p < 1) requestAnimationFrame(step);
        })(start);
        cio.unobserve(el);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { cio.observe(el); });
  } else {
    counters.forEach(function (el) { el.textContent = el.getAttribute('data-target'); });
  }

  /* ─────────── медовое пятно за курсором ─────────── */
  var glow = $('#cursorGlow');
  if (window.matchMedia('(hover: hover)').matches) {
    window.addEventListener('pointermove', function (e) {
      glow.style.left = e.clientX + 'px';
      glow.style.top = e.clientY + 'px';
    }, { passive: true });
  }

  /* ─────────── наклон макетов за курсором ─────────── */
  if (!reduced) {
    $$('[data-tilt]').forEach(function (wrap) {
      var card = wrap.firstElementChild;
      wrap.addEventListener('pointermove', function (e) {
        var r = wrap.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5;
        var y = (e.clientY - r.top) / r.height - 0.5;
        card.style.transform = 'rotateY(' + (x * 14).toFixed(2) + 'deg) rotateX(' + (-y * 14).toFixed(2) + 'deg) translateY(-6px)';
      });
      wrap.addEventListener('pointerleave', function () { card.style.transform = ''; });
    });
  }

  /* ─────────── живой демо-коллаж ─────────── */
  var cells = $$('#collageDemo .cg-cell');
  // [колонка, ширина, строка, высота] в сетке 12×12
  var layouts = [
    [[1, 6, 1, 6], [7, 6, 1, 6], [1, 4, 7, 6], [5, 4, 7, 6], [9, 4, 7, 6]],
    [[1, 4, 1, 6], [5, 4, 1, 6], [9, 4, 1, 6], [1, 6, 7, 6], [7, 6, 7, 6]],
    [[1, 6, 1, 6], [1, 6, 7, 6], [7, 6, 1, 4], [7, 6, 5, 4], [7, 6, 9, 4]],
    [[1, 12, 1, 6], [1, 3, 7, 6], [4, 3, 7, 6], [7, 3, 7, 6], [10, 3, 7, 6]]
  ];
  var layoutIdx = 0;
  function applyLayout(idx) {
    layouts[idx].forEach(function (pos, i) {
      var c = cells[i];
      if (!c) return;
      c.style.gridColumn = pos[0] + ' / span ' + pos[1];
      c.style.gridRow = pos[2] + ' / span ' + pos[3];
    });
  }
  if (cells.length) {
    applyLayout(0);
    $('#collageShuffle').addEventListener('click', function () {
      layoutIdx = (layoutIdx + 1) % layouts.length;
      applyLayout(layoutIdx);
    });
  }

  /* ─────────── маленькие всплывашки ─────────── */
  var toastEl = null, toastTimer = null;
  function toast(msg) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.className = 'toast-note';
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = msg;
    requestAnimationFrame(function () { toastEl.classList.add('show'); });
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('show'); }, 2600);
  }

  /* ─────────── копирование почты ─────────── */
  var mailBtn = $('#mailCopy');
  mailBtn.addEventListener('click', function () {
    var mail = mailBtn.getAttribute('data-mail');
    var done = function () { toast(lang === 'en' ? 'Email copied' : 'Адрес скопирован'); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(mail).then(done, function () { window.location.href = 'mailto:' + mail; });
    } else {
      window.location.href = 'mailto:' + mail;
    }
  });

  /* ─────────── форма → почтовый клиент ─────────── */
  $('#contactForm').addEventListener('submit', function (e) {
    e.preventDefault();
    var f = e.target;
    var els = f.elements;
    var subject = encodeURIComponent('NG Hive — ' + (els.name.value || 'сообщение с сайта'));
    var body = encodeURIComponent(els.msg.value + '\n\n— ' + els.name.value + '\n' + els.email.value);
    window.location.href = 'mailto:' + mailBtn.getAttribute('data-mail') + '?subject=' + subject + '&body=' + body;
    toast(lang === 'en' ? 'Opening your mail app…' : 'Открываем почтовый клиент…');
  });

  /* ─────────── пасхалка: клик по логотипу выпускает пчелу ─────────── */
  var bee = $('#bee');
  $('#brandLogo').addEventListener('click', function () {
    bee.classList.remove('fly');
    void bee.offsetWidth;          // перезапускаем анимацию с нуля
    bee.classList.add('fly');
    toast(lang === 'en' ? 'Bzzz. There goes the bee.' : 'Жжж. Полетела.');
  });

  /* ─────────── фон героя: живые соты ─────────── */
  var canvas = $('#hexCanvas');
  var ctx = canvas.getContext('2d');
  var hexes = [];
  var mouse = { x: -9999, y: -9999 };
  var R = 34;                       // радиус соты
  var dpr = Math.min(window.devicePixelRatio || 1, 2);

  function buildHexes() {
    var rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    hexes = [];
    var w = Math.sqrt(3) * R, h = 2 * R * 0.75;
    for (var row = -1; row * h < rect.height + R; row++) {
      for (var col = -1; col * w < rect.width + w; col++) {
        hexes.push({
          x: col * w + (row % 2 ? w / 2 : 0),
          y: row * h,
          seed: Math.random() * Math.PI * 2,
          lit: 0
        });
      }
    }
  }

  function hexPath(x, y) {
    ctx.beginPath();
    for (var i = 0; i < 6; i++) {
      var a = Math.PI / 180 * (60 * i - 30);
      var px = x + R * Math.cos(a), py = y + R * Math.sin(a);
      i ? ctx.lineTo(px, py) : ctx.moveTo(px, py);
    }
    ctx.closePath();
  }

  var t = 0;
  function drawHex() {
    if (!canvas.width) return;
    var rect = canvas.getBoundingClientRect();
    ctx.clearRect(0, 0, rect.width, rect.height);
    var dark = root.getAttribute('data-theme') === 'dark';
    t += 0.006;

    hexes.forEach(function (hx, i) {
      var dx = hx.x - mouse.x, dy = hx.y - mouse.y;
      var dist = Math.sqrt(dx * dx + dy * dy);
      var near = Math.max(0, 1 - dist / 190);
      var shimmer = reduced ? 0.12 : (Math.sin(t * 1.6 + hx.seed + i * 0.05) + 1) * 0.5 * 0.16;
      hx.lit += (Math.max(near, shimmer) - hx.lit) * 0.14;

      hexPath(hx.x, hx.y);
      ctx.strokeStyle = dark
        ? 'rgba(242,177,52,' + (0.06 + hx.lit * 0.55) + ')'
        : 'rgba(150,156,164,' + (0.10 + hx.lit * 0.35) + ')';
      ctx.lineWidth = 1 + hx.lit * 0.8;
      ctx.stroke();

      if (hx.lit > 0.05) {
        ctx.fillStyle = 'rgba(242,177,52,' + (hx.lit * (dark ? 0.16 : 0.2)) + ')';
        ctx.fill();
      }
    });
    requestAnimationFrame(drawHex);
  }

  function resizeCanvas() { buildHexes(); }
  window.addEventListener('resize', resizeCanvas);
  canvas.parentElement.addEventListener('pointermove', function (e) {
    var r = canvas.getBoundingClientRect();
    mouse.x = e.clientX - r.left;
    mouse.y = e.clientY - r.top;
  }, { passive: true });
  canvas.parentElement.addEventListener('pointerleave', function () {
    mouse.x = mouse.y = -9999;
  });

  buildHexes();
  drawHex();
})();
