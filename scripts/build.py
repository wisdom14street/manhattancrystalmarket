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
    s.append("Ships from New York City. Secure checkout is completed on Shopify.")
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

# ---------- layout ----------
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">'

def nav():
    links = ''.join(f'<a href="/shop/{CAT_SLUG[k]}/"><i style="background:{CAT_COLOR[k]}"></i>{E(CAT_SHORT[k])}</a>' for k in CATS)
    return f'''<header class="top">
<div class="bar"><span>Shipping from New York City</span><span>Secure Shopify checkout</span></div>
<div class="nav wrap">
<a class="logo" href="/" aria-label="{BRAND} home"><svg viewBox="0 0 40 40" width="34" height="34" aria-hidden="true"><path d="M20 2 33 14 20 38 7 14Z" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M7 14h26M20 2l-6 12 6 24 6-24z" fill="none" stroke="currentColor" stroke-width="1.6"/></svg><span><b>Manhattan</b> Crystal Market</span></a>
<button class="menu" aria-label="Menu" aria-expanded="false" onclick="document.body.classList.toggle('open');this.setAttribute('aria-expanded',document.body.classList.contains('open'))"><span></span><span></span></button>
<nav class="links"><a href="/shop/">Shop all</a>{links}<a href="/about/">About</a></nav>
</div></header>'''

def footer():
    return f'''<footer class="foot"><div class="wrap grid4">
<div><a class="logo light" href="/"><span><b>Manhattan</b> Crystal Market</span></a><p class="legal">{LEGAL}</p>
<p class="small">Orders are checked out on Shopify through namastebookshop.com, which processes payment and ships each order from New York City.</p></div>
<div><h4>Shop</h4>{''.join(f'<a href="/shop/{CAT_SLUG[k]}/">{E(CATS[k][0])}</a>' for k in CATS)}</div>
<div><h4>Help</h4><a href="/shipping/">Shipping</a><a href="/returns/">Returns</a><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a><a href="{SHOP}/policies/contact-information" rel="noopener">Contact</a></div>
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
<body>{nav()}<main>{body}</main>{footer()}<script src="/assets/site.js" defer></script></body></html>'''
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
<p class="eyebrow">New York City &middot; Crystals &middot; Minerals &middot; Stone jewelry</p>
<h1>A city-sized crystal market, <em>open around the clock.</em></h1>
<p class="lede">Browse {len(products):,} towers, clusters, specimens, tumbled stones, carvings and stone jewelry, each with its own photos and price, shipped from NYC.</p>
<div class="cta"><a class="btn" href="/shop/">Shop the market</a><a class="btn ghost" href="/shop/?sort=new">New arrivals</a></div>
</div></section>
<section class="wrap"><div class="sechead"><h2>Pick your aisle</h2><a href="/shop/">See everything &rarr;</a></div><div class="tiles">{tiles}</div></section>
<section class="wrap"><div class="sechead"><h2>Browse by stone</h2></div><div class="chips">{stones_top}</div></section>
<section class="wrap"><div class="sechead"><h2>Worth a closer look</h2><a href="/shop/">Shop all &rarr;</a></div><div class="grid">{''.join(card(x) for x in pick_featured())}</div></section>
<section class="band"><div class="wrap band-in"><div><h2>How the market works</h2><p>Every listing has its own photos, price and live stock count from our inventory. Add it to your bag and you are taken to a secure Shopify checkout. Orders ship from New York City.</p></div>
<ol class="steps"><li><b>Find it</b><span>Filter by aisle, stone or price.</span></li><li><b>Check out</b><span>Pay through Shopify, with Shop Pay and major cards.</span></li><li><b>Unbox it</b><span>Packed and shipped from NYC.</span></li></ol></div></section>'''
org_ld = {"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "url": SITE,
          "parentOrganization": {"@type": "Organization", "name": "Wealth Edge Ventures Inc."}}
page('/', f'{BRAND} | Crystals, Minerals & Stone Jewelry from NYC',
     f'Shop {len(products):,} crystals, mineral specimens, towers, clusters and stone jewelry from {BRAND}, shipped from New York City.',
     home, f'<script type="application/ld+json">{json.dumps(org_ld)}</script>')

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

shop_page('/shop/', f'Shop All Crystals & Stone Jewelry | {BRAND}', f'Browse every crystal, mineral and stone jewelry piece at {BRAND}. Filter by category, stone and price.',
          'Shop the market', f'{len(products):,} pieces in stock across six aisles.', '')
for k in CATS:
    shop_page(f'/shop/{CAT_SLUG[k]}/', f'{CATS[k][0]} | {BRAND}', f'{CAT_BLURB[k]} Shop {cat_count[k]} pieces at {BRAND}, shipped from NYC.',
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
    body = f'''<nav class="wrap crumbs"><a href="/shop/">Shop</a> / <a href="/shop/{CAT_SLUG[cat]}/">{E(CATS[cat][0])}</a></nav>
