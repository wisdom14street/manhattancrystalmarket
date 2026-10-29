#!/usr/bin/env python3
"""Download the public catalog from namastebookshop.com (only products published to the Online Store)."""
import json, urllib.request, os, sys
OUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'all_products.json')
allp = []
for page in range(1, 1000):  # loop until Shopify returns an empty page
    req = urllib.request.Request(f"https://namastebookshop.com/products.json?limit=250&page={page}",
                                 headers={"User-Agent": "ManhattanCrystalMarket-build/1.0"})
    d = json.load(urllib.request.urlopen(req, timeout=60))
    if not d['products']:
        break
    allp += d['products']
    print(f"page {page}: {len(allp)}", file=sys.stderr)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(allp, open(OUT, 'w'))
print(f"saved {len(allp)} products")
