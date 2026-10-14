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

## Station fields

Each file is a JSON array of stations: `id`, `country`, `brand`, `address`,
`city`, `province`, `schedule`, `lat`, `lng`, `prices` (only the fuels the
station sells) and `sourceUpdatedAt`.

`sourceUpdatedAt` (ISO 8601, UTC, identical for every station of a file) is
when the official source published the snapshot:

| File | `sourceUpdatedAt` |
| --- | --- |
| `stations-es.json` | the Ministry's dataset `Fecha` (Spanish local time, converted to UTC) |
| `stations-fr.json` | the dataset's `data_processed` on data.economie.gouv.fr |
| `stations-ad.json`, `stations-pt.json` | when the pipeline read the live service (neither publishes a snapshot time) |

If the source date is missing, the fetch time is used and the job logs it.
Spain's reuse terms (Ley 37/2007, art. 8) require citing the source and the
date of its last update, which is why the app shows this date. Clients that
predate the field ignore it.

Attribution, as shown in the app:

- Spain: Ministerio para la Transición Ecológica y el Reto Demográfico, with the date.
- France: DGCCRF, data.economie.gouv.fr, Licence Ouverte v2.0.
- Andorra: Govern d'Andorra, Oficina de l'Energia i del Canvi Climàtic.
- Portugal: Direção-Geral de Energia e Geologia (DGEG). Its site forbids
  commercial use, so the app keeps Portuguese prices off unless
  `app-config.json` has `"portugal_prices_enabled": true` (only once DGEG
  authorises it in writing).

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
