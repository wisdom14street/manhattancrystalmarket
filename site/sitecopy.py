"""Manhattan Crystal Market (manhattancrystalmarket.com): crystals, minerals and stone jewelry. Copy written for this site only."""
import re, types
E = __import__('html').escape
ICON = 'gem'
FAM_LABEL, FAM_ALL, STYLE_LABEL, STYLE_ALL = 'Stone', 'All stones', 'Origin', 'All origins'
NO_FAMILY = ()

# ---- product mix (product_type -> aisle), unchanged from the original crystal site ----
_TYPES = {
 "towers": ["Crystal Tower Obeliak","Crystal Tower Obeliak Generator","Crystal Points","CrystalS Point","Cut Base Crystal Point","Cutbase Cluster / Point","Crystal D/T Stones Points","Crystal Flame","Aura Quartz Points, Cluster, Tower","Aura Quartz Points, Cluster, Tower, Heart","Crystal Wand","Healing Stick Magic Wand","Healing Stick Wand"],
 "clusters": ["Clusters Crystal","Crystal Geode","Enhydro Quartz","Crystal Gem Tree"],
 "specimens": ["Crystals Specimens","Crystal specimen","Crystal specime","Crystal Rough Raw","Fossils Crystal","Crystal Polished Slabs, POF, Irregular","Crystal Polished Slabs, POF","Crystals Slabs POF","Free Form Crystals","Naturally Polished Faceted Crystal","Gallery Pieces Crystals Stones","Crystals","Crystal","Polished Crystal","Stones"],
 "tumbled": ["Crystal Tumbled","Worry Stones Crystals","Crystal Gallet","Crystal Palmstone Gallet","Palm Stone","Cube Crystal","chakra Stone Kit Set","Massager Crystal Gua Sha","Massage Therapy Stone"],
 "carvings": ["Crystal Sphere","crystal Heart","Crystal Carving","Crystal Eggs","Crystal Skulls","Pyramid","Orgone Pyramids","Merkaba Crystal"],
 "jewelry": ["Crystal Bead Bracelets","Crystal Pendant","Crystal Necklace","Crystal Bracelet","Crystal Earrings","Crystal Jewelry","Crystal Beads Mala","Crystal Mala","Wire Wrapped Pendant","SS Wire Wrap Pendant","Plated Stone Pendant","Plated Stone Earrings","Plated Stone Ring","Plated Stone Necklace","Black Cord Stone Necklace","Cuff Crystal Bracelets","Crystal Heart Pendant","Link Stone Bracelet","Crystal & Beads Adjustable Bracelet","Sterling Silver RIngs","Sterling Silver Pendant","Sterling Silver Necklace","Sterling Silver Earrings","Adjustable Sterling Silver Bracelet"],
}
_T2C = {t: k for k, ts in _TYPES.items() for t in ts}
_STONE_RE = re.compile(r'\b(amethyst|quartz|citrine|labradorite|moonstone|malachite|turquoise|lapis|jade|obsidian|tourmaline|rose|smoky|fluorite|pyrite|selenite|carnelian|agate|jasper|aventurine|tiger|opal|garnet|peridot|onyx|hematite|calcite|celestite|apatite|kyanite|larimar|rhodonite|rhodochrosite|sodalite|chrysocolla|amazonite|aquamarine|emerald|ruby|sapphire|topaz|moldavite|shungite|sunstone|howlite|prehnite|unakite|bloodstone|azurite|iolite|spinel|tanzanite|morganite|chalcedony|ametrine|angelite|lepidolite|charoite|seraphinite|sugilite|jet|amber|pearl|gemstone|stone|crystal)', re.I)
def category(p):
    t = p.get('product_type', ''); c = _T2C.get(t)
    if c is None: return None
    if t.startswith('Sterling Silver') or t == 'Adjustable Sterling Silver Bracelet':
        if not _STONE_RE.search(p['title']): return None
    return c

