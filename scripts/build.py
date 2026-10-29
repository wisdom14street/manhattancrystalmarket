#!/usr/bin/env python3
"""Build the Manhattan Crystal Market static site into ./dist from data/all_products.json.
Usage: python3 scripts/build.py [--preview]   (--preview adds noindex everywhere)
"""
import json, os, re, sys, html, shutil, datetime
sys.path.insert(0, os.path.dirname(__file__))
from catmap import CATS, category

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DIST = os.path.join(ROOT, 'dist')
PREVIEW = '--preview' in sys.argv or os.environ.get('MCM_PREVIEW') == '1'
SITE = os.environ.get('MCM_SITE_URL', 'https://manhattancrystalmarket.com').rstrip('/')
# Base path for hosting under a subfolder, e.g. GitHub Pages project sites: --base=/manhattancrystalmarket
BASE = os.environ.get('MCM_BASE_PATH', '')
for a in sys.argv:
    if a.startswith('--base='): BASE = a.split('=', 1)[1]
    if a.startswith('--site='): SITE = a.split('=', 1)[1].rstrip('/')
BASE = ('/' + BASE.strip('/')) if BASE.strip('/') else ''
SHOP = 'https://namastebookshop.com'
BRAND = 'Manhattan Crystal Market'
LEGAL = 'Manhattan Crystal Market is a brand of Wealth Edge Ventures Inc.'
# ---- store visit details (verified Oct 29, 2026) ----
# Address + hours: namastebookshop.com/pages/contact. Pickup: Shopify Local Pickup section on namastebookshop.com.
# Phone: Crystal Shop line provided by the owner. Transit/distance: MTA + OpenStreetMap geocode (see README).
STORE_STREET = '2 West 14th Street'
STORE_CITY, STORE_REGION, STORE_ZIP = 'New York', 'NY', '10011'
STORE_ADDR = f'{STORE_STREET}, {STORE_CITY}, {STORE_REGION} {STORE_ZIP}'
PHONE, TEL = '646-876-1401', '+16468761401'
GEO = (40.73602, -73.99404)
HOURS = [('Monday to Thursday', '11 AM to 8 PM'), ('Friday and Saturday', '11 AM to 9 PM'), ('Sunday', '11 AM to 7 PM')]
HOURS_LD = [(['Monday', 'Tuesday', 'Wednesday', 'Thursday'], '11:00', '20:00'), (['Friday', 'Saturday'], '11:00', '21:00'), (['Sunday'], '11:00', '19:00')]
MAP_Q = '2+West+14th+Street,+New+York,+NY+10011'
MAP_EMBED = f'https://www.google.com/maps/embed?origin=mfe&pb=!1m3!2m1!1s{MAP_Q}!6i16'
MAP_LINK = f'https://www.google.com/maps/search/?api=1&query={MAP_Q}'
DIRECTIONS = f'https://www.google.com/maps/dir/?api=1&destination={MAP_Q}'
READINGS = 'https://namastebookshop.com/pages/book-a-reading'
CART_ATTR = '?attributes%5BStorefront%5D=Manhattan%20Crystal%20Market'
E = html.escape

CAT_SLUG = {'towers': 'towers-points', 'clusters': 'clusters-geodes', 'specimens': 'specimens-raw',
            'tumbled': 'tumbled-pocket-stones', 'carvings': 'spheres-hearts-carvings', 'jewelry': 'crystal-jewelry'}
CAT_BLURB = {
 'towers': 'Standing towers, generators, obelisks and natural points, from palm-sized to statement pieces.',
 'clusters': 'Druzy clusters, geodes and gem trees that catch the light on a shelf or desk.',
 'specimens': 'One-of-a-kind mineral specimens, raw rough, slabs and free forms for collectors.',
 'tumbled': 'Tumbled stones, palm stones, worry stones and cubes made to be carried and handled.',
 'carvings': 'Polished spheres, hearts, eggs, skulls, pyramids and hand-carved figures.',
 'jewelry': 'Beaded bracelets, pendants, necklaces, rings and earrings set with real stones.',
}
CAT_SHORT = {'towers': 'Towers', 'clusters': 'Clusters', 'specimens': 'Specimens', 'tumbled': 'Pocket Stones',
             'carvings': 'Carvings', 'jewelry': 'Jewelry'}
CAT_COLOR = {'towers': '#7b5cff', 'clusters': '#2fb39a', 'specimens': '#e0913a', 'tumbled': '#e2557a',
             'carvings': '#3c8be0', 'jewelry': '#c9a227'}

