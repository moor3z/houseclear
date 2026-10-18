#!/usr/bin/env python3
"""HouseClear static site generator.
Run:  python3 build.py
Output: ./site/  — deploy the contents of that folder to Netlify / any static host.
To add a service or location later, add an entry to services_data.py or
locations_data.py and re-run this script.
"""
import os, json, shutil, html
from services_data import SERVICES
from locations_data import LOCATIONS
from guides_data import GUIDES, GUIDE_CLUSTERS

# ---------------------------------------------------------------- config ---
DOMAIN   = "https://houseclear.uk"                  # live domain (Cloudflare)
PHONE      = "01244 722 330"        # HouseClear line (default sitewide)
PHONE_E164 = "+441244722330"
PHONE2     = "0151 440 3704"        # Liverpool/Merseyside (used on Liverpool & Wirral pages)
PHONE2_E164 = "+441514403704"
WA_LINK  = "https://wa.me/message/R42OUVB7Q6DHE1"   # WhatsApp Business link
GBP_URL  = "https://maps.app.goo.gl/ENYvPdr3JCx8Pux27"  # Google Business Profile
EMAIL    = "steven@tidyupltd.com"
GA4_ID   = "G-XXXXXXXXXX"                           # TODO: set GA4 Measurement ID
COMPANY_NO = "14294404"
REG_OFFICE = "Unit 5 Catherine Court, Manor Lane, Hawarden, Deeside, CH5 3NU"
VAT_NO     = "441151045"
WASTE_LIC  = "CBDU464597"
BIZ_NAME = "HouseClear"
# GitHub Pages preview support:
#   BASE_PATH=/repo-name OUT_DIR=docs python3 build.py
# rewrites internal links for a subfolder host and noindexes every page.
BASE  = os.environ.get("BASE_PATH", "").rstrip("/")
OUT   = os.path.join(os.path.dirname(__file__), os.environ.get("OUT_DIR", "site"))

AREAS_HEADLINE = ["Cheshire", "Flintshire", "Liverpool", "The Wirral", "Denbighshire"]

_PHONE_OVERRIDE = None  # (display, e164) — set per-page for regional numbers
def cur_phone():
    return _PHONE_OVERRIDE or (PHONE, PHONE_E164)

def loc_url(slug): return f"/{slug}/"
def svc_url(slug): return f"/services/{slug}/"
def guide_url(slug): return f"/guides/{slug}/"
SVC = {s["slug"]: s for s in SERVICES}
LOC = {l["slug"]: l for l in LOCATIONS}
GDE = {g["slug"]: g for g in GUIDES}
# service slug -> guides that reference it (for "helpful guides" chips)
SVC_GUIDES = {}
for g in GUIDES:
    for s in g["related_services"]:
        SVC_GUIDES.setdefault(s, []).append(g["slug"])

# ------------------------------------------------------------ components ---
def esc(t): return html.escape(t, quote=True)

import re as _re
def esc_keep_links(text):
    """esc() for copy that may contain trusted internal <a href="/..."> links."""
    out = esc(text)
    out = _re.sub(r'&lt;a href=&quot;(/[^&]*?)&quot;&gt;', r'<a href="\1">', out)
    out = out.replace("&lt;/a&gt;", "</a>")
    return out



def ga_snippet():
    """GA4 only when a real Measurement ID is configured; injected after load so it never blocks render."""
    if not GA4_ID or GA4_ID.startswith("G-XXXX"):
        return "<!-- GA4: set GA4_ID in build.py to enable analytics -->"
    return f"""<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA4_ID}');
window.addEventListener('load',function(){{var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id={GA4_ID}';document.head.appendChild(s);}});</script>"""

def head(title, meta, canonical, schema_blocks):
    schemas = "\n".join(
        f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>'
        for b in schema_blocks)
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(meta)}">
<link rel="canonical" href="{DOMAIN}{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(meta)}">
<meta property="og:url" content="{DOMAIN}{canonical}">
<meta property="og:site_name" content="{BIZ_NAME}">
<meta property="og:image" content="{DOMAIN}/assets/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{DOMAIN}/assets/og-image.jpg">
<meta name="theme-color" content="#0A2540">
<link rel="preload" as="image" href="/assets/hero.webp" fetchpriority="high" media="(min-width: 641px)">
<link rel="preload" as="image" href="/assets/hero-mobile.webp" fetchpriority="high" media="(max-width: 640px)">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
{ga_snippet()}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Inter:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Inter:wght@400;500;600;700&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Inter:wght@400;500;600;700&display=swap"></noscript>
<link rel="stylesheet" href="/assets/styles.css">
{schemas}
</head>
<body>"""

LOGO_SVG = """<svg class="logo-mark" width="34" height="34" viewBox="0 0 34 34" fill="none" aria-hidden="true"><path d="M17 3 3 15h4v14h10v-9h6" stroke="#00A8CC" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M20 24l4 4 8-9" stroke="#0A2540" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none" class="logo-tick"/></svg>"""

NAV_SERVICE_GROUPS = [
    ("Home Clearances", ["end-of-tenancy-clearance", "flat-clearance", "full-house-clearance",
                         "hoarder-house-clearance", "house-clearance", "partial-house-clearance"]),
    ("Probate & Bereavement", ["bereavement-house-clearance", "probate-house-clearance"]),
    ("Spaces & Items", ["garage-clearance", "loft-clearance"]),
]
NAV_AREA_GROUPS = [
    ("Cheshire", ["house-clearance-cheshire", "house-clearance-chester",
                  "house-clearance-crewe", "house-clearance-ellesmere-port",
                  "house-clearance-knutsford", "house-clearance-northwich",
                  "house-clearance-warrington", "house-clearance-widnes",
                  "house-clearance-wilmslow"]),
    ("Merseyside", ["house-clearance-liverpool", "house-clearance-wirral"]),
    ("North Wales", ["house-clearance-north-wales", "house-clearance-buckley", "house-clearance-denbighshire",
                     "house-clearance-flintshire", "house-clearance-mold",
                     "house-clearance-prestatyn", "house-clearance-rhyl",
                     "house-clearance-wrexham"]),
]

def header_nav(active=""):
    p, p164 = cur_phone()
    def a(href, label, key):
        cls = ' class="active"' if key == active else ""
        return f'<a href="{href}"{cls}>{label}</a>'
    chev = '<svg class="nav-chev" width="10" height="10" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m6 9 6 6 6-6" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    def group_col(heading, links):
        items = "".join(links)
        return f'<div class="drop-group"><p class="drop-heading">{esc(heading)}</p>{items}</div>'
    svc_cols = "".join(group_col(h, [f'<a href="{svc_url(sl)}">{esc(SVC[sl]["name"])}</a>'
                                     for sl in sorted(slugs, key=lambda x: SVC[x]["name"])])
                       for h, slugs in NAV_SERVICE_GROUPS)
    area_cols = "".join(group_col(h, [f'<a href="{loc_url(sl)}">{esc(LOC[sl]["short"])}</a>'
                                      for sl in sorted(slugs, key=lambda x: LOC[x]["short"])])
                        for h, slugs in NAV_AREA_GROUPS)
    svc_active = ' class="active"' if active == "services" else ""
    area_active = ' class="active"' if active == "areas" else ""
    return f"""
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a href="/" class="logo" aria-label="{BIZ_NAME} home">{LOGO_SVG}<span>House<em>Clear</em></span></a>
    <nav class="main-nav" id="main-nav" aria-label="Main">
      {a('/', 'Home', 'home')}
      <div class="nav-item has-drop">
        <a href="/services/"{svc_active}>Services {chev}</a>
        <div class="drop-panel" aria-label="Services">
          <div class="drop-cols">{svc_cols}</div>
          <a class="drop-all" href="/services/">All services &rarr;</a>
        </div>
      </div>
      <div class="nav-item has-drop">
        <a href="/areas/"{area_active}>Areas We Cover {chev}</a>
        <div class="drop-panel drop-right" aria-label="Areas we cover">
          <div class="drop-cols">{area_cols}</div>
          <a class="drop-all" href="/areas/">All areas &rarr;</a>
        </div>
      </div>
      {a('/#how-it-works', 'How It Works', 'how')}
      {a('/about/', 'About', 'about')}
      {a('/guides/', 'Guides', 'guides')}
    </nav>
    <div class="header-cta">
      <a class="btn btn-ghost btn-call" href="tel:{p164}">{phone_icon()} Call Today</a>
      <a class="btn btn-primary" href="/quote/">Get a Free Quote</a>
    </div>
    <button class="nav-toggle" aria-expanded="false" aria-controls="main-nav" aria-label="Menu"><span></span><span></span><span></span></button>
  </div>
</header>"""

