import re
# product_type -> category
CATS = {
 "towers": ("Towers & Points", ["Crystal Tower Obeliak","Crystal Tower Obeliak Generator","Crystal Points","CrystalS Point","Cut Base Crystal Point","Cutbase Cluster / Point","Crystal D/T Stones Points","Crystal Flame","Aura Quartz Points, Cluster, Tower","Aura Quartz Points, Cluster, Tower, Heart","Crystal Wand","Healing Stick Magic Wand","Healing Stick Wand"]),
 "clusters": ("Clusters & Geodes", ["Clusters Crystal","Crystal Geode","Enhydro Quartz","Crystal Gem Tree"]),
 "specimens": ("Specimens & Raw", ["Crystals Specimens","Crystal specimen","Crystal specime","Crystal Rough Raw","Fossils Crystal","Crystal Polished Slabs, POF, Irregular","Crystal Polished Slabs, POF","Crystals Slabs POF","Free Form Crystals","Naturally Polished Faceted Crystal","Gallery Pieces Crystals Stones","Crystals","Crystal","Polished Crystal","Stones"]),
 "tumbled": ("Tumbled & Pocket Stones", ["Crystal Tumbled","Worry Stones Crystals","Crystal Gallet","Crystal Palmstone Gallet","Palm Stone","Cube Crystal","chakra Stone Kit Set","Massager Crystal Gua Sha","Massage Therapy Stone"]),
 "carvings": ("Spheres, Hearts & Carvings", ["Crystal Sphere","crystal Heart","Crystal Carving","Crystal Eggs","Crystal Skulls","Pyramid","Orgone Pyramids","Merkaba Crystal"]),
 "jewelry": ("Crystal Jewelry", ["Crystal Bead Bracelets","Crystal Pendant","Crystal Necklace","Crystal Bracelet","Crystal Earrings","Crystal Jewelry","Crystal Beads Mala","Crystal Mala","Wire Wrapped Pendant","SS Wire Wrap Pendant","Plated Stone Pendant","Plated Stone Earrings","Plated Stone Ring","Plated Stone Necklace","Black Cord Stone Necklace","Cuff Crystal Bracelets","Crystal Heart Pendant","Link Stone Bracelet","Crystal & Beads Adjustable Bracelet","Sterling Silver RIngs","Sterling Silver Pendant","Sterling Silver Necklace","Sterling Silver Earrings","Adjustable Sterling Silver Bracelet"]),
}
TYPE2CAT={t:k for k,(n,ts) in CATS.items() for t in ts}
STONES = "amethyst quartz citrine labradorite moonstone malachite turquoise lapis jade obsidian tourmaline rose clear smoky fluorite pyrite selenite carnelian agate jasper aventurine tiger opal garnet peridot onyx hematite calcite celestite apatite kyanite larimar rhodonite rhodochrosite sodalite chrysocolla amazonite aquamarine emerald ruby sapphire topaz moldavite shungite sunstone howlite prehnite unakite bloodstone azurite iolite spinel tanzanite morganite chalcedony ametrine angelite lepidolite charoite seraphinite sugilite jet amber pearl gemstone stone crystal".split()
STONE_RE=re.compile(r'\b('+'|'.join(STONES)+r')',re.I)
def category(p):
    t=p.get('product_type','')
    c=TYPE2CAT.get(t)
    if c is None: return None
    if t.startswith('Sterling Silver') or t=='Adjustable Sterling Silver Bracelet':
        if not STONE_RE.search(p['title']): return None
    return c