STONES = [
 ('Rose Quartz', r'rose quartz'), ('Clear Quartz', r'clear quartz|crystal quartz|quartz crystal'),
 ('Smoky Quartz', r'smok(e)?y quartz'), ('Aura Quartz', r'\baura\b|angel aura|titanium'),
 ('Amethyst', r'amethyst'), ('Citrine', r'citrine'), ("Tiger's Eye", r"tiger'?s? ?eye"),
 ('Moonstone', r'moonstone'), ('Tourmaline', r'tourmaline'), ('Obsidian', r'obsidian'),
 ('Pyrite', r'pyrite'), ('Malachite', r'malachite'), ('Lapis Lazuli', r'lapis'),
 ('Fluorite', r'fluorite'), ('Labradorite', r'labradorite'), ('Aquamarine', r'aquamarine'),
 ('Agate', r'agate'), ('Jasper', r'jasper'), ('Kyanite', r'kyanite'), ('Garnet', r'garnet'),
 ('Jade', r'\bjade\b'), ('Hematite', r'hematite'), ('Carnelian', r'carnelian'),
 ('Moldavite', r'moldavite'), ('Selenite', r'selenite'), ('Aventurine', r'aventurine'),
 ('Rhodochrosite', r'rhodochrosite'), ('Labradorite', r'labradorite'), ('Shungite', r'shungite'),
 ('Lepidolite', r'lepidolite'), ('Turquoise', r'turquoise'), ('Chrysocolla', r'chrysocolla'),
 ('Quartz', r'quartz'),
]
ORIGINS = ['Brazil', 'Madagascar', 'India', 'Peru', 'Pakistan', 'Congo', 'Mexico', 'Morocco', 'Uruguay',
           'South Africa', 'Russia', 'Afghanistan', 'Afganistan', 'Indonesia', 'Argentina', 'China', 'Nepal',
           'Czech Republic', 'Namibia', 'Arkansas', 'Bolivia', 'Australia', 'Canada', 'Tanzania', 'Zambia']

def stone_of(title):
    t = title.lower()
    for name, rx in STONES:
        if re.search(rx, t):
            return name
    return 'Other'

def origin_of(title):
    for o in ORIGINS:
        if re.search(r'\b' + o + r'\b', title, re.I):
            return 'Afghanistan' if o == 'Afganistan' else o
    return None

def img(url, w):
    if not url: return ''
    sep = '&' if '?' in url else '?'
    return f"{url}{sep}width={w}"

def money(s):
    v = float(s)
    return f"${v:,.2f}"

def describe(p, cat, stone, origin):
    """Original, factual copy; no claims beyond what the title states."""
    kind = {'towers': 'tower or point', 'clusters': 'cluster', 'specimens': 'specimen',
            'tumbled': 'hand-sized stone', 'carvings': 'polished carving', 'jewelry': 'piece of jewelry'}[cat]
    s = []
    stn = f"{stone.lower()} " if stone not in ('Other', 'Quartz') else ''
    s.append(f"{E(p['title'])} is a {stn}{kind} chosen for the {BRAND} collection.")
    if origin:
        s.append(f"Sourced from {origin}, as listed in its title.")
    if cat == 'jewelry':
        s.append("Natural stones are never identical, so expect small differences in color, pattern and bead size from the photo.")
    elif cat in ('specimens', 'clusters'):
        s.append("Every mineral grows differently, so color, shape and size vary from piece to piece.")
    else:
        s.append("Because each stone is natural, color, banding and size vary slightly from piece to piece.")
    s.append(f"Ships from New York City, or see our crystal floor in person at {STORE_STREET}, near Union Square. Secure checkout is completed on Shopify.")
    return s

# ---------- data ----------
raw = json.load(open(os.path.join(ROOT, 'data', 'all_products.json')))
products = []
for p in raw:
    cat = category(p)
    if not cat or not p.get('images'):
        continue
    vs = [v for v in p['variants'] if float(v['price']) > 0]
    if not any(v['available'] for v in vs):
        continue
    stone = stone_of(p['title'])
    origin = origin_of(p['title'])
    avail = [v for v in vs if v['available']]
    price = min(float(v['price']) for v in avail)
    cmp_ = [float(v['compare_at_price']) for v in avail if v.get('compare_at_price') and float(v['compare_at_price']) > float(v['price'])]
    products.append({
        'id': p['id'], 'handle': p['handle'], 'title': p['title'].strip(), 'cat': cat, 'stone': stone,
        'origin': origin, 'type': p['product_type'], 'price': price,
        'compare': max(cmp_) if cmp_ else None,
        'images': [i['src'] for i in p['images'][:6]],
        'variants': [{'id': v['id'], 'title': v['title'], 'price': v['price'], 'available': v['available'],
                      'sku': v.get('sku') or ''} for v in vs],
        'created': p.get('created_at', ''),
    })
products.sort(key=lambda x: x['created'], reverse=True)
_pk = os.path.join(ROOT, 'data', 'pickup.json')
PICKUP = json.load(open(_pk)) if os.path.exists(_pk) else {}
def pickup_for(x):
    for v in x['variants']:
        r = PICKUP.get(str(v['id']))
        if v['available'] and r and r.get('available'):
            return r
    return None
for x in products:
    x['pickup'] = pickup_for(x)
PICKUP_ON = sum(1 for x in products if x['pickup']) >= 0.5 * max(1, len(products))
_ready = [x['pickup']['ready'] for x in products if x['pickup']]
READY = max(set(_ready), key=_ready.count) if _ready else ''
MIN_PRICE = min(x['price'] for x in products)
ABOUT_N = int(round(len(products), -2))
handles = {x['handle'] for x in products}
# group near-identical listings (same title) so the grid shows one card per item with a "from" price
parent = {}
def find(a):
    while parent.setdefault(a, a) != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
def union(a, b): parent[find(a)] = find(b)
for x in products:
    tk = ('t', x['cat'], re.sub(r'\s+', ' ', x['title'].lower()).strip())
    ik = ('i', x['cat'], x['images'][0].split('?')[0].rsplit('/', 1)[-1])
    union(('h', x['handle']), tk); union(('h', x['handle']), ik)
groups = {}
for x in products:
    groups.setdefault(find(('h', x['handle'])), []).append(x)
for key, g in groups.items():
    g.sort(key=lambda y: y['price'])
    same_title = len({y['title'] for y in g}) == 1
    for y in g:
        y['group'] = g
        y['label'] = (y['variants'][0]['sku'] or y['title']) if same_title else y['title']
