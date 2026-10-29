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