def phone_icon():
    return '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.6 10.8a15.5 15.5 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.2.4 2.4.6 3.7.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.8 21 3 13.2 3 3.9c0-.6.4-1 1-1h3.4c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.7.1.3 0 .7-.2 1l-2.2 2.2z"/></svg>'

def mail_icon():
    return '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="2.5" y="5" width="19" height="14" rx="2.5" stroke="currentColor" stroke-width="2"/><path d="m3.5 7 8.5 6 8.5-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def wa_icon():
    return '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2c-1.5 0-3-.4-4.3-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.6-6.1c-.3-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1-.2.3-.7.8-.8 1-.1.2-.3.2-.6.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4 0-.4.2-.9l.4-.6c.1-.2 0-.4 0-.5l-.8-1.9c-.2-.5-.4-.4-.6-.4h-.5c-.2 0-.5.1-.7.3-.9.9-1.1 2.2-.2 3.9a12 12 0 0 0 4.6 4.3c1.7.8 2.4.9 3.2.7.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.1-1.2-.1 0-.3-.1-.4 0z"/></svg>'

def compliance_strip():
    items = ["Licensed Waste Carrier", "Fully Insured", "Digital Waste Transfer Notes", "VAT Invoices Provided"]
    lis = "".join(f'<li><svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M20 6 9 17l-5-5" stroke="#00A8CC" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>{i}</li>' for i in items)
    return f'<div class="compliance-strip" role="note" aria-label="Compliance credentials"><ul class="wrap">{lis}</ul></div>'

def key_facts(summary, facts):
    """GEO/LLM answer-first block: a self-contained summary sentence plus
    short factual bullets that generative engines can quote directly."""
    tick = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 13l5 5L20 7" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    lis = "".join(f'<li><span class="kf-tick">{tick}</span>{esc(f)}</li>' for f in facts)
    return f"""<section class="section key-facts-section"><div class="wrap wrap-narrow">
<div class="key-facts" role="note">
<p class="kf-badge">At a glance</p>
<p class="key-facts-summary">{esc(summary)}</p>
<ul class="kf-grid">{lis}</ul>
</div></div></section>"""

def hero_mark(cls="hero-mark"):
    return f"""<svg class="{cls}" viewBox="0 0 34 34" fill="none" aria-hidden="true"><path d="M17 3 3 15h4v14h10v-9h6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M20 24l4 4 8-9" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

def hero(h1, sub, small=False, eyebrow=None, with_form=False):
    p, p164 = cur_phone()
    eb = f'<p class="eyebrow">{esc(eyebrow)}</p>' if eyebrow else ""
    cls = "hero hero-small" if small else "hero"
    if with_form:
        return f"""
<section class="{cls} hero-has-form">
  {hero_mark()}
  <div class="wrap hero-grid">
    <div class="hero-copy">
      {eb}
      <h1>{h1}</h1>
      <p class="hero-sub">{sub}</p>
      <div class="hero-ctas">
        <a class="btn btn-light btn-lg" href="tel:{p164}">{phone_icon()} Call Today</a>
        <a class="btn btn-wa btn-lg" href="{WA_LINK}" rel="noopener">{wa_icon()} WhatsApp</a>
      </div>
      <div class="hero-proof">{google_badge()}<span class="hero-note">Free, no-obligation quotes &middot; usually the same day</span></div>
    </div>
    <div class="hero-form">
      <h2 class="hero-form-title">Get a Free Quote</h2>
      {quote_form(compact=True, prefix="hf")}
    </div>
  </div>
</section>
{compliance_strip()}"""
    return f"""
<section class="{cls}">
  {hero_mark()}
  <div class="wrap hero-inner">
    {eb}
    <h1>{h1}</h1>
    <p class="hero-sub">{sub}</p>
    <div class="hero-ctas">
      <a class="btn btn-primary btn-lg" href="/quote/">Get a Free Quote</a>
      <a class="btn btn-light btn-lg" href="tel:{p164}">{phone_icon()} Call Today</a>
    </div>
    <div class="hero-proof">{google_badge()}<span class="hero-note">Free, no-obligation quotes &middot; usually the same day</span></div>
  </div>
</section>
{compliance_strip()}"""

def breadcrumbs(trail):
    # trail: list of (label, url) — last item is current page (url ignored)
    lis = []
    for i, (label, url) in enumerate(trail):
        if i == len(trail) - 1:
            lis.append(f'<li aria-current="page">{esc(label)}</li>')
        else:
            lis.append(f'<li><a href="{url}">{esc(label)}</a></li>')
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><div class="wrap"><ol>{"".join(lis)}</ol></div></nav>'

def breadcrumb_schema(trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": label,
                 "item": DOMAIN + url}
                for i, (label, url) in enumerate(trail)]}

def faq_section(faqs, title="Frequently asked questions"):
    items = "".join(
        f"""<details class="faq-item"><summary><h3>{esc(q)}</h3><span class="faq-chevron" aria-hidden="true"></span></summary><div class="faq-body"><p>{esc(a)}</p></div></details>"""
        for q, a in faqs)
    return f"""<section class="section faq-section" id="faqs"><div class="wrap wrap-narrow"><h2>{esc(title)}</h2>{items}</div></section>"""

def faq_schema(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in faqs]}

def how_it_works():
    steps = [
        ("Tell us what needs clearing",
         "Send photos or a quick video over WhatsApp, fill in the quote form, or book a free visit. You'll get a clear, fixed price — usually the same day."),
        ("We clear, you relax",
         "Our uniformed, insured team arrives at the time booked, does all the lifting and sorting, and leaves the property swept and tidy."),
        ("Paperwork done properly",
         "Reusable items are donated or recycled, and you receive a digital waste transfer note and VAT invoice for your records."),
    ]
    cards = "".join(
        f'<div class="step-card"><span class="step-num" aria-hidden="true">{i+1}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></div>'
        for i, (t, d) in enumerate(steps))
    return f"""<section class="section section-grey" id="how-it-works"><div class="wrap">
