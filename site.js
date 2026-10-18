// HouseClear — shared behaviour
(function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('main-nav');
  var mq = window.matchMedia('(max-width: 1060px)');

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    // Close menu when a destination link is chosen (not a submenu toggle)
    nav.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (!a) return;
      if (mq.matches && a.parentElement.classList.contains('has-drop')) return;
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  }

  // Mobile: parent items expand/collapse their submenu instead of navigating
  document.querySelectorAll('.has-drop > a').forEach(function (link) {
    link.setAttribute('aria-expanded', 'false');
    link.addEventListener('click', function (e) {
      if (!mq.matches) return; // desktop keeps hover + click-through to hub page
      e.preventDefault();
      var item = link.parentElement;
      var open = item.classList.toggle('open');
      link.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  // --- Conversion tracking: works with GA4 directly (gtag) AND with Tag Manager (dataLayer) ---
  window.dataLayer = window.dataLayer || [];
  function track(name, params) {
    params = params || {};
    if (typeof window.gtag === 'function') { window.gtag('event', name, params); }
    var payload = { event: name }; for (var k in params) payload[k] = params[k];
    window.dataLayer.push(payload);
  }
  // Quote form submissions land on the thanks page: fire generate_lead there.
  if (location.pathname.indexOf('/quote/thanks') === 0) {
    track('generate_lead', { lead_source: 'quote_form' });
  }
  // Click-to-contact events (no PII)
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var loc = a.className || 'inline';
    if (href.indexOf('tel:') === 0)             { track('phone_click',    { link_location: loc }); }
    else if (href.indexOf('wa.me') !== -1)      { track('whatsapp_click', { link_location: loc }); }
    else if (href.indexOf('mailto:') === 0)     { track('email_click',    { link_location: loc }); }
  });

  // Scroll-reveal: fade cards up as they enter the viewport
  if ('IntersectionObserver' in window &&
      !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var targets = document.querySelectorAll(
      '.trust-card, .svc-card, .step-card, .review-card, .area-chips-even .area-chip');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    targets.forEach(function (t) { t.classList.add('reveal'); io.observe(t); });
  }
})();