# ---- stones act as the "family" facet ----
_ST = [('Rose Quartz', r'rose quartz'), ('Clear Quartz', r'clear quartz|crystal quartz|quartz crystal'), ('Smoky Quartz', r'smok(e)?y quartz'),
 ('Aura Quartz', r'\baura\b|angel aura|titanium'), ('Amethyst', r'amethyst'), ('Citrine', r'citrine'), ("Tiger's Eye", r"tiger'?s? ?eye"),
 ('Moonstone', r'moonstone'), ('Tourmaline', r'tourmaline'), ('Obsidian', r'obsidian'), ('Pyrite', r'pyrite'), ('Malachite', r'malachite'),
 ('Lapis Lazuli', r'lapis'), ('Fluorite', r'fluorite'), ('Labradorite', r'labradorite'), ('Aquamarine', r'aquamarine'), ('Agate', r'agate'),
 ('Jasper', r'jasper'), ('Kyanite', r'kyanite'), ('Garnet', r'garnet'), ('Jade', r'\bjade\b'), ('Hematite', r'hematite'), ('Carnelian', r'carnelian'),
 ('Moldavite', r'moldavite'), ('Selenite', r'selenite'), ('Aventurine', r'aventurine'), ('Rhodochrosite', r'rhodochrosite'), ('Shungite', r'shungite'),
 ('Lepidolite', r'lepidolite'), ('Turquoise', r'turquoise'), ('Chrysocolla', r'chrysocolla'), ('Sodalite', r'sodalite'), ('Calcite', r'calcite'),
 ('Sunstone', r'sunstone'), ('Amazonite', r'amazonite'), ('Black Onyx', r'onyx'), ('Howlite', r'howlite'), ('Amber', r'\bamber\b'), ('Quartz', r'quartz')]
def _slug(n): return re.sub(r'[^a-z0-9]+', '-', n.lower()).strip('-')
FAMILIES = [(_slug(n), n, rx) for n, rx in _ST]
_ORIG = ['Brazil', 'Madagascar', 'India', 'Peru', 'Pakistan', 'Congo', 'Mexico', 'Morocco', 'Uruguay', 'South Africa', 'Russia', 'Afghanistan', 'Afganistan', 'Indonesia',
         'Argentina', 'China', 'Nepal', 'Czech Republic', 'Namibia', 'Arkansas', 'Bolivia', 'Australia', 'Canada', 'Tanzania', 'Zambia']
def style_of(t, b, base):
    for o in _ORIG:
        if re.search(r'\b' + o + r'\b', t, re.I): return 'Afghanistan' if o == 'Afganistan' else o
    return ''

# ---- brands: only vendors that are real brands; supplier codes (Nirvana Inc, OCNLKW, yngint, drftpb, vlorg, vlgorgn, BNJINT, KHPINT,
# NAGIMPINC, Pkstn, SDNIMP, Crtnnpl, Village Original Inc, Ocealic Linkways, Tiemoko Toure, indiana Gems International, Benjamin International,
# Consignments, Namaste Bookshop) are wholesalers or the store itself and get no brand page ----
_BRANDS = [('heaven-earth', 'Heaven & Earth', r'heaven ?& ?earth', ['Heaven & Earth LLC', 'HVNRTH']),
           ('starborn', 'Starborn', r'\bstarborn\b', ['STARBORN']),
           ('crystal-earth-studio', 'Crystal Earth Studio', r'crystal earth studio', ['crystal Earth Studio']),
           ('zorbitz', 'Zorbitz', r'zorbitz', ['ZORBITZ Inc'])]
_V = {v: k for k, _, _, vs in _BRANDS for v in vs}
def _brand_of(title, vendor=''):
    for k, _, rx, _ in _BRANDS:
        if re.search(rx, title, re.I): return k
    return _V.get(vendor or '', '')
BR = types.SimpleNamespace(NAME={k: n for k, n, _, _ in _BRANDS}, brand_of=_brand_of, FACTS={})