<h2>How it works</h2>
<p class="section-intro">Three simple steps from first photo to finished clearance.</p>
<div class="steps-grid">{cards}</div></div></section>"""

TRUST_ICONS = {
    "licence": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="15" rx="2.5"/><path d="M7 9h6M7 13h3"/><path d="m13.5 14.5 2 2 3.5-4"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l7 3v5.5c0 4.4-3 7.6-7 9.5-4-1.9-7-5.1-7-9.5V6z"/><path d="m8.8 12 2.2 2.2 4.2-4.7"/></svg>',
    "recycle": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4.5 12a7.5 7.5 0 0 1 13-5.2"/><path d="M17.5 3v4h-4"/><path d="M19.5 12a7.5 7.5 0 0 1-13 5.2"/><path d="M6.5 21v-4h4"/></svg>',
    "tag": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.6 12.6 13 20.2a2 2 0 0 1-2.8 0L3.5 13.4A1.7 1.7 0 0 1 3 12.2V5a2 2 0 0 1 2-2h7.2c.4 0 .9.2 1.2.5l7.2 7.3a2 2 0 0 1 0 2.8z"/><circle cx="7.8" cy="7.8" r="1.4"/></svg>',
}

def trust_section():
    points = [
        ("licence", "Licensed waste carrier", "Registered with the Environment Agency. Your waste is our legal responsibility from the moment we load it — and your digital waste transfer note proves it."),
        ("shield", "Fully insured team", "Public liability insurance covers every job, and our uniformed team treats your property — and your neighbours — with respect."),
        ("recycle", "Recycling comes first", "Reusable furniture and goods are donated or resold, recyclables are recovered, and only genuine waste goes for disposal."),
        ("tag", "Clear, honest pricing", "Fixed quotes before we start, VAT invoices on completion, and finance options available on larger clearances where helpful."),
    ]
    cards = "".join(f'<div class="trust-card"><span class="trust-icon">{TRUST_ICONS[i]}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for i, t, d in points)
    return f"""<section class="section" id="why-houseclear"><div class="wrap">
<h2>Why people choose {BIZ_NAME}</h2>
<p class="section-intro">A clearance company you can hand the keys to — and the paperwork to back it up. From <a href="/house-clearance-chester/">house clearance in Chester</a> to <a href="/house-clearance-liverpool/">Liverpool</a>, <a href="/house-clearance-wirral/">the Wirral</a> and <a href="/house-clearance-prestatyn/">the North Wales coast</a>. <a href="/about/">More about HouseClear and our credentials</a>.</p>
<div class="trust-grid">{cards}</div></div></section>"""

def services_grid(slugs=None, title="Our clearance services", intro=None, current=None):
    slugs = slugs or [s["slug"] for s in SERVICES]
    cards = []
    for slug in slugs:
        if slug == current: continue
        s = SVC[slug]
        cards.append(f'<a class="svc-card" href="{svc_url(slug)}"><h3>{esc(s["name"])}</h3><p>{esc(s["lead"])}</p><span class="card-link">Learn more<span aria-hidden="true"> &rarr;</span></span></a>')
    intro_html = f'<p class="section-intro">{esc(intro)}</p>' if intro else ""
    return f"""<section class="section section-grey" id="services"><div class="wrap">
<h2>{esc(title)}</h2>{intro_html}
<div class="svc-grid">{''.join(cards)}</div></div></section>"""

def areas_grid(slugs=None, title="Areas we cover", intro=None, current=None):
    slugs = slugs or [l["slug"] for l in LOCATIONS]
    slugs = sorted(slugs, key=lambda s: LOC[s]["short"])
    chips = []
    for slug in slugs:
        if slug == current: continue
        l = LOC[slug]
        chips.append(f'<a class="area-chip" href="{loc_url(slug)}">{esc(l["short"])}</a>')
    intro_html = f'<p class="section-intro">{esc(intro)}</p>' if intro else ""
    return f"""<section class="section" id="areas"><div class="wrap">
<h2>{esc(title)}</h2>{intro_html}
<div class="area-chips area-chips-even">{''.join(chips)}</div></div></section>"""

# --- Testimonials -----------------------------------------------------------
# IMPORTANT (DMCC Act 2024): the reviews below are PLACEHOLDERS for layout
# only. Replace with genuine, verifiable customer reviews before going live.
# Google rating — update these two numbers as the profile grows
GOOGLE_RATING = "5.0"
GOOGLE_REVIEW_COUNT = 27

# Genuine Google reviews (verbatim; longer ones excerpted). (quote, name, context)
TESTIMONIALS = [
    ("Really professional service from quote to how quickly and efficiently the team cleared the house on the day. The team were friendly and sensitive and cleaned up more than I expected. Highly recommended.", "Wanda Hall", "Google review"),
    ("We needed to clear my late father-in-law's house, which was naturally a very emotional and difficult time for our family. Everyone was so patient, respectful, understanding and professional, and they made what could have been an incredibly stressful and upsetting experience so much easier for us.", "Jane Irlam", "Google review"),
    ("Absolutely delighted to have called the crew at House Clear. 2 days from the initial call and the job was complete, photos supplied on completion. Highly recommend House Clear, professional and compassionate service.", "David Nolan", "Google review"),
    ("Excellent professional supportive team. The flat clearance was efficiently conducted from start to finish! Highly recommended.", "Kay Sheikh", "Google review"),
    ("Absolutely fantastic service from these guys. They have helped me with house clearances as a result of bereavement, renovations, and general waste removal from my home. Steven and the team are so friendly and do a superb job. 10/10.", "Sian Rees-Jones", "Google review"),
    ("House Clear made emptying my Mum's house hassle free after she passed last year. Very friendly and respectful. I have no trouble recommending them to anyone.", "Pamela Lyon", "Google review"),
    ("I have used their service twice. They are efficient, and leave the premises tidy and brushed. Anything you want to keep is set aside or notified about. They are very thorough.", "Peter O'Leary", "Google review"),
    ("Can't fault these guys, they go above and beyond. Exceptional service from start to finish, I would highly recommend them. Top service.", "Jim Bilsland", "Google review"),
    ("Great company to work with. Communication excellent. Great staff. Highly efficient. Good price. Arrived on time. Would highly recommend.", "Elaine Harburn", "Google review"),
    ("House Clear did a great job with a recent house clearance for my family. Their service was efficient and professional. Highly recommend.", "Susan Smith", "Google review"),
    ("Good company. Sorted our clearance. Took everything and left everything tidy.", "Steve Hale", "Google review"),
    ("Excellent service, reasonably priced and helpful guys.", "Tim Braithwaite", "Google review"),
    ("Very professional and thoughtful. Highly recommend.", "Simon Callaghan", "Google review"),
]

def google_badge(cls="google-badge"):
    """Visible on-page rating badge linking to the profile."""
    return f"""<a class="{cls}" href="{GBP_URL}" rel="noopener" aria-label="Rated {GOOGLE_RATING} out of 5 from {GOOGLE_REVIEW_COUNT} Google reviews"><span class="gb-stars" aria-hidden="true">★★★★★</span><span class="gb-text"><strong>{GOOGLE_RATING}</strong> &middot; {GOOGLE_REVIEW_COUNT} Google reviews</span></a>"""

def review_cards(items):
    return "".join(
        f'<figure class="review-card"><div class="stars" aria-label="5 out of 5 stars">★★★★★</div><blockquote>{esc(q)}</blockquote><figcaption><span class="review-avatar" aria-hidden="true">{esc(n[:1])}</span><span><strong>{esc(n)}</strong><span>{esc(w)}</span></span></figcaption></figure>'
        for q, n, w in items)

# Rotation pool: short reviews spaced out so every 3-card window has substance
_SHORT = [t for t in TESTIMONIALS if len(t[0]) < 90]
_LONG  = [t for t in TESTIMONIALS if len(t[0]) >= 90]
ROTATION = []
for _i, _t in enumerate(_LONG):
    ROTATION.append(_t)
    if _i % 3 == 0 and _SHORT: ROTATION.append(_SHORT.pop(0))
ROTATION += _SHORT
BEREAVEMENT_PICKS = [t for t in TESTIMONIALS if t[1] in ("Jane Irlam", "Pamela Lyon", "Sian Rees-Jones")]

def testimonials_section(count=6, offset=0, title="What customers say", items=None):
    if items is None:
        pool = ROTATION[offset:] + ROTATION[:offset]
        items = pool[:count]
    cards = review_cards(items)
    return f"""<section class="section section-navy" id="reviews"><div class="wrap">