leaders = []
seen = set()
for x in products:
    g = x['group']
    if id(g) in seen: continue
    seen.add(id(g)); leaders.append(g[0])

# ---------- visit helpers ----------
def hours_html(cls='hours'):
    return f'<dl class="{cls}">' + ''.join(f'<div><dt>{d}</dt><dd>{h}</dd></div>' for d, h in HOURS) + '</dl>'

def visit_buttons(light=False):
    g = ' ghost' if light else ' alt'
    return (f'<div class="cta"><a class="btn" href="{DIRECTIONS}" rel="noopener" target="_blank">Get directions</a>'
            f'<a class="btn{g}" href="tel:{TEL}">Call {PHONE}</a></div>')

def visit_block(full=False):
    pickup = (f'<p><b>Reserve online, pick up in store.</b> Choose Pickup at checkout; orders are {READY.lower()}.</p>' if PICKUP_ON else
              f'<p><b>Looking for a specific piece?</b> Call {PHONE} before you come in.</p>')
    return f'''<div class="visit">
<div class="vinfo"><p class="eyebrow dark">Visit the crystal floor</p><h2>{STORE_STREET}</h2>
<p class="addr">{STORE_ADDR}<br>On 14th Street just west of Fifth Avenue, about a 4-minute walk from Union Square.</p>
<h3>Hours</h3>{hours_html()}
<p class="small">Holiday hours may differ. Call {PHONE} to check before a special trip.</p>
{pickup}{visit_buttons()}
{'' if full else '<p><a href="/visit/">Directions, subway lines and pickup details &rarr;</a></p>'}</div>
<div class="vmap"><iframe title="Map to {STORE_ADDR}" src="{MAP_EMBED}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
</div>'''

def store_ld():
    return {"@context": "https://schema.org", "@type": "Store", "name": BRAND, "url": SITE + '/',
            "image": products[0]['images'][0] if products else None,
            "description": f"Crystal floor at {STORE_ADDR}, near Union Square. {BRAND} is a brand of Wealth Edge Ventures Inc.",
            "telephone": TEL,
            "address": {"@type": "PostalAddress", "streetAddress": STORE_STREET, "addressLocality": STORE_CITY,
                        "addressRegion": STORE_REGION, "postalCode": STORE_ZIP, "addressCountry": "US"},
            "geo": {"@type": "GeoCoordinates", "latitude": GEO[0], "longitude": GEO[1]},
            "hasMap": MAP_LINK,
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": d, "opens": o, "closes": c} for d, o, c in HOURS_LD],
            "parentOrganization": {"@type": "Organization", "name": "Wealth Edge Ventures Inc."}}

def ldjson(obj):
    return f'<script type="application/ld+json">{json.dumps(obj)}</script>'

# ---------- layout ----------
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">'

def nav():
    links = ''.join(f'<a href="/shop/{CAT_SLUG[k]}/"><i style="background:{CAT_COLOR[k]}"></i>{E(CAT_SHORT[k])}</a>' for k in CATS)
    return f'''<header class="top">
<div class="bar"><a href="/visit/">Visit us: {STORE_STREET}, near Union Square</a><span>Open daily from 11 AM</span>{'<span>Reserve online, pick up in store</span>' if PICKUP_ON else ''}</div>
<div class="nav wrap">
<a class="logo" href="/" aria-label="{BRAND} home"><svg viewBox="0 0 40 40" width="34" height="34" aria-hidden="true"><path d="M20 2 33 14 20 38 7 14Z" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M7 14h26M20 2l-6 12 6 24 6-24z" fill="none" stroke="currentColor" stroke-width="1.6"/></svg><span><b>Manhattan</b> Crystal Market</span></a>
<button class="menu" aria-label="Menu" aria-expanded="false" onclick="document.body.classList.toggle('open');this.setAttribute('aria-expanded',document.body.classList.contains('open'))"><span></span><span></span></button>
<nav class="links"><a href="/visit/" class="vlink">Visit</a><a href="/shop/">Shop all</a>{links}<a href="/about/">About</a></nav>
</div></header>'''

def footer():
    return f'''<footer class="foot"><div class="wrap grid4">
<div><a class="logo light" href="/"><span><b>Manhattan</b> Crystal Market</span></a><p class="legal">{LEGAL}</p>
<p class="small">Orders are checked out on Shopify through namastebookshop.com, which processes payment and ships each order from New York City.</p></div>
<div><h4>Shop</h4>{''.join(f'<a href="/shop/{CAT_SLUG[k]}/">{E(CATS[k][0])}</a>' for k in CATS)}</div>
<div><h4>Help</h4><a href="/shipping/">Shipping</a><a href="/returns/">Returns</a><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a><a href="{SHOP}/policies/contact-information" rel="noopener">Contact</a></div>
<div><h4>Visit</h4><p class="small foottxt">{STORE_ADDR}</p>{''.join(f'<p class="small foottxt">{d}: {h}</p>' for d, h in HOURS)}<a href="tel:{TEL}">Call {PHONE}</a><a href="{DIRECTIONS}" rel="noopener" target="_blank">Get directions</a><a href="/visit/">Visit &amp; pickup info</a><a href="/crystal-shop-near-union-square/">Crystal shopping near Union Square</a></div>
<div><h4>Company</h4><a href="/about/">About us</a><p class="small">&copy; {datetime.date.today().year} Wealth Edge Ventures Inc.</p></div>
</div><div class="wrap legalline">{LEGAL}</div></footer>'''

