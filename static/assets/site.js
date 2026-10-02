/* Keystone Fence & Deck Co. — site behaviour.
   Navigation, project filters and the lead-form engine. No dependencies. */
(function () {
  'use strict';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var MODE = (window.KEYSTONE_FORM && window.KEYSTONE_FORM.mode) || document.body.getAttribute('data-form-mode') || 'live';
  var track = function (name, params) { if (typeof window.gtag === 'function') window.gtag('event', name, params || {}); };

  // ── header ────────────────────────────────────────────────────
  var hdr = $('.hdr');
  if (hdr) {
    var onScroll = function () { hdr.classList.toggle('scrolled', window.scrollY > 8); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && document.activeElement && document.activeElement.closest('.nav-item')) document.activeElement.blur();
  });

  // ── mobile drawer ─────────────────────────────────────────────
  var drawer = $('#drawer'), opener = $('.js-menu');
  var setDrawer = function (open) {
    if (!drawer) return;
    drawer.classList.toggle('open', open);
    drawer.setAttribute('aria-hidden', open ? 'false' : 'true');
    if (opener) opener.setAttribute('aria-expanded', open ? 'true' : 'false');
    document.documentElement.style.overflow = open ? 'hidden' : '';
    if (open) { var c = $('.js-close', drawer); if (c) c.focus(); } else if (opener) { opener.focus(); }
  };
  if (opener) opener.addEventListener('click', function () { setDrawer(true); });
  $$('.js-close').forEach(function (b) { b.addEventListener('click', function () { setDrawer(false); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && drawer && drawer.classList.contains('open')) setDrawer(false); });
  $$('.d-group > button.d-row').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var g = btn.parentElement, open = !g.classList.contains('open');
      g.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  // ── click-to-call tracking ────────────────────────────────────
  $$('a[href^="tel:"]').forEach(function (a) { a.addEventListener('click', function () { track('click_to_call', { link_location: a.getAttribute('data-loc') || 'page' }); }); });

  // ── project filters ───────────────────────────────────────────
  var filterBar = $('.filters');
  if (filterBar) {
    var cards = $$('.proj-card');
    filterBar.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-filter]');
      if (!b) return;
      var f = b.getAttribute('data-filter');
      $$('button', filterBar).forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      cards.forEach(function (c) { c.hidden = !(f === 'all' || c.getAttribute('data-silo') === f); });
      var live = $('.js-filter-count');
      if (live) live.textContent = cards.filter(function (c) { return !c.hidden; }).length + ' project types shown';
    });
  }

  // ── lead forms ────────────────────────────────────────────────
  var MAX_FILES = 8, MAX_RAW = 15 * 1024 * 1024;
  var EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  function fieldOf(el) { return el.closest('.field') || el.closest('fieldset'); }

  function checkField(box) {
    var ok = true;
    if (box.tagName === 'FIELDSET') {
      if (box.hasAttribute('data-required')) ok = !!$('input:checked', box);
    } else {
      var el = $('input, select, textarea', box);
      if (!el) return true;
      var v = (el.value || '').trim();
      if (el.required && !v) ok = false;
      else if (v && el.type === 'email' && !EMAIL.test(v)) ok = false;
      else if (v && el.hasAttribute('data-phone') && v.replace(/\D/g, '').length < 10) ok = false;
    }
    box.classList.toggle('invalid', !ok);
    var ctl = box.tagName === 'FIELDSET' ? null : $('input, select, textarea', box);
    if (ctl) ctl.setAttribute('aria-invalid', ok ? 'false' : 'true');
    return ok;
  }

  function checkScope(scope) {
    var boxes = $$('.field, fieldset[data-required]', scope);
    var first = null;
    boxes.forEach(function (b) { if (!checkField(b) && !first) first = b; });
    if (first) {
      var ctl = $('input, select, textarea', first);
      if (ctl) ctl.focus({ preventScroll: true });
      first.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    return !first;
  }

  function compress(file) {
    return new Promise(function (resolve) {
      if (!/^image\/(jpeg|png|webp)$/i.test(file.type)) { resolve(file); return; }
      var url = URL.createObjectURL(file), img = new Image();
      img.onload = function () {
        var max = 1600, w = img.naturalWidth, h = img.naturalHeight, s = Math.min(1, max / Math.max(w, h));
        var c = document.createElement('canvas');
        c.width = Math.round(w * s); c.height = Math.round(h * s);
        c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
        c.toBlob(function (b) {
          URL.revokeObjectURL(url);
          resolve(b && b.size < file.size ? new File([b], file.name.replace(/\.[^.]+$/, '') + '.jpg', { type: 'image/jpeg' }) : file);
        }, 'image/jpeg', 0.82);
      };
      img.onerror = function () { URL.revokeObjectURL(url); resolve(file); };
      img.src = url;
    });
  }

  function post(fd) {
    return fetch(window.KEYSTONE_FORM.endpoint, { method: 'POST', body: fd, headers: { Accept: 'application/json' } })
      .then(function (r) { return r.json().catch(function () { return { success: r.ok }; }); });
  }

  function initForm(form) {
    var type = form.getAttribute('data-form');
    var shell = form.closest('[data-form-shell]') || form.parentElement;
    var success = $('.success', shell);
    var status = $('.form-status', form);
    var files = [];

    // Service pre-selected from ?service= (every service-page CTA passes it)
    var svc = new URLSearchParams(window.location.search).get('service');
    var sel = $('select[name="service"]', form);
    if (svc && sel) {
      $$('option', sel).forEach(function (o) { if (o.getAttribute('data-slug') === svc) sel.value = o.value; });
    }

    // two-step flow
    var panels = $$('.step-panel', form), bars = $$('.progress > div', form), step = 0;
    var show = function (i) {
      step = i;
      panels.forEach(function (p, k) { p.hidden = k !== i; });
      bars.forEach(function (b, k) { b.classList.toggle('on', k <= i); });
      var first = $('input:not([type=hidden]):not(.hp), select, textarea', panels[i]);
      if (first) first.focus({ preventScroll: true });
      form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };
    $$('[data-next]', form).forEach(function (b) { b.addEventListener('click', function () { if (checkScope(panels[step])) show(step + 1); }); });
    $$('[data-back]', form).forEach(function (b) { b.addEventListener('click', function () { show(step - 1); }); });

    form.addEventListener('input', function (e) { var b = fieldOf(e.target); if (b && b.classList.contains('invalid')) checkField(b); });
    form.addEventListener('change', function (e) { var b = fieldOf(e.target); if (b && b.classList.contains('invalid')) checkField(b); });

    // photos
    var drop = $('.drop', form), thumbs = $('.thumbs', form), count = $('.js-photo-count', form);
    var render = function () {
      if (!thumbs) return;
      thumbs.innerHTML = '';
      files.forEach(function (f, i) {
        var t = document.createElement('div'); t.className = 'thumb';
        var img = document.createElement('img'); img.alt = ''; img.src = URL.createObjectURL(f);
        img.onload = function () { URL.revokeObjectURL(img.src); };
        var n = document.createElement('small'); n.textContent = f.name;
        var x = document.createElement('button'); x.type = 'button'; x.setAttribute('aria-label', 'Remove ' + f.name); x.textContent = '×';
        x.addEventListener('click', function () { files.splice(i, 1); render(); });
        t.appendChild(img); t.appendChild(n); t.appendChild(x); thumbs.appendChild(t);
      });
      if (count) count.textContent = files.length ? files.length + ' of ' + MAX_FILES + ' photos added' : 'Up to ' + MAX_FILES + ' photos';
    };
    var addFiles = function (list) {
      var skipped = 0;
      Array.prototype.forEach.call(list, function (f) {
        if (files.length >= MAX_FILES || !/^image\//.test(f.type) || f.size > MAX_RAW) { skipped++; return; }
        files.push(f);
      });
      render();
      if (skipped && status) { status.className = 'form-status show error'; status.textContent = skipped + ' file(s) skipped — photos only, up to ' + MAX_FILES + ', 15 MB each.'; }
    };
    if (drop) {
      var input = $('input[type=file]', drop);
      ['dragenter', 'dragover'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('over'); }); });
      ['dragleave', 'drop'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove('over'); }); });
      drop.addEventListener('drop', function (e) { if (e.dataTransfer) addFiles(e.dataTransfer.files); });
      input.addEventListener('change', function () { addFiles(input.files); input.value = ''; });
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (status) { status.className = 'form-status'; status.textContent = ''; }
      var scope = panels.length ? panels[step] : form;
      if (!checkScope(scope)) return;
      if (panels.length && step < panels.length - 1) { show(step + 1); return; }
      var trap = $('input[name="botcheck"]', form);
      if (trap && trap.checked) return;

      var btn = $('button[type=submit]', form), label = btn.innerHTML;
      btn.disabled = true; btn.textContent = 'Sending…';
      var finish = function (ok, note) {
        btn.disabled = false; btn.innerHTML = label;
        if (ok) {
          track('generate_lead', { form_type: type, service: sel ? sel.value : (($('input[name=service]', form) || {}).value || '') });
          form.hidden = true;
          if (success) {
            success.classList.add('show');
            var pn = $('.js-photo-note', success); if (pn) pn.hidden = !note;
            var pv = $('.js-preview-note', success); if (pv) pv.hidden = MODE !== 'preview';
            success.focus();
          }
        } else if (status) {
          status.className = 'form-status show error';
          status.textContent = note;
        }
      };

      var fd = new FormData(form);
      fd.delete('photos');
      // One source of truth for the form key: the site config.
      if (window.KEYSTONE_FORM && window.KEYSTONE_FORM.key) fd.set('access_key', window.KEYSTONE_FORM.key);
      fd.append('page', window.location.href);

      if (MODE === 'preview') { setTimeout(function () { finish(true, false); }, 600); return; }
      if (!window.KEYSTONE_FORM || !window.KEYSTONE_FORM.key) {
        finish(false, 'This form isn\'t connected yet. Please call ' + (window.KEYSTONE_FORM ? window.KEYSTONE_FORM.phone : 'us') + ' and we\'ll take your details by phone.');
        return;
      }
      Promise.all(files.map(compress)).then(function (ready) {
        ready.forEach(function (f) { fd.append('attachment', f, f.name); });
        return post(fd).then(function (res) {
          if (res && res.success) { finish(true, false); return; }
          if (!ready.length) throw new Error((res && res.message) || 'rejected');
          // The endpoint refused the photos (size or plan limit): send the
          // request without them rather than lose the lead.
          fd.delete('attachment');
          fd.append('photos_note', ready.length + ' photo(s) were attached but could not be delivered — ask the customer to text them.');
          return post(fd).then(function (r2) {
            if (r2 && r2.success) finish(true, true);
            else throw new Error((r2 && r2.message) || 'rejected');
          });
        });
      }).catch(function () {
        finish(false, 'Something went wrong sending your request. Please try again, or call ' + window.KEYSTONE_FORM.phone + '.');
      });
    });
    render();
  }
  $$('form.js-lead').forEach(initForm);

  // Hero video: a muted loop. Stays on its poster for reduced-motion and
  // Save-Data visitors, pauses off-screen, and has a visible pause control.
  (function () {
    var v = document.querySelector('.js-vid');
    if (!v) return;
    var btn = v.closest('figure').querySelector('.vid-btn'), lbl = btn.querySelector('.vid-lbl');
    var calm = (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) ||
               (navigator.connection && navigator.connection.saveData);
    var wanted = !calm, inView = true;
    function sync() { btn.classList.toggle('is-paused', v.paused); lbl.textContent = v.paused ? 'Play' : 'Pause'; }
    function go() { var p = v.play(); if (p && p.catch) p.catch(sync); }
    btn.hidden = false;
    btn.addEventListener('click', function () { wanted = v.paused; if (wanted) go(); else v.pause(); });
    v.addEventListener('play', sync); v.addEventListener('pause', sync);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        inView = es[0].isIntersecting;
        if (inView && wanted) go(); else if (!inView && !v.paused) v.pause();
      }, { threshold: 0.2 }).observe(v);
    } else if (wanted) go();
    sync();
  })();

  // keep the footer year current without an edit each January
  $$('.js-year').forEach(function (y) { y.textContent = new Date().getFullYear(); });
})();