<div class="reviews-head"><h2>{esc(title)}</h2>{google_badge("google-badge google-badge-dark")}</div>
<div class="reviews-grid">{cards}</div>
<p class="reviews-more"><a href="{GBP_URL}" rel="noopener">Read all {GOOGLE_REVIEW_COUNT} reviews on Google &rarr;</a></p>
</div></section>"""

def cta_band(heading="Ready for a free, no-obligation quote?",
             sub="Send a few photos and we'll price your clearance today — or call and talk it through with a real person."):
    p, p164 = cur_phone()
    return f"""<section class="cta-band">{hero_mark("hero-mark cta-mark")}<div class="wrap cta-inner">
<div><h2>{esc(heading)}</h2><p>{esc(sub)}</p></div>
<div class="cta-buttons">
  <a class="btn btn-primary btn-lg" href="/quote/">Get a Free Quote</a>
  <a class="btn btn-light btn-lg" href="tel:{p164}">{phone_icon()} Call Today</a>
  <a class="btn btn-wa btn-lg" href="{WA_LINK}" rel="noopener">{wa_icon()} WhatsApp Us</a>
</div></div></section>"""

def quote_form(compact=False, prefix="qf"):
    services_opts = "".join(f'<option>{esc(s["name"])}</option>' for s in SERVICES)
    p = prefix
    return f"""
<form name="quote" method="POST" action="/quote/thanks/" data-netlify="true" netlify-honeypot="company" toolname="request_house_clearance_quote" tooldescription="Request a free, no-obligation house clearance quote from HouseClear. Provide contact details, the property postcode, the service needed and a brief description." class="quote-form{' quote-form-compact' if compact else ''}">
  <input type="hidden" name="form-name" value="quote">
  <p class="hp-field"><label>Company <input name="company" tabindex="-1" autocomplete="off"></label></p>
  <div class="form-grid">
    <div class="field"><label for="{p}-name">Name<span aria-hidden="true"> *</span></label><input id="{p}-name" name="name" type="text" autocomplete="name" toolparamdescription="Your full name" required></div>
    <div class="field"><label for="{p}-phone">Phone number<span aria-hidden="true"> *</span></label><input id="{p}-phone" name="phone" type="tel" autocomplete="tel" toolparamdescription="Best contact phone number" required></div>
    <div class="field"><label for="{p}-email">Email address<span aria-hidden="true"> *</span></label><input id="{p}-email" name="email" type="email" autocomplete="email" toolparamdescription="Email address for the quote" required></div>
    <div class="field"><label for="{p}-postcode">Property postcode<span aria-hidden="true"> *</span></label><input id="{p}-postcode" name="postcode" type="text" autocomplete="postal-code" toolparamdescription="Postcode of the property to be cleared" required></div>
    <div class="field"><label for="{p}-service">Service required</label>
      <select id="{p}-service" name="service" toolparamdescription="Type of clearance required"><option value="">Please choose&hellip;</option>{services_opts}<option>Something else</option></select></div>
    <div class="field"><label for="{p}-contact">Preferred contact method</label>
      <select id="{p}-contact" name="contact_method"><option>Phone call</option><option>WhatsApp</option><option>Email</option><option>Text message</option></select></div>
    <div class="field field-full"><label for="{p}-desc">Brief description</label>
      <textarea id="{p}-desc" name="description" rows="{2 if compact else 4}" placeholder="e.g. 3-bed semi, full clearance including garage. Needed by end of the month."></textarea></div>
  </div>
  <!-- Spam protection: Netlify honeypot is active above. To add Cloudflare
       Turnstile, uncomment the div below, add your site key, and include
       <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script> -->
  <!-- <div class="cf-turnstile" data-sitekey="YOUR_TURNSTILE_SITE_KEY"></div> -->
  <button type="submit" class="btn btn-primary btn-lg btn-block">Request My Free Quote</button>
  <p class="form-privacy">We only use your details to respond to your enquiry. No mailing lists, no nonsense.</p>
</form>"""

def quote_section():
    p, p164 = cur_phone()
    return f"""<section class="section section-grey" id="quote"><div class="wrap quote-wrap">
<div class="quote-copy">
  <h2>Get your free quote</h2>
  <p>Tell us a little about the property and we'll come back with a fixed price — most quotes go back the same day. Photos help us quote fastest: send them straight over on <a href="{WA_LINK}" rel="noopener">WhatsApp</a>.</p>
  <ul class="tick-list">
    <li>Fixed price — what we quote is what you pay</li>
    <li>No obligation and no pushy follow-up calls</li>
    <li>Prefer to talk? Call <a href="tel:{p164}">{p}</a> or <a href="{WA_LINK}" rel="noopener">WhatsApp us</a></li>
  </ul>
</div>
{quote_form()}
</div></section>"""

def map_section():
    embed = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d612246.6995590054!2d-2.78839975!3d53.1714193!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x21ab22d71399804b%3A0xf92566d47187cc5e!2sHouseClear!5e0!3m2!1sen!2suk!4v1786368390889!5m2!1sen!2suk"
    return f"""<section class="section section-grey map-section"><div class="wrap">
<h2>Find HouseClear on Google</h2>
<p class="section-intro">Serving Cheshire, Flintshire, Denbighshire, Liverpool, Wrexham and the Wirral from our Deeside base.</p>
<div class="map-panel"><iframe src="{embed}" title="HouseClear on Google Maps" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>
<div class="map-actions">
  <a class="btn btn-primary" href="{GBP_URL}" rel="noopener">View our Google profile</a>
  <a class="btn btn-ghost" href="{GBP_URL}" rel="noopener">Leave us a review</a>
</div></div></section>"""

def footer():
    p, p164 = cur_phone()
    svc_links = "".join(f'<li><a href="{svc_url(s["slug"])}">{esc(s["name"])}</a></li>' for s in sorted(SERVICES, key=lambda x: x["name"]))
    area_links = "".join(f'<li><a href="{loc_url(l["slug"])}">{esc(l["short"])}</a></li>' for l in sorted(LOCATIONS, key=lambda x: x["short"]))
    return f"""
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <a href="/" class="logo logo-footer">{LOGO_SVG}<span>House<em>Clear</em></span></a>
      <p>Professional, fully compliant house clearance across Cheshire, North Wales, Liverpool and the Wirral.</p>
      <p class="footer-contact">Chester: <a href="tel:{PHONE_E164}">{PHONE}</a><br>Liverpool: <a href="tel:{PHONE2_E164}">{PHONE2}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p class="footer-compliance">Registered waste carrier &middot; Fully insured<br>Digital waste transfer notes with every clearance</p>
    </div>
    <nav aria-label="Services"><h3>Services</h3><ul>{svc_links}</ul></nav>
    <nav aria-label="Areas"><h3>Areas we cover</h3><ul>{area_links}</ul></nav>
  </div>
  <div class="wrap footer-bottom">
    <nav class="footer-utility" aria-label="Footer">
      <a href="/about/">About HouseClear</a>
      <a href="/guides/">Guides &amp; advice</a>
      <a href="/quote/">Get a free quote</a>
      <a href="/services/">All services</a>
      <a href="/areas/">All areas</a>
    </nav>
    <p class="footer-legal">{BIZ_NAME} is a trading name of <a href="https://tidyupltd.com" rel="noopener">Tidy Up Ltd</a>, registered in England and Wales.<br>Registered office: {REG_OFFICE}</p>
    <p class="footer-reg"><span>Company No: {COMPANY_NO}</span><span>VAT No: {VAT_NO}</span><span>Waste Carrier Licence: {WASTE_LIC}</span></p>
    <p class="footer-copy">&copy; 2026 {BIZ_NAME}. All rights reserved.</p>
  </div>