def page(path, title, desc, body, extra_head='', canonical=True):
    url = SITE + path
    robots = '<meta name="robots" content="noindex,nofollow">' if PREVIEW else ''
    can = f'<link rel="canonical" href="{url}">' if canonical else ''
    doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">{robots}{can}
<meta property="og:site_name" content="{BRAND}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}">
<meta name="theme-color" content="#101418"><link rel="icon" href="/favicon.svg" type="image/svg+xml">{FONTS}<link rel="stylesheet" href="/assets/site.css"><script>window.MCM_BASE={json.dumps(BASE)}</script>{extra_head}</head>
<body>{nav()}<main>{body}</main>{footer()}<div class="actionbar"><a href="tel:{TEL}">Call</a><a href="{DIRECTIONS}" rel="noopener" target="_blank">Directions</a><a href="/visit/">Hours</a></div><script src="/assets/site.js" defer></script></body></html>'''
    if BASE:
        doc = re.sub(r'(href|src)="/(?!/)', lambda m: f'{m.group(1)}="{BASE}/', doc)
    out = os.path.join(DIST, path.strip('/'), 'index.html') if path.endswith('/') else os.path.join(DIST, path.strip('/'))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write(doc)

def card(x):
    n = len(x.get('group', [x]))
    cmp_ = f'<s>{money(x["compare"])}</s> ' if x['compare'] and n == 1 else ''
    if n > 1: cmp_ = f'<small>{n} options from</small> '
    return (f'<a class="card" href="/products/{x["handle"]}/"><div class="ph"><img loading="lazy" src="{img(x["images"][0],400)}" alt="{E(x["title"])}" width="400" height="400"></div>'
            f'<div class="meta"><span class="tag" style="--c:{CAT_COLOR[x["cat"]]}">{E(x["stone"] if x["stone"]!="Other" else CATS[x["cat"]][0])}</span>'
            f'<h3>{E(x["title"])}</h3><p class="price">{cmp_}{money(x["price"])}</p></div></a>')

# ---------- build ----------
if os.path.exists(DIST): shutil.rmtree(DIST)
os.makedirs(DIST)
shutil.copytree(os.path.join(ROOT, 'src', 'assets'), os.path.join(DIST, 'assets'))
for f in os.listdir(os.path.join(ROOT, 'src', 'static')):
    shutil.copy(os.path.join(ROOT, 'src', 'static', f), DIST)

# compact catalog for the shop grid
os.makedirs(os.path.join(DIST, 'data'), exist_ok=True)
compact = [{'h': x['handle'], 't': x['title'], 'c': x['cat'], 's': x['stone'], 'p': x['price'],
            'k': x['compare'] if len(x['group']) == 1 else None, 'n': len(x['group']), 'i': img(x['images'][0], 400),
            'd': max(y['created'] for y in x['group'])[:10]} for x in leaders]
json.dump(compact, open(os.path.join(DIST, 'data', 'catalog.json'), 'w'), separators=(',', ':'))
meta = {'cats': {k: {'name': CATS[k][0], 'slug': CAT_SLUG[k], 'color': CAT_COLOR[k]} for k in CATS},
        'built': datetime.datetime.now().isoformat(timespec='minutes')}
json.dump(meta, open(os.path.join(DIST, 'data', 'meta.json'), 'w'))

from collections import Counter
cat_count = Counter(x['cat'] for x in products)
stone_count = Counter(x['stone'] for x in products)

# Home
def pick_featured():
    out = []
    for k in CATS:
        pool = sorted([x for x in leaders if x['cat'] == k], key=lambda x: -x['price'])
        pool = pool[len(pool)//6: len(pool)//6 + 2]
        out += pool
    return out
tiles = ''.join(f'''<a class="tile" href="/shop/{CAT_SLUG[k]}/" style="--c:{CAT_COLOR[k]}"><img loading="lazy" src="{img(next(x for x in products if x['cat']==k)['images'][0],500)}" alt=""><div><span class="line">{i+1}</span><h3>{E(CATS[k][0])}</h3><p>{cat_count[k]} pieces</p></div></a>''' for i, k in enumerate(CATS))
stones_top = ''.join(f'<a class="chip" href="/shop/?stone={E(s)}">{E(s)} <small>{n}</small></a>' for s, n in stone_count.most_common(16) if s != 'Other')
home = f'''
<section class="hero"><div class="wrap hero-in">
<p class="eyebrow">{STORE_STREET} &middot; Union Square &middot; New York City</p>
<h1>Visit our crystal floor at 2 West 14th Street, <em>steps from Union Square.</em></h1>
<p class="lede">About {ABOUT_N:,} crystals, minerals and stone jewelry pieces, priced from {money(MIN_PRICE)}. Open daily from 11 AM.{f" Reserve online and pick up in store; orders are {READY.lower()}." if PICKUP_ON else ""}</p>
<div class="cta"><a class="btn" href="{DIRECTIONS}" rel="noopener" target="_blank">Get directions</a><a class="btn ghost" href="tel:{TEL}">Call {PHONE}</a><a class="btn ghost" href="/shop/">Shop online</a></div>
</div></section>
<section class="wrap">{visit_block()}</section>
<section class="wrap"><div class="sechead"><h2>Why stop by</h2></div><ul class="whys">
<li><b>About {ABOUT_N:,} pieces</b><span>Towers, clusters, specimens, pocket stones, carvings and stone jewelry, all listed online so you can browse before you come in.</span></li>
<li><b>Prices from {money(MIN_PRICE)}</b><span>Every listing shows its price, so you know what to expect at the counter.</span></li>
{f'<li><b>Reserve, then pick up</b><span>Buy online, choose Pickup at checkout, and collect it at {STORE_STREET}. Orders are {READY.lower()}.</span></li>' if PICKUP_ON else ''}
<li><b>Readings with Namaste</b><span>Pair your visit with a tarot or intuitive reading. <a href="{READINGS}" rel="noopener">See readers and book</a>.</span></li>
<li><b>Easy to reach</b><span>About 0.2 miles from both the 14 St&ndash;Union Square and 14 St/6 Av subway stations.</span></li>
</ul></section>
<section class="wrap"><div class="sechead"><h2>Pick your aisle</h2><a href="/shop/">See everything &rarr;</a></div><div class="tiles">{tiles}</div></section>
<section class="wrap"><div class="sechead"><h2>Browse by stone</h2></div><div class="chips">{stones_top}</div></section>
<section class="wrap"><div class="sechead"><h2>Worth a closer look</h2><a href="/shop/">Shop all &rarr;</a></div><div class="grid">{''.join(card(x) for x in pick_featured())}</div></section>
<section class="band"><div class="wrap band-in"><div><h2>{"Reserve online, pick up in store" if PICKUP_ON else "See it in person"}</h2><p>Every listing has its own photos, price and live stock. {"Reserve a piece online and collect it on 14th Street, or have it shipped from New York City." if PICKUP_ON else "Call ahead to check a piece is on the floor, or order online and have it shipped from New York City."}</p>{visit_buttons(True)}</div>
<ol class="steps"><li><b>Find it</b><span>Filter by aisle, stone or price.</span></li>{"<li><b>Choose Pickup at checkout</b><span>Pay securely on Shopify. Orders are " + READY.lower() + ".</span></li><li><b>Collect it</b><span>" + STORE_ADDR + ".</span></li>" if PICKUP_ON else "<li><b>Call ahead</b><span>" + PHONE + "</span></li><li><b>Visit</b><span>" + STORE_ADDR + ".</span></li>"}</ol></div></section>'''
org_ld = {"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "url": SITE,
          "parentOrganization": {"@type": "Organization", "name": "Wealth Edge Ventures Inc."}}
page('/', f'{BRAND} | Crystal Shop at 2 W 14th St near Union Square, NYC',
     f'Visit our crystal floor at {STORE_ADDR}, near Union Square, Flatiron, Chelsea and Greenwich Village. About {ABOUT_N:,} crystals from {money(MIN_PRICE)}, with in-store pickup.',
     home, ldjson(org_ld) + ldjson(store_ld()))

# Shop + category pages (client-side grid with static fallback list for crawlers)
def shop_page(path, title, desc, h1, sub, preset):
    chips = '<button class="f on" data-cat="">All</button>' + ''.join(
        f'<button class="f" data-cat="{k}" style="--c:{CAT_COLOR[k]}">{E(CATS[k][0])} <small>{cat_count[k]}</small></button>' for k in CATS)
    stones = '<option value="">All stones</option>' + ''.join(f'<option>{E(s)}</option>' for s, n in sorted(stone_count.items()) if s != 'Other') + '<option value="Other">Other</option>'
    pool = [x for x in leaders if not preset or x['cat'] == preset][:48]
    body = f'''<section class="wrap shophead"><h1>{E(h1)}</h1><p>{E(sub)}</p></section>