AISLES = {
 'towers': ('Towers & Points', 'Towers', 'towers-points', 'Standing towers, generators, obelisks and natural points, from palm-sized to statement pieces.', '#7b5cff'),
 'clusters': ('Clusters & Geodes', 'Clusters', 'clusters-geodes', 'Druzy clusters, geodes and gem trees that catch the light on a shelf or desk.', '#2fb39a'),
 'specimens': ('Specimens & Raw', 'Specimens', 'specimens-raw', 'One-of-a-kind mineral specimens, raw rough, slabs and free forms for collectors.', '#e0913a'),
 'tumbled': ('Tumbled & Pocket Stones', 'Pocket Stones', 'tumbled-pocket-stones', 'Tumbled stones, palm stones, worry stones and cubes made to be carried and handled.', '#e2557a'),
 'carvings': ('Spheres, Hearts & Carvings', 'Carvings', 'spheres-hearts-carvings', 'Polished spheres, hearts, eggs, skulls, pyramids and hand-carved figures.', '#3c8be0'),
 'jewelry': ('Crystal Jewelry', 'Jewelry', 'crystal-jewelry', 'Beaded bracelets, pendants, necklaces, rings and earrings set with real stones.', '#c9a227'),
}
def assign(x): return x['base']
READINGS = 'https://namastebookshop.com/pages/book-a-reading'

VISIT_EYEBROW = 'Visit the crystal floor'
def STORE_DESC(S): return f'Crystal shop near Union Square with about {S.ABOUT_N:,} crystals, minerals and stone jewelry pieces at 2 West 14th Street.'
REVIEW_TITLE = 'Took a crystal home with you?'
REVIEW_TEXT = 'Share a quick Google review of the crystal floor. It helps other New Yorkers looking for crystals near Union Square find us.'
LOGO_SVG = '<svg viewBox="0 0 40 40"><path d="M20 2 33 14 20 38 7 14Z" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M7 14h26M20 2l-6 12 6 24 6-24z" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'
WORDMARK = '<b>Manhattan</b> Crystal Market'
BAR_TEXT = 'Visit us: 2 West 14th Street, near Union Square'
SEARCH_PLACEHOLDER = 'Search amethyst, towers, bracelets, Brazil'

QUIZ = {
 'slug': 'crystal-finder', 'nav': 'Crystal finder', 'cta': 'Find my crystal',
 'title': 'Crystal Finder Quiz', 'desc': 'Three questions to find crystals in stock today at 2 West 14th Street near Union Square, by intention, shape and budget.',
 'h1': 'Find your crystal', 'lead': 'Pick an intention, a shape and a budget, and we will pull matching pieces from what is on the floor today. The intentions follow popular crystal traditions and are shared for interest only, not as medical or other advice. Your answers never leave this page.',
 'submit': 'Show my crystals',
 'questions': [
  {'q': 'What intention are you working with?', 'options': [
    {'label': 'Calm and rest (amethyst, lepidolite, selenite)', 'filter': {'fam': ['amethyst', 'lepidolite', 'selenite']}},
    {'label': 'Love and self-care (rose quartz, rhodochrosite)', 'filter': {'fam': ['rose-quartz', 'rhodochrosite']}},
    {'label': 'Grounding and protection (obsidian, tourmaline, smoky quartz, hematite)', 'filter': {'fam': ['obsidian', 'tourmaline', 'smoky-quartz', 'hematite', 'black-onyx']}},
    {'label': 'Abundance (citrine, pyrite, aventurine)', 'filter': {'fam': ['citrine', 'pyrite', 'aventurine']}},
    {'label': 'Clarity and focus (clear quartz, fluorite)', 'filter': {'fam': ['clear-quartz', 'fluorite', 'quartz']}}]},
  {'q': 'What would you like it to be?', 'options': [
    {'label': 'Something to wear', 'filter': {'aisle': ['jewelry']}},
    {'label': 'A pocket or palm stone', 'filter': {'aisle': ['tumbled']}},
    {'label': 'A tower, sphere or heart for display', 'filter': {'aisle': ['towers', 'carvings']}},
    {'label': 'A cluster, geode or raw specimen', 'filter': {'aisle': ['clusters', 'specimens']}}]},
  {'q': 'Budget?', 'options': [
    {'label': 'Under $25', 'filter': {'maxp': 25}}, {'label': 'Under $75', 'filter': {'maxp': 75}}, {'label': 'Show me everything', 'filter': {}}]},
 ]}