</footer>
<div class="sticky-callbar" role="navigation" aria-label="Quick contact">
  <a href="tel:{p164}" class="scb-call">{phone_icon()} Call Today</a>
  <a href="{WA_LINK}" class="scb-wa" rel="noopener">{wa_icon()} WhatsApp</a>
  <a href="mailto:{EMAIL}" class="scb-email">{mail_icon()} Email</a>
</div>
<script src="/assets/site.js" defer></script>
</body></html>"""

# ---------------------------------------------------------------- schema ---
def local_business_schema():
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "@id": DOMAIN + "/#business",
        "name": BIZ_NAME,
        "legalName": "Tidy Up Ltd",
        "description": "Professional house clearance services across Cheshire, Flintshire, Liverpool, the Wirral and Denbighshire. HouseClear is a trading name of Tidy Up Ltd.",
        "url": DOMAIN + "/",
        "telephone": PHONE_E164,
        "contactPoint": [
            {"@type": "ContactPoint", "telephone": PHONE_E164, "contactType": "customer service", "areaServed": "GB", "name": "Chester"},
            {"@type": "ContactPoint", "telephone": PHONE2_E164, "contactType": "customer service", "areaServed": "GB", "name": "Liverpool"}],
        "email": EMAIL,
        "image": DOMAIN + "/assets/og-image.jpg",
        "priceRange": "££",
        "address": {"@type": "PostalAddress", "streetAddress": "Unit 5 Catherine Court, Manor Lane", "addressLocality": "Hawarden, Deeside", "addressRegion": "Flintshire", "postalCode": "CH5 3NU", "addressCountry": "GB"},
        "vatID": "GB441151045",
        "geo": {"@type": "GeoCoordinates", "latitude": 53.1714193, "longitude": -2.7883998},
        "logo": DOMAIN + "/assets/icon-512.png",
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "House clearance services",
            "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": DOMAIN + svc_url(s["slug"])}} for s in SERVICES]},
        "areaServed": [{"@type": "AdministrativeArea", "name": n} for n in
                       ["Cheshire", "Flintshire", "Liverpool", "Wirral", "Denbighshire", "Wrexham"]],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
            "opens": "08:00", "closes": "18:00"}],
        "slogan": "Respectful, compliant house clearance — with the paperwork to prove it.",
        "knowsAbout": ["House clearance", "Probate house clearance",
                       "Bereavement house clearance", "Hoarder house clearance",
                       "End of tenancy clearance", "Waste transfer notes",
                       "Waste carrier licensing"],
        # Add Facebook / directory profiles here as they're created
        "sameAs": [GBP_URL]
    }

def service_schema(name, desc, url, area=None):
    s = {"@context": "https://schema.org", "@type": "Service",
         "serviceType": name, "name": name, "description": desc,
         "url": DOMAIN + url,
         "provider": {"@id": DOMAIN + "/#business"},
         "areaServed": [{"@type": "AdministrativeArea", "name": n} for n in
                        (["Cheshire","Flintshire","Liverpool","Wirral","Denbighshire","Wrexham"] if not area else [area])]}
    return s

# ----------------------------------------------------------------- pages ---
def write(path, content):
    full = os.path.join(OUT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if BASE and full.endswith(".html"):
        # Preview build: prefix internal root-relative links with the repo path
        content = (content.replace('href="/', f'href="{BASE}/')
                          .replace('src="/', f'src="{BASE}/')
                          .replace('action="/', f'action="{BASE}/'))
        # Keep the preview out of search indexes (avoids duplicate content
        # competing with the live domain)
        if 'name="robots"' not in content:
            content = content.replace("</head>", '<meta name="robots" content="noindex, nofollow">\n</head>', 1)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

def page(url, title, meta, schema_blocks, body, active=""):
    doc = head(title, meta, url, schema_blocks) + header_nav(active) + f'<main id="main">{body}</main>' + footer()
    write(url.rstrip("/") + "/index.html" if url != "/" else "/index.html", doc)
    return url

URLS = []

def homepage():
    body = hero(
        "Professional <span class='hl'>House Clearance</span> Services",
        f"{BIZ_NAME} provides respectful, efficient and fully compliant house clearances across Cheshire, North Wales, Liverpool and the Wirral — for homeowners, landlords, estate agents, solicitors and families dealing with probate or bereavement.",
        with_form=True)
    body += trust_section()
    body += services_grid(intro="From single-item collections to complete house clearances — every job insured, documented and disposed of responsibly. We handle house clearances of every kind across the region.")
    body += areas_grid(intro="Local teams covering Cheshire, Flintshire, Denbighshire, Liverpool, Wrexham and the Wirral.")
    body += how_it_works()
    body += testimonials_section(items=TESTIMONIALS[:6])
    home_faqs = [
        ("How do I get a house clearance quote?", "Send a few photos over WhatsApp, use our quote form, or book a free visit. We price by volume and confirm a fixed quote — usually the same day — with no obligation."),
        ("Are you licensed and insured?", "Yes. HouseClear is a registered waste carrier with full public liability insurance, and every clearance comes with a digital waste transfer note and a VAT invoice."),
        ("What happens to the items you clear?", "Reusable furniture and household goods are donated to local charities or resold, recyclables are recovered at licensed facilities, and only genuine waste goes for disposal."),
        ("Which areas do you cover?", "Cheshire, Flintshire, Denbighshire, Liverpool, Wrexham and the whole Wirral peninsula — including Chester, Ellesmere Port, Northwich, Mold, Rhyl and Prestatyn."),
        ("Can you help with probate or bereavement clearances?", "Yes — sensitively and at your pace. We set aside keepsakes and documents as we work, liaise with solicitors where needed, and provide paperwork suitable for estate accounting."),
        ("Do you offer finance on larger clearances?", "On larger jobs, yes — spread-cost options are available where relevant. Ask when you enquire and we will explain what applies to your clearance."),
    ]
    body += faq_section(home_faqs)
    body += quote_section()
    body += map_section()
    body += cta_band()
    schemas = [
        local_business_schema(),
        {"@context": "https://schema.org", "@type": "WebSite", "name": BIZ_NAME,
         "url": DOMAIN + "/"},
        faq_schema(home_faqs),
    ]
    URLS.append(page("/", 
        "House Clearance Chester, Cheshire & North Wales | HouseClear",
        "Professional, fully insured house clearance across Cheshire, Flintshire, Denbighshire, Liverpool & the Wirral. Licensed waste carrier. Free quotes.",
        schemas, body, active="home"))

def services_hub():
    body = hero("House Clearance Services",
                "Every clearance service under one roof — insured, licensed and documented, from single items to complete properties.",
                small=True, eyebrow="Our services")
    trail = [("Home", "/"), ("Services", "/services/")]
    body = breadcrumbs(trail) + body
    body += services_grid(title="Choose a service", intro="Each service page explains what's included, how pricing works and answers the questions we're asked most.")
    body += how_it_works()
    body += areas_grid()
    body += cta_band("Not sure which service you need?", "Describe the job in a sentence or two and we'll point you the right way — no obligation.")
    URLS.append(page("/services/",
        "House Clearance Services | HouseClear",
        "HouseClear's services: full and partial house clearance, probate and bereavement clearances, hoarder, garage, loft and flat clearances.",
        [breadcrumb_schema(trail)], body, active="services"))

def areas_hub():
    body = hero("Areas We Cover",
                "Local house clearance teams across Cheshire, North Wales, Liverpool and the Wirral — with same-day quotes wherever you are.",
                small=True, eyebrow="Coverage")
    trail = [("Home", "/"), ("Areas We Cover", "/areas/")]
    body = breadcrumbs(trail) + body
    body += areas_grid(title="Find your area", intro="Every area page covers local response times, the neighbourhoods we serve and answers to common local questions.")
    body += services_grid()
    body += cta_band("Just outside these areas?", "We often travel a little further for full clearances — ask and we'll tell you straight away if we can help.")
    URLS.append(page("/areas/",
        "Areas We Cover | HouseClear House Clearance",
        "HouseClear covers Cheshire, Flintshire, Denbighshire, Liverpool, Wrexham and the Wirral — including Chester, Northwich, Mold, Rhyl and Prestatyn.",
        [breadcrumb_schema(trail)], body, active="areas"))

def service_pages():
    for sidx, s in enumerate(SERVICES):
        url = svc_url(s["slug"])
        trail = [("Home", "/"), ("Services", "/services/"), (s["name"], url)]
        body = breadcrumbs(trail)
        body += hero(esc(s["h1"]), esc(s["lead"]), small=True, eyebrow="Clearance services")
        body += key_facts(
            f"HouseClear provides {s['name'].lower()} across Cheshire, Flintshire, Denbighshire, Liverpool, Wrexham and the Wirral, with fixed quotes usually provided the same day.",
            ["Registered waste carrier — digital waste transfer note with every job",
             "Fully insured, uniformed local team",
             "Fixed quotes from photos, a description or a free visit",
             "Reusable items donated, resold or recycled before anything is disposed of",
             "VAT invoices provided; finance available on larger clearances"])
        intro = "".join(f"<p>{esc(p)}</p>" for p in s["intro"])
        includes = "".join(f"<li>{esc(i)}</li>" for i in s["includes"])
        body += f"""<section class="section"><div class="wrap wrap-narrow svc-detail">
{intro}
<h2>What's included</h2>
<ul class="tick-list tick-list-lg">{includes}</ul>
</div></section>"""
        body += how_it_works()
        if s["slug"] in ("bereavement-house-clearance", "probate-house-clearance"):
            body += testimonials_section(items=BEREAVEMENT_PICKS)
        elif s["slug"] == "flat-clearance":
            body += testimonials_section(items=[t for t in TESTIMONIALS if t[1] in ("Kay Sheikh", "Wanda Hall", "David Nolan")])
        else:
            body += testimonials_section(count=3, offset=(sidx*3) % len(ROTATION))
        body += faq_section(s["faqs"], f"{s['name']} — your questions answered")
        rel = "".join(f'<a class="area-chip" href="{svc_url(r)}">{esc(SVC[r]["name"])}</a>' for r in s["related"])
        body += f"""<section class="section"><div class="wrap"><h2>Related services</h2><div class="area-chips">{rel}</div></div></section>"""
        body += related_guides_chips(s["slug"])
        body += areas_grid(title=f"{s['name']} — areas we cover",
                           intro="Available across our whole coverage area. Choose your location for local details.")
        body += cta_band(f"Need {s['name'].lower()}? Get a free quote today.",
                         "Photos or a quick description are all we need — most quotes go back the same day.")
        schemas = [service_schema(s["name"], s["meta"], url),
                   faq_schema(s["faqs"]),
                   breadcrumb_schema(trail)]
        URLS.append(page(url, s["title"], s["meta"], schemas, body, active="services"))

def location_pages():
    global _PHONE_OVERRIDE
    for idx, l in enumerate(sorted(LOCATIONS, key=lambda x: x['short'])):
        _PHONE_OVERRIDE = (PHONE2, PHONE2_E164) if l["slug"] in ("house-clearance-liverpool", "house-clearance-wirral", "house-clearance-widnes") else None
        url = loc_url(l["slug"])
        trail = [("Home", "/"), ("Areas We Cover", "/areas/"), (f"House Clearance {l['short']}", url)]
        body = breadcrumbs(trail)
        body += hero(esc(l["h1"]),
                     f"Respectful, fully compliant house clearances across {esc(l['place'])} — free quotes, usually the same day.",
                     small=True, eyebrow=f"Local to {l['short']}")
        towns_sample = ", ".join(l["towns"][:4])
        body += key_facts(
            f"HouseClear provides full and partial house clearances throughout {l['place']}, including {towns_sample}, with quotes usually provided the same day.",
            [f"Local team covering the whole of {l['place']}",
             "Registered waste carrier — digital waste transfer note with every clearance",
             "Fully insured; probate, bereavement, landlord and hoarder clearances handled",
             "Reusable furniture donated to local charities where possible",
             "Fixed quotes from photos or a free, no-obligation visit"])
        intro = "".join(f"<p>{esc_keep_links(p)}</p>" for p in l["intro"])
        towns = "".join(f"<li>{esc(t)}</li>" for t in sorted(l["towns"]))
        parent = ""
        if l.get("county"):
            c = LOC[l["county"]]
            parent = f'<p class="parent-link">Part of our wider coverage of <a href="{loc_url(c["slug"])}">{esc(c["short"])}</a>.</p>'
        body += f"""<section class="section"><div class="wrap wrap-narrow svc-detail">
{intro}
<h2>Neighbourhoods and villages we cover</h2>
<ul class="town-list">{towns}</ul>
{parent}
</div></section>"""
        body += services_grid(title=f"Clearance services in {l['short']}",
                              intro=f"Every HouseClear service is available in {l['short']} — these are the ones booked most often here.")
        body += how_it_works()
        body += testimonials_section(count=3, offset=(idx*3) % len(ROTATION))
        body += faq_section(l["faqs"], f"House clearance in {l['short']} — common questions")
        rel = "".join(f'<a class="area-chip" href="{loc_url(r)}">{esc(LOC[r]["short"])}</a>' for r in l["related_locations"])
        body += f"""<section class="section"><div class="wrap"><h2>Nearby areas we cover</h2><div class="area-chips">{rel}<a class="area-chip area-chip-all" href="/areas/">All areas &rarr;</a></div></div></section>"""
        loc_guides = ["how-much-does-a-house-clearance-cost", "what-happens-to-belongings-after-a-house-clearance", "house-clearance-vs-skip-hire", "how-to-check-a-waste-carrier-licence", "clearing-a-house-during-probate"]
        gchips = "".join(f'<a class="area-chip" href="{guide_url(gg)}">{esc(GDE[gg]["h1"])}</a>' for gg in loc_guides)
        body += f"""<section class="section section-grey"><div class="wrap"><h2>Helpful guides</h2><p class="section-intro">Planning a clearance in {esc(l['short'])}? These plain-English guides answer the questions we're asked most.</p><div class="area-chips">{gchips}<a class="area-chip area-chip-all" href="/guides/">All guides &rarr;</a></div></div></section>"""
        body += cta_band(f"Book your house clearance in {l['short']}",
                         f"Send photos for a same-day fixed quote, or call to talk it through — we're local to {l['short']}.")
        schemas = [service_schema(f"House Clearance {l['short']}", l["meta"], url, area=l["short"]),
                   faq_schema(l["faqs"]),
                   breadcrumb_schema(trail)]
        URLS.append(page(url, l["title"], l["meta"], schemas, body, active="areas"))
    _PHONE_OVERRIDE = None

