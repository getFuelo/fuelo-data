# fuelo-data

Aggregated fuel-station price data for Spain, France and Andorra.

A GitHub Action runs every 6 hours, fetches the public datasets, normalizes
brand names, and commits the resulting JSON to this repo. The Fuelo mobile
app fetches these files via jsDelivr — one CDN-cached request per country
instead of pounding the upstream government APIs from every device.

## Files

- `stations-es.json` — Spain (Ministerio para la Transición Ecológica)
- `stations-fr.json` — France (data.economie.gouv.fr)
- `stations-ad.json` — Andorra (sig.govern.ad ArcGIS FeatureServer)
- `brand-typos.json` — manual canonical-brand mapping; edit to fix new typos
- `scripts/fetch.py` — the ingestion script
- `.github/workflows/refresh.yml` — the cron

## URLs (jsDelivr)

```
https://cdn.jsdelivr.net/gh/getFuelo/fuelo-data@main/stations-es.json
https://cdn.jsdelivr.net/gh/getFuelo/fuelo-data@main/stations-fr.json
https://cdn.jsdelivr.net/gh/getFuelo/fuelo-data@main/stations-ad.json
```

## Run locally

```
pip install requests
python scripts/fetch.py
```