def FOOTER_EXPLORE(S):
    return [('Crystal finder quiz', '/crystal-finder/'), ('Stones A to Z', '/stones/'), ('Crystal shopping near Union Square', '/crystal-shop-near-union-square/'),
            ('Crystal care guide', '/guide/crystal-care/'), ('Gifts under $25', '/crystal-gifts-under-25/'), ('Book a reading', READINGS)]
FOOT_BLURB = 'The crystal floor on 14th Street: towers, clusters, specimens, pocket stones, carvings and stone jewelry, every piece listed online.'
HERO_BASES = ('towers', 'clusters', 'carvings', 'specimens')
def HERO(S):
    return {'eyebrow': '2 West 14th Street &middot; Union Square &middot; New York City',
            'h1': 'Visit our crystal floor at 2 West 14th Street, <em>steps from Union Square.</em>',
            'lede': f'About {S.ABOUT_N:,} crystals, minerals and stone jewelry pieces, priced from {S.money(S.MIN_PRICE)}. Open daily from 11 AM.' + (f' Reserve online, skip the shipping wait and pick up in store; orders are {S.READY.lower()}.' if S.PICKUP_ON else ''),
            'shop_cta': 'Shop crystals online'}
def _stones(S):
    top = [(k, n) for k, n, _ in FAMILIES if S.fam_count[k] >= 5]
    top = sorted(top, key=lambda kn: -S.fam_count[kn[0]])[:18]
    chips = ''.join(f'<a class="chip" href="/stones/{k}/">{E(n)} <small>{S.fam_count[k]}</small></a>' for k, n in top)
    return f'<section class="wrap"><div class="sechead"><h2>Shop by stone</h2><a href="/stones/">All stones A&ndash;Z &rarr;</a></div><div class="chips">{chips}</div></section>'
def _best(S): return S.by_rank(S.leaders)[:8] if S.HAS_RANK else []
def _new(S): return S.leaders[:8]
def _value(S): return S.by_rank([x for x in S.leaders if x['price'] < 25])[:8]
def _whys(S):
    return [(f'About {S.ABOUT_N:,} pieces online', 'Every crystal has its own photos, price and live stock, so you can choose before you come in.'),
            (f'Prices from {S.money(S.MIN_PRICE)}', 'Prices are listed on every piece, including pocket stones and bracelets under $25.'),
            (('Pick up in about 2 hours' if '2 hour' in S.READY else 'Reserve, then pick up', f'Choose Pickup at checkout and collect at 2 West 14th Street once your ready email arrives. Orders are {S.READY.lower()}.') if S.PICKUP_ON else ('', '')),
            ('Secure checkout', 'Payment is handled by Shopify through namastebookshop.com; nothing is stored on this site.'),
            ('Readings with Namaste', f'Pair your visit with a tarot or intuitive reading. <a href="{READINGS}" rel="noopener">See readers and book</a>.'),
            ('Easy to reach', 'About 0.2 miles from both the 14 St&ndash;Union Square and 14 St/6 Av subway stations.')]