def quote_page():
    trail = [("Home", "/"), ("Get a Quote", "/quote/")]
    body = breadcrumbs(trail)
    body += hero("Get a Free House Clearance Quote",
                 "Fixed prices, no obligation and no pushy follow-ups. Photos help us quote fastest — most quotes go back the same day.",
                 small=True, eyebrow="Free quotes")
    body += f"""<section class="section"><div class="wrap quote-wrap">
<div class="quote-copy">
  <h2>Three ways to get your price</h2>
  <ul class="tick-list tick-list-lg">
    <li><strong>Use the form</strong> — tell us about the property and we'll reply with a fixed quote, usually within hours.</li>
    <li><strong>WhatsApp us</strong> — the fastest option if you have photos: send them straight from your phone to <a href="{WA_LINK}" rel="noopener">our WhatsApp</a>.</li>
    <li><strong>Call us</strong> — Chester <a href="tel:{PHONE_E164}">{PHONE}</a> or Liverpool <a href="tel:{PHONE2_E164}">{PHONE2}</a>, Monday to Saturday, 8am–6pm.</li>
  </ul>
  <p>Every quote is fixed, itemised where helpful, and comes with our compliance credentials — waste carrier registration, insurance, and digital waste transfer notes on completion.</p>
</div>
{quote_form()}
</div></section>"""
    body += trust_section()
    body += map_section()
    URLS.append(page("/quote/",
        "Get a Free House Clearance Quote | HouseClear",
        "Get a fixed house clearance quote today. Send photos via our form or WhatsApp, or call us — covering Cheshire, North Wales, Liverpool & the Wirral.",
        [breadcrumb_schema(trail)], body, active="quote"))