<section class="wrap pdp" data-handle="{x['handle']}">
<div class="gallery"><div class="main"><img id="mainimg" src="{img(x['images'][0],1000)}" alt="{E(x['title'])}" width="1000" height="1000"></div><div class="thumbs">{gallery if len(x['images'])>1 else ''}</div></div>
<div class="info"><span class="tag" style="--c:{CAT_COLOR[cat]}">{E(CATS[cat][0])}</span><h1>{E(x['title'])}</h1>
<p class="pprice">{cmp_} <span id="price">{money(v0['price'])}</span></p>
<p class="stock" id="stock"><i></i><span>In stock</span></p>
{opts}{sibs}
<a class="btn buy" id="buy" href="{SHOP}/cart/{v0['id']}:1{CART_ATTR}" rel="nofollow">Buy now</a>
<p class="note">Checkout opens on Shopify (namastebookshop.com), where you can review your order before paying.</p>
<div class="desc">{''.join(f'<p>{s}</p>' for s in describe(x, cat, stone, origin))}</div>
<dl class="facts">{factl}</dl>
<p class="small"><a href="/shipping/">Shipping</a> &middot; <a href="/returns/">Returns</a></p></div></section>
<section class="wrap"><div class="sechead"><h2>More like this</h2></div><div class="grid">{''.join(card(y) for y in related)}</div></section>'''
    page(f"/products/{x['handle']}/", f"{x['title']} | {BRAND}",
         f"{x['title']} for {money(v0['price'])}. {CAT_BLURB[cat]} Ships from NYC.",
         body, f'<script type="application/ld+json">{json.dumps(ld)}</script><script>window.MCM_PRODUCT={json.dumps({"handle":x["handle"],"cartAttr":CART_ATTR,"shop":SHOP})}</script>')

# Info pages
def info(path, title, desc, h1, html_body):
    page(path, f'{title} | {BRAND}', desc, f'<section class="wrap prose"><h1>{h1}</h1>{html_body}<p class="legal">{LEGAL}</p></section>')

info('/about/', 'About', f'About {BRAND}, a New York City crystal and mineral brand of Wealth Edge Ventures Inc.', 'About Manhattan Crystal Market', f'''
<p class="lead">{BRAND} is an online crystal market built for New York: a single place to browse towers, clusters, raw specimens, pocket stones, carvings and stone jewelry without walking twenty blocks between shops.</p>
<p>We keep the market simple. Every piece is listed on its own page with its own photos and price, and stock levels update from our inventory system, so what you see is what is on the shelf. Many pieces are one of a kind, and when one sells it comes off the site.</p>
<h2>Who we are</h2><p>{LEGAL} Orders are checked out on Shopify through namastebookshop.com, which processes payment and fulfills orders. Products ship from New York City.</p>
<h2>What we carry</h2><ul>{''.join(f'<li><a href="/shop/{CAT_SLUG[k]}/">{E(CATS[k][0])}</a>: {E(CAT_BLURB[k])}</li>' for k in CATS)}</ul>
<h2>A note on natural stones</h2><p>Crystals and minerals are natural materials. Color, pattern, inclusions and size vary from piece to piece, and photos can look slightly different on different screens. Crystal folklore and traditions are shared for interest only and are not medical advice.</p>
<h2>Get in touch</h2><p>For order questions, use the contact details on our <a href="{SHOP}/policies/contact-information">store contact page</a>.</p>''')

def policy(path, title, slug, intro):
    info(path, title, f'{title} for {BRAND} orders.', title, f'''<p class="lead">{intro}</p>
<p>Because checkout and fulfillment run through our Shopify store, the full and current {title.lower()} is published there:</p>
<p><a class="btn" href="{SHOP}/policies/{slug}">Read the full {title.lower()}</a></p>''')
policy('/shipping/', 'Shipping Policy', 'shipping-policy', 'Orders ship from New York City. Shipping options and costs are shown at checkout before you pay.')
policy('/returns/', 'Refund Policy', 'refund-policy', 'If something is not right with your order, the refund policy below explains eligibility, timing and how to start a return.')
policy('/privacy/', 'Privacy Policy', 'privacy-policy', 'This site does not use accounts or collect payment details; checkout and payment are handled by Shopify. The privacy policy below covers the data collected at checkout.')
policy('/terms/', 'Terms of Service', 'terms-of-service', 'Purchases made through this site are completed on Shopify and governed by the terms below.')

# 404
page('/404.html', f'Page not found | {BRAND}', 'Page not found', '<section class="wrap prose"><h1>That aisle is empty</h1><p>The page you were looking for may have sold out or moved.</p><p><a class="btn" href="/shop/">Back to the market</a></p></section>', canonical=False)

# sitemap + robots
urls = ['/', '/shop/', '/about/', '/shipping/', '/returns/', '/privacy/', '/terms/'] + [f'/shop/{CAT_SLUG[k]}/' for k in CATS] + [f"/products/{x['handle']}/" for x in products]
open(os.path.join(DIST, '.nojekyll'), 'w').write('')
open(os.path.join(DIST, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{SITE}{u}</loc></url>' for u in urls) + '</urlset>')
open(os.path.join(DIST, 'robots.txt'), 'w').write('User-agent: *\nDisallow: /\n' if PREVIEW else f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')

# manifest for reporting
json.dump({'count': len(products), 'categories': {CATS[k][0]: cat_count[k] for k in CATS},
           'products': [{'title': x['title'], 'handle': x['handle'], 'gid': f"gid://shopify/Product/{x['id']}", 'category': CATS[x['cat']][0],
                         'stone': x['stone'], 'price': x['price'], 'variants': x['variants'], 'images': x['images']} for x in products]},
          open(os.path.join(ROOT, 'data', 'mcm_products.json'), 'w'), indent=1)
print(f"built {len(products)} products, preview={PREVIEW}, base={BASE!r}, site={SITE}", dict(cat_count))