<section class="wrap shop" data-preset="{preset}">
<div class="filters"><div class="fcats">{chips}</div>
<div class="frow"><input type="search" id="q" placeholder="Search stones, shapes, origins" aria-label="Search">
<select id="stone" aria-label="Stone">{stones}</select>
<select id="price" aria-label="Price"><option value="">Any price</option><option value="0-25">Under $25</option><option value="25-75">$25 to $75</option><option value="75-200">$75 to $200</option><option value="200-99999">$200 and up</option></select>
<select id="sort" aria-label="Sort"><option value="new">Newest</option><option value="lo">Price: low to high</option><option value="hi">Price: high to low</option><option value="az">A to Z</option></select></div>
<p class="count" id="count"></p></div>
<div class="grid" id="grid">{''.join(card(x) for x in pool)}</div>
<div class="more"><button class="btn" id="more" hidden>Show more</button></div>
</section>'''
    page(path, title, desc, body)

shop_page('/shop/', f'Shop Crystals Online, Pick Up Near Union Square | {BRAND}', f'Browse {len(products):,} crystals, minerals and stone jewelry pieces from {money(MIN_PRICE)}. Reserve online and pick up at {STORE_STREET}, NYC, or have it shipped.',
          'Shop the market', f'{len(products):,} pieces in stock across six aisles. Reserve online and pick up at {STORE_STREET}, or have it shipped.', '')
for k in CATS:
    shop_page(f'/shop/{CAT_SLUG[k]}/', f'{CATS[k][0]} in NYC near Union Square | {BRAND}', f'{CAT_BLURB[k]} {cat_count[k]} pieces at {BRAND}, {STORE_STREET}, NYC. Reserve online and pick up in store or have it shipped.',
              CATS[k][0], CAT_BLURB[k], k)

# Product pages
for x in products:
    stone, origin, cat = x['stone'], x['origin'], x['cat']
    avail = [v for v in x['variants'] if v['available']]
    v0 = avail[0]
    gallery = ''.join(f'<button class="th{" on" if i==0 else ""}" data-src="{img(u,1000)}"><img loading="lazy" src="{img(u,160)}" alt="" width="80" height="80"></button>' for i, u in enumerate(x['images']))
    opts = ''
    if len(x['variants']) > 1:
        opts = '<label class="vlab">Option<select id="variant">' + ''.join(
            f'<option value="{v["id"]}" data-price="{v["price"]}"{" disabled" if not v["available"] else ""}{" selected" if v is v0 else ""}>{E(v["title"])}{"" if v["available"] else " (sold out)"}</option>' for v in x['variants']) + '</select></label>'
    facts = [('Aisle', f'<a href="/shop/{CAT_SLUG[cat]}/">{E(CATS[cat][0])}</a>')]
    if stone != 'Other': facts.append(('Stone', f'<a href="/shop/?stone={E(stone)}">{E(stone)}</a>'))
    if origin: facts.append(('Origin', E(origin)))
    if v0['sku']: facts.append(('SKU', E(v0['sku'])))
    facts.append(('Ships from', 'New York City'))
    if x['pickup']: facts.append(('Pickup', f'<a href="/visit/">{STORE_STREET}</a>'))
    factl = ''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in facts)
    related = [y for y in leaders if y['cat'] == cat and y['stone'] == stone and y['group'] is not x['group']][:4]
    if len(related) < 4:
        related += [y for y in leaders if y['cat'] == cat and y['group'] is not x['group'] and y not in related][:4-len(related)]
    sibs = ''
    if len(x['group']) > 1:
        sibs = '<div class="sibs"><h3>Choose your piece</h3><p class="small">Each listing is a separate stone, priced by size and quality.</p>' + ''.join(
            f'<a class="sib{" on" if y is x else ""}" href="/products/{y["handle"]}/"><img loading="lazy" src="{img(y["images"][0],120)}" alt="" width="60" height="60"><span>{E(y["label"])}</span><b>{money(y["price"])}</b></a>' for i, y in enumerate(x['group'])) + '</div>'
    ld = {"@context": "https://schema.org", "@type": "Product", "name": x['title'], "image": x['images'][:3],
          "sku": v0['sku'] or str(v0['id']), "brand": {"@type": "Brand", "name": BRAND},
          "category": CATS[cat][0], "url": f"{SITE}/products/{x['handle']}/",
          "description": ' '.join(describe(x, cat, stone, origin)),
          "offers": {"@type": "Offer", "price": f"{float(v0['price']):.2f}", "priceCurrency": "USD",
                     "availability": "https://schema.org/InStock", "itemCondition": "https://schema.org/NewCondition",
                     "url": f"{SITE}/products/{x['handle']}/",
                     "seller": {"@type": "Organization", "name": "Wealth Edge Ventures Inc."}}}
    cmp_ = f'<s id="cmp">{money(x["compare"])}</s>' if x['compare'] else '<s id="cmp" hidden></s>'
    if x['pickup']:
        pickup_html = (f'<div class="pickup"><h3>Reserve online, pick up in store</h3>'
                       f'<p>Pickup available at <b>{STORE_ADDR}</b>, near Union Square. {E(x["pickup"]["ready"])}.</p>'
                       f'<p class="small">Tap Buy now, then choose <b>Pickup</b> at checkout. Questions about this piece? Call <a href="tel:{TEL}">{PHONE}</a>.</p>'
                       f'<div class="pbtns"><a href="{DIRECTIONS}" rel="noopener" target="_blank">Directions</a><a href="tel:{TEL}">Call</a><a href="/visit/">Hours</a></div></div>')
    else:
        pickup_html = (f'<div class="pickup"><h3>See it in person</h3>'
                       f'<p>Visit our crystal floor at <b>{STORE_ADDR}</b>, near Union Square. Call <a href="tel:{TEL}">{PHONE}</a> before you come to check this piece is on the floor.</p>'
                       f'<div class="pbtns"><a href="{DIRECTIONS}" rel="noopener" target="_blank">Directions</a><a href="tel:{TEL}">Call</a><a href="/visit/">Hours</a></div></div>')
    body = f'''<nav class="wrap crumbs"><a href="/shop/">Shop</a> / <a href="/shop/{CAT_SLUG[cat]}/">{E(CATS[cat][0])}</a></nav>