def thanks_page():
    body = f"""<section class="hero hero-small"><div class="wrap hero-inner">
<h1>Thanks — we've got your enquiry</h1>
<p class="hero-sub">We'll come back to you shortly with your quote, using your preferred contact method. If it's urgent, call us now on <a href="tel:{PHONE_E164}" style="color:#fff;text-decoration:underline">{PHONE}</a>.</p>
<div class="hero-ctas"><a class="btn btn-light btn-lg" href="/">Back to homepage</a></div>
</div></section>{compliance_strip()}"""
    doc = ('<meta name="robots" content="noindex">').join
    full = head("Enquiry received | HouseClear", "Thanks — your quote request has been received.", "/quote/thanks/", [])
    full = full.replace("</head>", '<meta name="robots" content="noindex">\n</head>')
    write("/quote/thanks/index.html", full + header_nav("quote") + f'<main id="main">{body}</main>' + footer())

def about_page():
    trail = [("Home", "/"), ("About HouseClear", "/about/")]
    body = breadcrumbs(trail)
    body += hero("About HouseClear",
                 "Who we are, how we work, and the credentials behind every clearance.",
                 small=True, eyebrow="About us")
    body += f"""<section class="section"><div class="wrap wrap-narrow svc-detail">
<p><strong>HouseClear is a professional house clearance company serving Cheshire, Flintshire, Denbighshire, Liverpool, Wrexham and the Wirral.</strong> HouseClear is a trading name of Tidy Up Ltd, an established Chester-based clearance and waste management company — so behind the HouseClear name sits an experienced team, existing insurance, and a current Environment Agency waste carrier registration held by Tidy Up Ltd. We clear houses, flats, garages, lofts and commercial-adjacent domestic properties for homeowners, landlords, estate agents, solicitors and families dealing with probate or bereavement.</p>
<h2>Our credentials</h2>
<ul class="tick-list tick-list-lg">
<li><strong>Registered waste carrier</strong> — Environment Agency registration <strong>CBDU464597</strong> (held by Tidy Up Ltd), valid for our work in both England and Wales, and verifiable on the public register.</li>
<li><strong>Fully insured</strong> — public liability insurance covers every clearance we carry out, and certificates are supplied to agents, solicitors and housing providers on request.</li>
<li><strong>Digital waste transfer notes</strong> — every clearance is documented with a digital waste transfer note, giving you legal proof of correct disposal.</li>
<li><strong>VAT registered</strong> — VAT invoices are provided on completion (VAT No. 441151045), and can be addressed to an estate for probate accounting.</li>
</ul>
<h2>Part of the Tidy Up Ltd family</h2>
<p>HouseClear is one of several trading names of <a href="https://tidyupltd.com" rel="noopener">Tidy Up Ltd</a>, a Deeside-based clearance and waste management company. For general waste removal and rubbish collection rather than a property clearance, our sister brand <a href="https://clearwaste.uk" rel="noopener">ClearWaste</a> handles that side of the business — same team, same licence, same paperwork. Whichever brand you contact, you are dealing with the same established local company.</p>
<h2>How we handle what we clear</h2>
<p>Every load is sorted before disposal. Reusable furniture and household goods are donated to charities local to the clearance or resold; metals, timber, cardboard and other recyclables are recovered at licensed transfer stations; only genuine waste goes for disposal. Where contents have resale value, that value is offset against your quote.</p>
<h2>Who we work with</h2>
<p>Alongside private households, HouseClear works directly with solicitors and probate professionals, letting agents and landlords, estate agents preparing properties for sale, and housing providers turning around void properties. We are used to being someone's contractor of record — supplying compliance documents up front, working to completion dates, and invoicing on account where needed.</p>
<h2>Where we work</h2>
<p>Our teams cover Chester, Ellesmere Port and Northwich across Cheshire; Mold, Buckley and Deeside in Flintshire; Rhyl, Prestatyn, Denbigh and Ruthin in Denbighshire; Wrexham and its villages; the whole of Liverpool; and the Wirral peninsula from Birkenhead to West Kirby. See our <a href="/areas/">areas page</a> for local details.</p>
</div></section>"""
    body += trust_section()
    body += testimonials_section(items=TESTIMONIALS[:6])
    body += map_section()
    body += cta_band("Want our licence and insurance details?", "Ask with your quote — we supply compliance documents to every client who wants them, before any work begins.")
    schemas = [
        {"@context": "https://schema.org", "@type": "AboutPage",
         "name": "About HouseClear", "url": DOMAIN + "/about/",
         "mainEntity": {"@id": DOMAIN + "/#business"}},
        breadcrumb_schema(trail)]
    URLS.append(page("/about/",
        "About HouseClear | Licensed Clearance Specialists",
        "HouseClear is a registered waste carrier providing insured, fully documented house clearances across Cheshire, North Wales, Liverpool and the Wirral.",
        schemas, body, active="about"))