HOME_SECTIONS = [
 {'type': 'html', 'html': _stones},
 {'type': 'grid', 'title': 'Best sellers', 'select': _best, 'href': '/shop/', 'link': 'Shop all', 'intro': 'Ranked by the store’s own best-selling order at namastebookshop.com, refreshed daily.'},
 {'type': 'visit'},
 {'type': 'collections', 'title': 'Featured collections', 'items': [
   {'title': 'Towers & points', 'blurb': 'Statement pieces for a shelf or desk.', 'href': '/shop/towers-points/', 'filter': {'aisle': ['towers']}},
   {'title': 'Amethyst', 'blurb': 'Clusters, points and jewelry.', 'href': '/stones/amethyst/', 'filter': {'fam': ['amethyst']}},
   {'title': 'Crystal bracelets & pendants', 'blurb': 'Real stones to wear every day.', 'href': '/shop/crystal-jewelry/', 'filter': {'aisle': ['jewelry']}},
   {'title': 'Clusters & geodes', 'blurb': 'Druzy that catches the light.', 'href': '/shop/clusters-geodes/', 'filter': {'aisle': ['clusters']}},
   {'title': 'Spheres & hearts', 'blurb': 'Polished, hand-sized carvings.', 'href': '/shop/spheres-hearts-carvings/', 'filter': {'aisle': ['carvings']}},
   {'title': 'Gifts under $25', 'blurb': 'Pocket stones, bracelets and more.', 'href': '/crystal-gifts-under-25/', 'filter': {'maxp': 25}}]},
 {'type': 'grid', 'title': 'New on the floor', 'select': _new, 'href': '/shop/?sort=new', 'link': 'See what is new'},
 {'type': 'whys', 'title': 'Why shop with us', 'items': _whys},
 {'type': 'grid', 'title': 'Best value: favorites under $25', 'select': _value, 'href': '/crystal-gifts-under-25/', 'link': 'All under $25'},
 {'type': 'quiz', 'title': 'Not sure which crystal?', 'text': 'Pick an intention, a shape and a budget; we will show pieces in stock today.'},
 {'type': 'brands', 'title': 'Makers we carry', 'n': 8},
 {'type': 'review'},
 {'type': 'band', 'title': 'Reserve online, pick up in store', 'text': lambda S: 'Every listing has its own photos, price and live stock. Reserve a piece online and collect it on 14th Street, or have it shipped from New York City.',
  'steps': lambda S: [('Find it', 'Filter by aisle, stone, origin or price.'), ('Choose Pickup at checkout', f'Pay securely on Shopify. Orders are {S.READY.lower() or "prepared quickly"}.'), ('Collect it', S.STORE_ADDR + ', once your ready email arrives.')]},
]
def HOME_TITLE(S): return 'Manhattan Crystal Market | Crystal Shop at 2 W 14th St near Union Square, NYC'
def HOME_DESC(S): return f'Visit our crystal floor at {S.STORE_ADDR}, near Union Square, Flatiron, Chelsea and Greenwich Village. About {S.ABOUT_N:,} crystals from {S.money(S.MIN_PRICE)}, with in-store pickup.'
def SHOP_TITLE(S): return 'Shop Crystals Online, Pick Up Near Union Square | Manhattan Crystal Market'
def SHOP_DESC(S): return f'Browse {S.N:,} crystals, minerals and stone jewelry pieces from {S.money(S.MIN_PRICE)}. Reserve online and pick up at 2 West 14th Street, NYC, or have it shipped.'
SHOP_H1 = 'Shop the market'
def SHOP_SUB(S): return f'{S.N:,} pieces in stock across {len(S.AISLE_KEYS)} aisles. Filter by stone, maker, origin or price.'
def AISLE_TITLE(S, k): return f'{AISLES[k][0]} in NYC near Union Square | Manhattan Crystal Market'
def AISLE_DESC(S, k): return f'{AISLES[k][3]} {S.cat_count[k]} pieces at Manhattan Crystal Market, 2 West 14th Street, NYC. Reserve online and pick up in store or have it shipped.'

def LANDINGS(S):
    L = []
    for k, n, _ in FAMILIES:
        c = S.fam_count[k]
        if c < 5: continue
        L.append({'path': f'/stones/{k}/', 'title': f'{n} Crystals in NYC near Union Square | Manhattan Crystal Market',
                  'desc': f'{c} {n.lower()} pieces in stock at 2 West 14th Street: towers, tumbled stones, carvings, specimens and jewelry. Reserve online and pick up near Union Square.',
                  'h1': f'{n}', 'sub': f'{c} {n.lower()} pieces on the crystal floor today.', 'filter': {'fam': [k]}})
    L.append({'path': '/crystal-gifts-under-25/', 'title': 'Crystal Gifts Under $25 in NYC | Manhattan Crystal Market', 'desc': 'Pocket stones, bracelets, pendants and small carvings under $25 near Union Square.',
              'h1': 'Crystal gifts under $25', 'sub': 'Small, real-stone gifts that are easy to say yes to.', 'filter': {'maxp': 25}})
    return L

def brand_intro(S, k, st):
    name = S.BRAND_NAME[k]
    return (f'<p>We carry {st["n"]} piece{"s" if st["n"] != 1 else ""} from {E(name)}, mostly {E(" and ".join(S.AISLES[a][0].lower() for a, _ in st["aisles"].most_common(2)))}, priced from {S.money(st["min"])}. '
            'Each listing below shows its own photos and live price.' + (' Reserve online and pick up at 2 West 14th Street.' if st['pickup'] else '') + '</p>')