<section class="wrap pdp" data-handle="{x['handle']}">
<div class="gallery"><div class="main"><img id="mainimg" src="{img(x['images'][0],1000)}" alt="{E(x['title'])}" width="1000" height="1000"></div><div class="thumbs">{gallery if len(x['images'])>1 else ''}</div></div>
<div class="info"><span class="tag" style="--c:{CAT_COLOR[cat]}">{E(CATS[cat][0])}</span><h1>{E(x['title'])}</h1>
<p class="pprice">{cmp_} <span id="price">{money(v0['price'])}</span></p>
<p class="stock" id="stock"><i></i><span>In stock</span></p>
{opts}{sibs}
<a class="btn buy" id="buy" href="{SHOP}/cart/{v0['id']}:1{CART_ATTR}" rel="nofollow">Buy now</a>
<p class="note">Checkout opens on Shopify (namastebookshop.com), where you can choose shipping{" or in-store pickup" if x['pickup'] else ""} and review your order before paying.</p>
{pickup_html}
<div class="desc">{''.join(f'<p>{s}</p>' for s in describe(x, cat, stone, origin))}</div>
<dl class="facts">{factl}</dl>
<p class="small"><a href="/shipping/">Shipping</a> &middot; <a href="/returns/">Returns</a></p></div></section>
<section class="wrap"><div class="sechead"><h2>More like this</h2></div><div class="grid">{''.join(card(y) for y in related)}</div></section>'''
    page(f"/products/{x['handle']}/", f"{x['title']} | {BRAND} NYC",
         f"{x['title']} for {money(v0['price'])}. " + (f"Reserve online and pick up at {STORE_STREET} near Union Square, or ship from NYC." if x['pickup'] else f"See it at {STORE_STREET} near Union Square or ship from NYC."),
         body, f'<script type="application/ld+json">{json.dumps(ld)}</script><script>window.MCM_PRODUCT={json.dumps({"handle":x["handle"],"cartAttr":CART_ATTR,"shop":SHOP})}</script>')

# Info pages
def info(path, title, desc, h1, html_body, extra_head=''):
    page(path, f'{title} | {BRAND}', desc, f'<section class="wrap prose"><h1>{h1}</h1>{html_body}<p class="legal">{LEGAL}</p></section>', extra_head)

info('/about/', 'About', f'About {BRAND}, the crystal floor at {STORE_ADDR}, a brand of Wealth Edge Ventures Inc.', 'About Manhattan Crystal Market', f'''
<p class="lead">{BRAND} is the crystal floor inside the store at {STORE_ADDR}, on 14th Street just west of Fifth Avenue and a few minutes' walk from Union Square.</p>
<p>Come in to see towers, clusters, raw specimens, pocket stones, carvings and stone jewelry up close, or browse the full selection of about {ABOUT_N:,} pieces online first. Every piece online has its own photos and price, and stock updates from the same inventory the floor uses.{" Reserve a piece online and choose Pickup at checkout to collect it in store." if PICKUP_ON else ""}</p>
<h2>Visit</h2><p>{STORE_ADDR}. Call <a href="tel:{TEL}">{PHONE}</a>.</p>{hours_html()}{visit_buttons()}<p><a href="/visit/">Directions, subway lines and pickup details &rarr;</a></p>
<h2>Who we are</h2><p>{LEGAL} Online orders are checked out on Shopify through namastebookshop.com, which processes payment and fulfills orders, including in-store pickups. Products ship from New York City.</p>
<h2>What we carry</h2><ul>{''.join(f'<li><a href="/shop/{CAT_SLUG[k]}/">{E(CATS[k][0])}</a>: {E(CAT_BLURB[k])}</li>' for k in CATS)}</ul>
<h2>Readings</h2><p>Tarot and intuitive readings are available through Namaste. <a href="{READINGS}" rel="noopener">See the readers and book a reading</a>.</p>
<h2>A note on natural stones</h2><p>Crystals and minerals are natural materials. Color, pattern, inclusions and size vary from piece to piece, and photos can look slightly different on different screens. Crystal folklore and traditions are shared for interest only and are not medical advice.</p>
<h2>Get in touch</h2><p>Call <a href="tel:{TEL}">{PHONE}</a>, or see the <a href="{SHOP}/policies/contact-information">store contact page</a> for order questions.</p>''', extra_head=ldjson(store_ld()))

# Visit page
TRANSIT = '''<ul class="transit">
<li><b>14 St&ndash;Union Square</b> <span class="lines">4 5 6 L N Q R W</span><br>About 0.2 miles east, roughly a 4-minute walk west along 14th Street.</li>
<li><b>14 St/6 Av</b> <span class="lines">F M L</span>, connected to <b>14 St</b> <span class="lines">1 2 3</span><br>About 0.2 miles west at Sixth Avenue, roughly a 4-minute walk east along 14th Street.</li>
<li><b>PATH</b> 14th Street station at Sixth Avenue.</li>
<li><b>Bus</b> M14A and M14D Select Bus Service run along 14th Street.</li></ul>
<p class="small">Some lines run only at certain times (for example, the W runs weekdays and the M weekdays during the day). Check the MTA before you travel.</p>'''
info('/visit/', 'Visit Our Crystal Floor near Union Square', f'Directions, hours, subway lines and in-store pickup for {BRAND} at {STORE_ADDR}, near Union Square, Flatiron, Chelsea and Greenwich Village.',
     'Visit us at 2 West 14th Street', f'''
