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

  // --- Conversion tracking (GA4 via dataLayer; no PII is pushed) ---
  window.dataLayer = window.dataLayer || [];
  // Quote form submissions land on the thanks page: fire generate_lead there.
  if (location.pathname.indexOf('/quote/thanks') === 0) {
    window.dataLayer.push({ event: 'generate_lead', lead_source: 'quote_form' });
  }
  // Click-to-contact events
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (href.indexOf('tel:') === 0) {
      window.dataLayer.push({ event: 'phone_click', link_location: a.className || 'inline' });
    } else if (href.indexOf('wa.me') !== -1) {
      window.dataLayer.push({ event: 'whatsapp_click', link_location: a.className || 'inline' });
    } else if (href.indexOf('mailto:') === 0) {
      window.dataLayer.push({ event: 'email_click', link_location: a.className || 'inline' });
    }
  });
})();