def brand_faq(S, k, st):
    name = S.BRAND_NAME[k]
    return [(f'Where can I buy {name} in New York City?', f'At Manhattan Crystal Market, 2 West 14th Street, near Union Square. {st["n"]} {name} pieces are in stock today.'),
            (f'How much is {name}?', (f'From {S.money(st["min"])} to {S.money(st["max"])}' if st['max'] > st['min'] else S.money(st['min'])) + ' right now; prices update daily.')]
def BRAND_H1(S, k): return f'{S.BRAND_NAME[k]} crystals and jewelry in NYC'
def BRAND_TITLE(S, k, st): return f'{S.BRAND_NAME[k]} near Union Square, NYC | Manhattan Crystal Market'
def BRAND_DESC(S, k, st): return f'{st["n"]} {S.BRAND_NAME[k]} pieces from {S.money(st["min"])} at Manhattan Crystal Market, 2 West 14th Street. Pick up in store or ship.'
def BRANDS_TITLE(S): return 'Crystal & Jewelry Brands A to Z | Manhattan Crystal Market'
def BRANDS_DESC(S): return 'Every named crystal and stone-jewelry maker we stock at 2 West 14th Street, with live counts. Shop most of the floor by stone instead.'
BRANDS_H1 = 'Brands A to Z'
def BRANDS_LEAD(S, n): return f'{n} named makers are in stock today. Most of our crystals come from mineral wholesalers rather than branded makers, so the best way to browse them is by <a href="/stones/">stone, A to Z</a>.'

PAIR = {'towers': ['tumbled'], 'clusters': ['tumbled'], 'specimens': ['tumbled'], 'carvings': ['tumbled'], 'tumbled': ['jewelry'], 'jewelry': ['tumbled']}
REL_BRAND = 'More from {brand}'
REL_SCENT = 'More {scent}'
REL_PAIR = 'Add a pocket stone or bracelet'
REL_MORE = 'More {aisle}'
def describe(S, x):
    a = x['aisle']; fam = S.FAM_NAME.get(x['family'], '')
    kind = {'towers': 'tower or point', 'clusters': 'cluster', 'specimens': 'specimen', 'tumbled': 'hand-sized stone', 'carvings': 'polished carving', 'jewelry': 'piece of jewelry'}[a]
    stn = f'{fam.lower()} ' if fam and fam != 'Quartz' else ''
    s = [f"{E(x['title'])} is a {stn}{kind} chosen for the Manhattan Crystal Market collection."]
    if x['style']: s.append(f"Sourced from {x['style']}, as listed in its title.")
    s.append('Natural stones are never identical, so expect small differences in color, pattern and size from the photo.' if a == 'jewelry' else 'Every mineral grows differently, so color, shape and size vary slightly from piece to piece.')
    if x['noimg']: s.append('A photo is on its way; call 646-876-1401 and we can describe the piece, or see it on the floor.')
    s.append('Ships from New York City, or see it in person at 2 West 14th Street, near Union Square. Secure checkout is completed on Shopify.')
    return s
def PRODUCT_DESC(S, x, v0): return f"{x['title']} for {S.money(v0['price'])}. " + ('Reserve online and pick up at 2 West 14th Street near Union Square, or ship from NYC.' if x['pickup'] else 'See it at 2 West 14th Street near Union Square or ship from NYC.')