<p class="lead">Our crystal floor is at {STORE_ADDR}, on 14th Street just west of Fifth Avenue. It sits where Greenwich Village, Chelsea, the Flatiron District and Union Square meet.</p>
{visit_block(full=True)}
<h2>Getting here</h2>{TRANSIT}
<h2>{"Reserve online, pick up in store" if PICKUP_ON else "Looking for a specific piece?"}</h2>
{f"<ol><li>Find your piece in the <a href='/shop/'>online shop</a>.</li><li>Tap Buy now and choose <b>Pickup</b> at checkout.</li><li>Orders are {READY.lower()}. Come to {STORE_ADDR} during open hours.</li></ol><p>Questions about a pickup? Call <a href='tel:{TEL}'>{PHONE}</a>.</p>" if PICKUP_ON else f"<p>Call <a href='tel:{TEL}'>{PHONE}</a> before you come in and we'll check it's on the floor.</p>"}
<h2>Make it a longer visit</h2><p>Book a tarot or intuitive reading through Namaste: <a href="{READINGS}" rel="noopener">see readers and book</a>.</p>''', extra_head=ldjson(store_ld()))

# Neighborhood guide
info('/crystal-shop-near-union-square/', 'Crystal Shop Near Union Square, Flatiron, Chelsea & the Village',
     f'Looking for a crystal shop near Union Square? {BRAND} is at {STORE_ADDR}, between Greenwich Village, Chelsea and the Flatiron District, with about {ABOUT_N:,} pieces and in-store pickup.',
     'Crystal shopping near Union Square', f'''
