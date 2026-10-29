# Manhattan Crystal Market (preview)

Static storefront for Manhattan Crystal Market, a brand of Wealth Edge Ventures Inc.
Products come from the public catalog of the Shopify store namastebookshop.com (only products published
to the Online Store, in stock, with photos, in crystal product types; see `scripts/catmap.py`).
Buy buttons use Shopify cart permalinks
`https://namastebookshop.com/cart/<VARIANT_ID>:1?attributes[Storefront]=Manhattan Crystal Market`.
Product pages re-check live price and stock in the browser from
`https://namastebookshop.com/products/<handle>.js`. No API tokens or secrets are used anywhere.

## Build
    python3 scripts/fetch.py                       # download the public catalog into data/
    python3 scripts/build.py --preview             # noindex preview build into dist/
    python3 scripts/build.py --preview --base=/manhattancrystalmarket \
        --site=https://wisdom14street.github.io/manhattancrystalmarket   # GitHub Pages subpath build
    python3 scripts/build.py                       # production build for https://manhattancrystalmarket.com

## Hosting
`.github/workflows/pages.yml` builds the preview on every push to `main` and daily, and deploys it to
GitHub Pages. Requires Settings > Pages > Build and deployment > Source = "GitHub Actions".
When going live on the domain: drop `--preview`, set `--site=https://manhattancrystalmarket.com`, remove `--base`.

## Store visit details (verified Oct 29, 2026)
- Address and hours: namastebookshop.com/pages/contact (Mon-Thu 11-8, Fri-Sat 11-9, Sun 11-7). Edit HOURS in scripts/build.py if they change.
- Phone shown: 646-876-1401 (Crystal Shop line, owner-provided). Shopify's pickup location lists 212-645-0141.
- Pickup: `scripts/pickup.py` reads Shopify's public Local Pickup text per variant at build time; the site only shows
  "Reserve online, pick up in store" for pieces Shopify reports as pickup-available.
- Transit: 14 St-Union Sq (4 5 6 L N Q R W) and 14 St/6 Av (F M L, connected to 1 2 3), each ~0.2 mi (OpenStreetMap geocode).