def ABOUT_DESC(S): return 'About Manhattan Crystal Market, the crystal floor at 2 West 14th Street, a brand of Wealth Edge Ventures Inc.'
ABOUT_H1 = 'About Manhattan Crystal Market'
def ABOUT(S):
    return f'''<p class="lead">Manhattan Crystal Market is the crystal floor inside the store at {S.STORE_ADDR}, on 14th Street just west of Fifth Avenue and a few minutes' walk from Union Square.</p>
<p>Come in to see towers, clusters, raw specimens, pocket stones, carvings and stone jewelry up close, or browse about {S.ABOUT_N:,} pieces online first. Every piece online has its own photos and price, and stock updates daily from the same inventory the floor uses.{" Reserve a piece online and choose Pickup at checkout to collect it in store." if S.PICKUP_ON else ""}</p>
<h2>Visit</h2><p>{S.STORE_ADDR}. Call <a href="tel:{S.TEL}">{S.PHONE}</a>.</p>{S.hours_html()}{S.visit_buttons()}
<h2>Who we are</h2><p>{S.LEGAL} Online orders are checked out on Shopify through namastebookshop.com, which processes payment and fulfills orders, including in-store pickups. Products ship from New York City.</p>
<h2>What we carry</h2><ul>{''.join(f'<li><a href="/shop/{AISLES[k][2]}/">{E(AISLES[k][0])}</a>: {E(AISLES[k][3])}</li>' for k in S.AISLE_KEYS)}</ul>
<h2>Readings</h2><p>Tarot and intuitive readings are available through Namaste. <a href="{READINGS}" rel="noopener">See the readers and book a reading</a>.</p>
<h2>A note on natural stones</h2><p>Crystals and minerals are natural materials. Color, pattern, inclusions and size vary from piece to piece. Crystal folklore and traditions are shared for interest only and are not medical advice.</p>'''
VISIT_TITLE = 'Visit Our Crystal Floor near Union Square'
def VISIT_DESC(S): return f'Directions, hours, subway lines and in-store pickup for Manhattan Crystal Market at {S.STORE_ADDR}, near Union Square, Flatiron, Chelsea and Greenwich Village.'
def VISIT_LEAD(S): return f'Our crystal floor is at {S.STORE_ADDR}, on 14th Street just west of Fifth Avenue, where Greenwich Village, Chelsea, the Flatiron District and Union Square meet.'
def FAQ_DESC(S): return 'Answers about Manhattan Crystal Market: location, hours, in-store pickup, shipping, natural variation in crystals and how to choose a stone.'
FAQ_H1 = 'Crystal floor FAQ'
def FAQ(S):
    return [('Where is Manhattan Crystal Market?', f'At {S.STORE_ADDR}, on 14th Street just west of Fifth Avenue, about a 4-minute walk from the 14 St&ndash;Union Square subway station.'),
            ('What are your hours?', 'Monday to Thursday 11 AM to 8 PM, Friday and Saturday 11 AM to 9 PM, Sunday 11 AM to 7 PM. Holiday hours may differ.'),
            ('Can I reserve a crystal online and pick it up?', 'Yes. Tap Buy now, choose Pickup at checkout, and come in once you get the email saying your order is ready.' + (f' Orders are {S.READY.lower()}.' if S.READY else '')),
            ('Will my crystal look exactly like the photo?', 'Natural stones vary in color, pattern and size. Where a listing shows a specific piece, that is the piece you get; for assorted items, expect small differences. Call us if you want a description first.'),
            ('Do you ship?', 'Yes, from New York City. Shipping options and costs are shown at checkout before you pay.'),
            ('How do I choose a crystal?', 'Many people start with a stone whose color or tradition speaks to them. Our <a href="/crystal-finder/">crystal finder</a> suggests in-stock pieces, and the <a href="/stones/">stones A to Z</a> page lists everything we carry.'),
            ('How do I care for crystals?', 'Dust them with a soft dry cloth, keep soft or water-sensitive stones such as selenite out of water, and keep colored stones out of strong sun. See our <a href="/guide/crystal-care/">crystal care guide</a>.'),
            ('Do crystals have healing powers?', 'We share crystal traditions for interest only. They are not medical advice or a substitute for professional care.'),
            ('Can I book a reading?', f'Yes, tarot and intuitive readings are available through Namaste. <a href="{READINGS}" rel="noopener">See readers and book</a>.')]