<p class="lead">If you are searching for a crystal shop near you in Manhattan, {STORE_STREET} is easy to reach from most of downtown and midtown. Here is what to expect and how to get here.</p>
<h2>Where we are</h2><p>{STORE_ADDR}, on 14th Street just west of Fifth Avenue. 14th Street is the dividing line between Greenwich Village to the south and Chelsea and the Flatiron District to the north, and Union Square is about 0.2 miles to the east.</p>
<h2>Coming from nearby neighborhoods</h2><ul>
<li><b>Union Square and Gramercy:</b> walk west on 14th Street past Union Square West and University Place to Fifth Avenue.</li>
<li><b>Flatiron and NoMad:</b> walk south on Fifth Avenue to 14th Street.</li>
<li><b>Chelsea:</b> take the 1, 2, 3, F, M or L to 14th Street at Seventh or Sixth Avenue and walk east on 14th Street.</li>
<li><b>Greenwich Village and the West Village:</b> walk north on Fifth Avenue, or take the 1, 2 or 3 to 14 St.</li>
<li><b>East Village:</b> take the L west to 14 St&ndash;Union Square, or walk west on 14th Street.</li></ul>
<h2>What you will find</h2><ul>
<li>About {ABOUT_N:,} pieces listed online across six aisles, priced from {money(MIN_PRICE)}.</li>
<li>Towers, clusters, geodes, mineral specimens, tumbled and palm stones, spheres and carvings, and stone jewelry.</li>
{f"<li>Reserve online and pick up in store; orders are {READY.lower()}.</li>" if PICKUP_ON else ""}
<li>Open daily from 11 AM. See <a href="/visit/">full hours</a>.</li>
<li>Tarot and intuitive readings available through Namaste. <a href="{READINGS}" rel="noopener">Book a reading</a>.</li></ul>
<h2>Tips for your visit</h2><ul><li>Browse the <a href="/shop/">online shop</a> first and note the pieces you want to see.</li>
<li>Natural stones vary, so seeing a piece in person is the best way to choose.</li>
<li>Going out of your way for one item? Call <a href="tel:{TEL}">{PHONE}</a> first.</li></ul>
{visit_block()}''', extra_head=ldjson(store_ld()))

def policy(path, title, slug, intro):
    info(path, title, f'{title} for {BRAND} orders.', title, f'''<p class="lead">{intro}</p>
<p>Because checkout and fulfillment run through our Shopify store, the full and current {title.lower()} is published there:</p>
<p><a class="btn" href="{SHOP}/policies/{slug}">Read the full {title.lower()}</a></p>''')
policy('/shipping/', 'Shipping Policy', 'shipping-policy', f'Orders ship from New York City. Shipping options and costs are shown at checkout before you pay.{" You can also choose Pickup at checkout and collect your order at " + STORE_ADDR + "." if PICKUP_ON else ""}')
policy('/returns/', 'Refund Policy', 'refund-policy', 'If something is not right with your order, the refund policy below explains eligibility, timing and how to start a return.')
policy('/privacy/', 'Privacy Policy', 'privacy-policy', 'This site does not use accounts or collect payment details; checkout and payment are handled by Shopify. The privacy policy below covers the data collected at checkout.')
policy('/terms/', 'Terms of Service', 'terms-of-service', 'Purchases made through this site are completed on Shopify and governed by the terms below.')

# 404
page('/404.html', f'Page not found | {BRAND}', 'Page not found', '<script>(function(){var p=location.pathname,b="/manhattancrystalmarket";if(p.indexOf(b+"/")===0||p===b){location.replace((p.slice(b.length)||"/")+location.search+location.hash);}})();</script><section class="wrap prose"><h1>That aisle is empty</h1><p>The page you were looking for may have sold out or moved.</p><p><a class="btn" href="/shop/">Back to the market</a></p></section>', canonical=False)

# sitemap + robots
urls = ['/', '/visit/', '/crystal-shop-near-union-square/', '/shop/', '/about/', '/shipping/', '/returns/', '/privacy/', '/terms/'] + [f'/shop/{CAT_SLUG[k]}/' for k in CATS] + [f"/products/{x['handle']}/" for x in products]
open(os.path.join(DIST, '.nojekyll'), 'w').write('')
if not BASE and SITE.startswith('https://') and 'github.io' not in SITE:
    open(os.path.join(DIST, 'CNAME'), 'w').write(SITE.split('://', 1)[1] + '\n')
open(os.path.join(DIST, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{SITE}{u}</loc></url>' for u in urls) + '</urlset>')
open(os.path.join(DIST, 'robots.txt'), 'w').write('User-agent: *\nDisallow: /\n' if PREVIEW else f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')

# manifest for reporting
json.dump({'count': len(products), 'categories': {CATS[k][0]: cat_count[k] for k in CATS},
           'products': [{'title': x['title'], 'handle': x['handle'], 'gid': f"gid://shopify/Product/{x['id']}", 'category': CATS[x['cat']][0],
                         'stone': x['stone'], 'price': x['price'], 'variants': x['variants'], 'images': x['images']} for x in products]},
          open(os.path.join(ROOT, 'data', 'mcm_products.json'), 'w'), indent=1)
print(f"built {len(products)} products, preview={PREVIEW}, base={BASE!r}, site={SITE}", dict(cat_count))