def llms_txt():
    """llms.txt — a plain-text/markdown map of the site for LLM crawlers
    (https://llmstxt.org). Helps generative engines summarise and cite the
    business accurately."""
    svc_lines = "\n".join(f"- [{s['name']}]({DOMAIN}{svc_url(s['slug'])}): {s['lead']}" for s in SERVICES)
    loc_lines = "\n".join(f"- [House Clearance {l['short']}]({DOMAIN}{loc_url(l['slug'])}): {l['meta']}" for l in LOCATIONS)
    guide_lines = "\n".join(f"- [{g['h1']}]({DOMAIN}{guide_url(g['slug'])}): {g['meta']}" for g in GUIDES)
    write("/llms.txt", f"""# {BIZ_NAME}

> {BIZ_NAME} is a professional house clearance company covering Cheshire, Flintshire, Denbighshire, Liverpool, Wrexham and the Wirral (UK). Registered waste carrier, fully insured. Every clearance includes a digital waste transfer note and VAT invoice. Reusable items are donated, resold or recycled before disposal. Fixed quotes from photos, usually the same day. Phone: {PHONE} (Chester) or {PHONE2} (Liverpool). Website: {DOMAIN}/

Key facts:
- Services: full and partial house clearance, probate and bereavement clearance, hoarder clearance, garage, loft and flat clearance, end of tenancy clearance
- Clients: homeowners, landlords, letting and estate agents, solicitors, executors, housing providers
- Compliance: Environment Agency registered waste carrier (England & Wales), public liability insured, digital waste transfer notes, VAT invoices; finance available on larger clearances
- Coverage: Chester, Ellesmere Port, Northwich, Mold, Buckley, Deeside, Wrexham, Rhyl, Prestatyn, Denbigh, Ruthin, Liverpool, Birkenhead, Wallasey, Heswall, West Kirby and surrounding areas
- Google Business Profile: {GBP_URL}
- Legal entity: HouseClear is a trading name of Tidy Up Ltd (Company No. 14294404, registered office Hawarden, Deeside CH5 3NU); Environment Agency waste carrier registration CBDU464597

## Services
{svc_lines}

## Areas covered
{loc_lines}

## Guides
{guide_lines}

## Company
- [About HouseClear]({DOMAIN}/about/): credentials, disposal process and who we work with
- [Get a free quote]({DOMAIN}/quote/): fixed quotes from photos, phone or WhatsApp
""")

def related_guides_chips(svc_slug):
    slugs = SVC_GUIDES.get(svc_slug, [])
    if not slugs: return ""
    chips = "".join(f'<a class="area-chip" href="{guide_url(g)}">{esc(GDE[g]["h1"])}</a>' for g in slugs)
    return f"""<section class="section section-grey"><div class="wrap"><h2>Helpful guides</h2><div class="area-chips">{chips}<a class="area-chip area-chip-all" href="/guides/">All guides &rarr;</a></div></div></section>"""

def article_schema(g):
    return {"@context": "https://schema.org", "@type": "Article",
            "headline": g["h1"], "description": g["meta"],
            "url": DOMAIN + guide_url(g["slug"]),
            "datePublished": g["date"], "dateModified": g["date"],
            "image": [DOMAIN + "/assets/og-image.jpg"],
            "author": {"@type": "Organization", "name": BIZ_NAME, "url": DOMAIN + "/"},
            "publisher": {"@id": DOMAIN + "/#business"}}

def guides_hub():
    trail = [("Home", "/"), ("Guides", "/guides/")]
    body = breadcrumbs(trail)
    body += hero("House Clearance Guides &amp; Advice",
                 "Plain-English guides to clearance costs, probate, paperwork and choosing the right option — written by the team that does the work.",
                 small=True, eyebrow="Guides")
    for cluster, slugs in GUIDE_CLUSTERS:
        cards = "".join(
            f'<a class="svc-card" href="{guide_url(s)}"><h3>{esc(GDE[s]["h1"])}</h3><p>{esc(GDE[s]["lead"])}</p><span class="card-link">Read the guide<span aria-hidden="true"> &rarr;</span></span></a>'
            for s in slugs)
        body += f"""<section class="section"><div class="wrap"><h2>{esc(cluster)}</h2><div class="svc-grid">{cards}</div></div></section>"""
    body += services_grid(title="Ready to book instead?",
                          intro="Every guide links to the service it describes — or jump straight to the service you need.")
    body += cta_band("Prefer to just ask?", "Whatever the question — timing, paperwork, price — call or message and we'll give you a straight answer.")
    URLS.append(page("/guides/",
        "House Clearance Guides & Advice | HouseClear",
        "Plain-English house clearance guides: costs, probate, waste transfer notes, checking a waste carrier licence, and clearance vs skip hire.",
        [breadcrumb_schema(trail)], body, active="guides"))

def guide_pages():
    for g in GUIDES:
        url = guide_url(g["slug"])
        trail = [("Home", "/"), ("Guides", "/guides/"), (g["h1"], url)]
        body = breadcrumbs(trail)
        body += hero(esc(g["h1"]), esc(g["lead"]), small=True, eyebrow=g["cluster"])
        sections = []
        for h2, paras in g["body"]:
            if h2: sections.append(f"<h2>{esc(h2)}</h2>")
            sections.extend(f"<p>{p}</p>" for p in paras)  # raw HTML: carries contextual links
        body += f"""<section class="section"><div class="wrap wrap-narrow svc-detail guide-body">{''.join(sections)}</div></section>"""
        body += faq_section(g["faqs"], "Related questions")
        svc_chips = "".join(f'<a class="area-chip" href="{svc_url(s)}">{esc(SVC[s]["name"])}</a>' for s in g["related_services"])
        others = [o for c, sl in GUIDE_CLUSTERS for o in sl if c == g["cluster"] and o != g["slug"]]
        guide_chips = "".join(f'<a class="area-chip" href="{guide_url(o)}">{esc(GDE[o]["h1"])}</a>' for o in others)
        body += f"""<section class="section"><div class="wrap"><h2>Related services</h2><div class="area-chips">{svc_chips}</div></div></section>"""
        if guide_chips:
            body += f"""<section class="section section-grey"><div class="wrap"><h2>More in {esc(g["cluster"])}</h2><div class="area-chips">{guide_chips}<a class="area-chip area-chip-all" href="/guides/">All guides &rarr;</a></div></div></section>"""
        body += cta_band("Got a clearance to arrange?", "Free fixed quotes, usually the same day — photos over WhatsApp are the fastest route.")
        schemas = [article_schema(g), faq_schema(g["faqs"]), breadcrumb_schema(trail)]
        URLS.append(page(url, g["title"], g["meta"], schemas, body, active="guides"))

def sitemap_and_robots():
    urls = "".join(f"<url><loc>{DOMAIN}{u}</loc></url>" for u in URLS)
    write("/sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    ai_bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "Bingbot", "CCBot", "meta-externalagent", "Claude-Web", "anthropic-ai", "Amazonbot", "Bytespider"]
    ai_rules = "\n\n".join(f"User-agent: {b}\nAllow: /" for b in ai_bots)
    write("/robots.txt", f"""# Standard crawlers
User-agent: *
Allow: /
Disallow: /quote/thanks/

# AI / generative engine crawlers — explicitly allowed so the business can
# be cited in AI Overviews, ChatGPT, Claude, Perplexity etc.
{ai_rules}

Sitemap: {DOMAIN}/sitemap.xml
""")

def assets():
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    shutil.copy(os.path.join(os.path.dirname(__file__), "styles.css"), os.path.join(OUT, "assets/styles.css"))
    shutil.copy(os.path.join(os.path.dirname(__file__), "site.js"), os.path.join(OUT, "assets/site.js"))
    brand = os.path.join(os.path.dirname(__file__), "brand")
    for f in ["favicon.svg", "favicon.ico", "apple-touch-icon.png", "icon-192.png", "icon-512.png", "og-image.jpg", "hero.webp", "hero-mobile.webp"]:
        shutil.copy(os.path.join(brand, f), os.path.join(OUT, "assets", f))

if __name__ == "__main__":
    if os.path.exists(OUT): shutil.rmtree(OUT)
    homepage()
    services_hub()
    areas_hub()
    service_pages()
    location_pages()
    quote_page()
    thanks_page()
    about_page()
    guides_hub()
    guide_pages()
    llms_txt()
    sitemap_and_robots()
    assets()
    print(f"Built {len(URLS)} indexable pages into {OUT}")
    for u in URLS: print("  ", u)