def GUIDES(S):
    letters = {}
    for k, n, _ in sorted(FAMILIES, key=lambda f: f[1]):
        if S.fam_count[k]: letters.setdefault(n[0].upper(), []).append((k, n))
    az = '<nav class="az" aria-label="Jump to letter">' + ''.join(f'<a href="#s-{L}">{L}</a>' for L in sorted(letters)) + '</nav>' + ''.join(
        f'<h2 id="s-{L}">{L}</h2><ul class="dir">' + ''.join((f'<li><a href="/stones/{k}/">{E(n)}</a>' if S.fam_count[k] >= 5 else f'<li><a href="/shop/?fam={k}">{E(n)}</a>') + f' <span class="small">{S.fam_count[k]} pieces</span></li>' for k, n in items) + '</ul>' for L, items in sorted(letters.items()))
    return [
     {'path': '/stones/', 'title': 'Crystals & Stones A to Z', 'desc': 'Every stone on the Manhattan Crystal Market floor, A to Z, with live piece counts: amethyst, rose quartz, citrine, labradorite and more.', 'h1': 'Stones A to Z',
      'html': f'<p class="lead">Every stone we have in stock today, with live counts. Pick one to see all its towers, pocket stones, carvings, specimens and jewelry.</p>{az}'},
     {'path': '/guide/crystal-care/', 'title': 'Crystal Care: Cleaning, Water, Sunlight and Storage', 'desc': 'Simple care for crystals and stone jewelry: how to clean, which stones to keep dry, sun-sensitive stones and how to store them.', 'h1': 'Crystal care guide',
      'html': '''<p class="lead">Most crystals need very little care. A few simple habits keep them looking their best.</p>
<h2>Cleaning</h2><p>Dust with a soft, dry cloth or a soft brush. For hard, polished stones such as quartz, a quick rinse in plain water and a thorough dry is fine.</p>
<h2>Keep these dry</h2><p>Soft or water-sensitive stones, including selenite, should not be soaked. When in doubt, keep a stone dry.</p>
<h2>Sunlight</h2><p>Strong, direct sun can fade some colored stones over time, amethyst and rose quartz among them. Display them out of a sunny window.</p>
<h2>Storage</h2><p>Store pieces apart or wrapped so harder stones do not scratch softer ones, and keep jewelry away from perfume and lotions.</p>
<p>Questions about a specific piece? Call <a href="tel:+16468761401">646-876-1401</a> or ask on the floor.</p>'''},
     {'path': '/crystal-shop-near-union-square/', 'title': 'Crystal Shop Near Union Square, Flatiron, Chelsea & the Village', 'store_ld': True,
      'desc': f'Looking for a crystal shop near Union Square? Manhattan Crystal Market is at {S.STORE_ADDR}, between Greenwich Village, Chelsea and the Flatiron District, with about {S.ABOUT_N:,} pieces and in-store pickup.',
      'h1': 'Crystal shopping near Union Square', 'html': f'''<p class="lead">If you are searching for a crystal shop near you in Manhattan, 2 West 14th Street is easy to reach from most of downtown and midtown.</p>
<h2>Where we are</h2><p>{S.STORE_ADDR}, on 14th Street just west of Fifth Avenue. Union Square is about 0.2 miles to the east.</p>
<h2>Coming from nearby neighborhoods</h2><ul><li><b>Union Square and Gramercy:</b> walk west on 14th Street past Union Square West and University Place to Fifth Avenue.</li>
<li><b>Flatiron and NoMad:</b> walk south on Fifth Avenue to 14th Street.</li><li><b>Chelsea:</b> take the 1, 2, 3, F, M or L to 14th Street and walk east.</li>
<li><b>Greenwich Village and the West Village:</b> walk north on Fifth Avenue, or take the 1, 2 or 3 to 14 St.</li><li><b>East Village:</b> take the L west to 14 St&ndash;Union Square, or walk west on 14th Street.</li></ul>
<h2>What you will find</h2><ul><li>About {S.ABOUT_N:,} pieces listed online across {len(S.AISLE_KEYS)} aisles, priced from {S.money(S.MIN_PRICE)}.</li><li>Browse by <a href="/stones/">stone, A to Z</a>, or try the <a href="/crystal-finder/">crystal finder</a>.</li>
{f"<li>Reserve online and pick up in store; orders are {S.READY.lower()}.</li>" if S.PICKUP_ON else ""}<li>Tarot and intuitive readings through Namaste. <a href="{READINGS}" rel="noopener">Book a reading</a>.</li></ul>{S.visit_block()}'''},
    ]
NOT_FOUND = 'That aisle is empty'
