# Tolls dataset — build & refresh runbook

> **Read this fully before refreshing `tolls-*.json`.** It records exactly where
> each price came from and every intricacy, so any future run (Claude or human)
> can refresh without re-deriving anything.
>
> Last full build: **2026-07-17** · Tariff year covered: **2026**

## What this is

Curated per-toll dataset served from this repo via jsDelivr, exactly like
`stations-*.json` and `history-*.json`:

```
cdn.jsdelivr.net/gh/getFuelo/fuelo-data@main/tolls-es.json
cdn.jsdelivr.net/gh/getFuelo/fuelo-data@main/tolls-ad.json
```

The app matches a route's toll-flagged segments (from the router — Valhalla, see
STRATEGY.md) to entries here and sums the light-vehicle prices to show estimated
toll cost + a per-toll "pay this one?" picker. **The app-side integration is not
built yet** (still OSRM); this dataset ships ahead of it.

## File format

Object with a self-dating header (we deliberately store `generated` so the app's
freshness stamp can show *data* age, not fetch time — a mistake we made with the
stations files):

```jsonc
{
  "generated": "YYYY-MM-DD",   // when this file was last rebuilt
  "schema": 1,
  "currency": "EUR",
  "tolls": [ { …toll… } ]
}
```

Each toll:

| field | meaning |
|-------|---------|
| `id` | stable slug, `<cc>-<name>` |
| `country` | `es` / `ad` / `pt` / `fr` |
| `name`, `road`, `operator` | human labels |
| `lat`, `lng` | gate/plaza location (see coordinate note) |
| `model` | `fixed` = single flat price (tunnels, barriers) → **exact**. `ticket` = closed/OD system, price depends on entry **and** exit → the stored `price` is a **representative** full-traversal value, NOT per-gate. |
| `vehicle_class` | `light` (only class we serve) |
| `price` | representative light-vehicle €, **telepeaje / off-peak / normal season** |
| `price_high` | optional higher variant (peak, cash, or summer). `null` if none |
| `variable` | `true` if peak / seasonal / time-of-day / payment-method variation exists — UI should render `~€X` |
| `source` | exact URL the number came from |
| `verified` | date the number was last checked against source |
| `notes` | everything else — the intricacy log |

**Convention for `price` vs `price_high`:** always store the *cheaper, most
common* case in `price` (telepeaje, off-peak, normal season) and the pricier
variant in `price_high`. Never inflate `price`; overclaiming poisons trust (same
principle as the savings meter).

## Refresh procedure

Tariffs change **once a year, effective 1 January** (France 1 Feb). A monthly
task is belt-and-suspenders — most months nothing changes. Each run:

1. For every entry, re-fetch its `source`, find the current light-vehicle price,
   compare to the stored `price`/`price_high`. Update + bump `verified`.
2. Update the top-level `generated` date.
3. Work through **Coverage / pending** below — add any newly-collected entries.
4. Append anything you learned to the per-entry notes here.
5. Hand the changed files to Pedro to commit + push (do NOT git-commit yourself).
   After first push of a *new* filename, hit `purge.jsdelivr.net/gh/getFuelo/fuelo-data@main/<file>`
   (jsDelivr negative-caches unknown paths).

PDF extraction that works here: `curl -sL <url> -o x.pdf && pdftotext -layout x.pdf -`.

## Per-entry provenance (the intricacy log)

### AD — Túnel d'Envalira `ad-envalira` (fixed, €8.10)
- Source: operator tuneldenvalira.com/en/rates. Confirmed via Diari d'Andorra /
  Altaveu (Dec 2025): 2026 light-vehicle (Tipus 1) = **€8.10**, up from €7.90 (+2.5%).
- Annual formula: Oct YoY CPI of AD/ES/FR blended (per concession contract).
- Gotcha: 50% discount for Pas de la Casa residents/workers + Andorran transport
  firms — we serve the **non-resident** price.
- Only tolled road in Andorra.

### ES — Túnel del Cadí `es-cadi` (fixed, €14.56)
- Source: tunels.cat/es/tarifas-tuneles-del-cadi. 2026 Category 2 (light) = **€14.56**
  (~+2.82% vs 2025). Flat — no peak/season. Operator Tabasa (Abertis).
- The Barcelona↔Andorra chokepoint — Pedro's #1 toll.

### ES — Túnels de Vallvidrera `es-vallvidrera` (fixed, €4.70 / €5.28)
- Source: tunels.cat/es/tuneles-de-vallvidrera. 2026 Category 2: **€4.70 off-peak,
  €5.28 peak** (~+2.99%). Peak = weekdays **07:30–10:30 & 17:00–21:00**. Same operator.

### ES — Radial R-2 `es-r2` (ticket, repr. €4.60 / €5.20)
- Source PDF: `…/tarifas_r2_2026.pdf` (SEITT). **Closed/ticket** — price = f(entry, exit).
- Stored `price` = full run **Aeropuerto ↔ NII-Taracena**: telepeaje €4.60 / cash €5.20.
- Free **00:00–06:00**. 21% VAT included. Effective 1 Jan 2026.
- Full light-vehicle OD matrix (telepeaje / cash), barriers
  Aeropuerto · Alcobendas · Ajalvir · Alcalá · Meco · Cabanillas · Guadalajara Norte · NII-Taracena:
  - Aeropuerto→Alcobendas 0.55/0.60 · Ajalvir→Alcalá 0.85/0.95 · Ajalvir→Meco 1.75/2.00 ·
    Ajalvir→Cabanillas 2.85/3.20 · Ajalvir→Guadalajara N 3.90/4.35 · Ajalvir→NII-Taracena 4.60/5.20 ·
    Alcalá→Meco 0.95/1.05 · Meco→Cabanillas 1.10/1.25 · Cabanillas→Guadalajara N 1.10/1.20 ·
    Guadalajara N→NII-Taracena 0.00 (free segment). (Re-pull PDF for the complete grid.)

### ES — Radial R-4 `es-r4` (ticket, repr. €5.50 / €6.15)
- Source PDF: `…/tarifas_r4_2026_0.pdf` (SEITT). **Closed/ticket**.
- Stored `price` = full run **M-50 ↔ Ocaña/A-40**: telepeaje €5.50 / cash €6.15.
- Free 00:00–06:00. 21% VAT. 8 points: M-50 · Pinto-Parla · Valdemoro · Seseña ·
  Villaseca Sagra (CM-4001) · Aranjuez · Ontígola · Ocaña/A-40.
- OD sample (telepeaje/cash): M-50→Pinto-Parla 0.55/0.60 · M-50→Valdemoro 1.25/1.40 ·
  M-50→Seseña 2.30/2.55 · M-50→Aranjuez 3.30/3.65 · M-50→Ocaña 5.50/6.15 ·
  Pinto-Parla→Ocaña 4.80/5.35 · Valdemoro→Ocaña 4.25/4.75 · Aranjuez→Ocaña 2.05/2.25.
  (Full matrix in the PDF — re-pull to regenerate.)

### ES — AP-15 `es-ap15` (open barrier / sum, €9.23 / €14.05)
- OPEN barrier, NOT closed ticket: troncales Sarasa 2.65/1.77, Tiebas 4.55/2.99,
  Marcilla 6.85/4.47 + enlaces Marcilla 3.45/2.29, Zuasti 0.90/0.59 (base / Via-T
  registrado). price = full Irurzun↔AP-68 with AUDENASA-registered Via-T (9.23);
  price_high = cash/unregistered (14.05). Round trip <72h: return leg free. No
  time/season variation.
- Sources: Acuerdo Gobierno de Navarra 23-12-2025 (BON 258; bon.navarra.es
  connection-resets from non-ES networks — figure-verified via mirror) + audenasa.es
  `Tarifas-2026-web.pdf` / `Tarifas-2026-Recorrido.pdf`.
- Concession ends 8-Jun-2029 → Gobierno announced (Feb-2026) free for turismos after.
- AP-15 is Navarra's ONLY regional toll (A-10/A-12/A-15/A-21 free). AP-68 crosses
  Navarra but is the state entry already in the file.

### ES — Bidegi (Gipuzkoa): `es-ap8-gipuzkoa` €11.52, `es-ap1-gipuzkoa` €7.56, `es-ap636` €2.79
- One official PDF covers all three: bidegi.eus → "Tarifas vigentes en € a partir de
  01.01.2026" (`documents/42696171/0/2026__AP-8_AP-1_AP-636_tarifak.pdf/…`).
- AP-8: Ermua↔Behobia, 75 km, closed. Full 11.52 (Ermua-Donostia 8.37 + Donostia-
  Behobia 3.15). The joint matrix also prices through-trips into Bizkaia (Interbiak)
  and Bilbao↔Behobia — use the Gipuzkoa-only cells.
- AP-1 tolled section = Bergara↔Etxabarri-Ibiña, 31.9 km (Isuskitza tunnel), NOT
  Etzegarate; beyond toward Vitoria/Burgos is state + free. Full 7.56.
- AP-636 = Beasain↔Bergara, FREE-FLOW (no booths; Beasain/Ezkio/Deskarga portals +
  Antzuola semi). Full = computed sum 0.42+0.82+1.55 = 2.79. Mandatory except
  motorcycles; plate pre-registration required without Via-T.
- NO cash/telepeaje/peak price difference anywhere at Bidegi — discounts are monthly
  TAG refunds (round-trip −0.59 at select plazas; progressive 25/55/75% from 6+
  transits; 38.02 €/month cap).

### ES — Interbiak (Bizkaia): `es-ap8-bizkaia` €5.93, `es-supersur` €2.05, `es-artxanda` €1.55
- Legal basis: Decreto Foral 147/2025 (BOB 248, 30-12-2025) + Interbiak PDFs.
  interbiak.bizkaia.eus is behind a WAF — plain curl 403s; use a browser UA.
- AP-8 Bizkaia: Galdakao↔límite Gipuzkoa; full (Accesos Oeste→Límite) 5.93.
  Iurreta–Abadiño stays FREE in 2026 (proposal to drop tarifa-0 was dropped).
  1.05 € OBE local-hop adjustment; EV −25% with OBE; resident subsidy per DF 108/2025.
- Supersur (VSM): Arrigorriaga↔Santurtzi; full 2.05. Night tarifa-0 ABOLISHED for 2026.
- Artxanda: fixed 1.55 per crossing, charged BOTH directions, free-flow gantries;
  night tarifa-0 abolished 2026. Túnel 2 closed from 3-Feb-2026 (~6 months).
- All Interbiak light prices are flat — no peak/payment variation at the gate
  (benefits are after-the-fact refunds).

## Coordinate note
Tunnel/plaza coords here are **approximate** (portal or plaza, hand-placed) and
flagged in each `notes`. To refine: OSM `barrier=toll_booth` via Overpass, e.g.
`node["barrier"="toll_booth"](area.<iso>);out;`. Good enough for segment matching;
tighten when the app integration lands. (OSM toll-booth tagging is solid — PT alone
had 409 nodes; ES/FR autoroute networks are densely mapped.)

## Coverage / pending (NOT yet in the JSON — with how to get each)

Staged deliberately (Pedro's rule: ship what's real, flag the rest). Priority =
Pedro's corridors (AD↔BCN done; Madrid next).

### ES — remaining still-tolled 2026 roads: **ALL ADDED (2026-07-18)** — kept for reference
Master list + confirmation of what still charges: Ministerio press release
`transportes.gob.es/…/mar-30122025-1746` (30-12-2025).
- **SEITT radiales R-3 & R-5** — shared "Accesos de Madrid" concession; the R-2/R-4
  filename pattern (`tarifas_r3_2026*.pdf`) 404'd — find the real link from the
  SEITT tariffs index page. Ticket model, same 00–06 free rule.
- **AP-6 / AP-51 / AP-61** (Villalba–Adanero + Ávila + Segovia spurs) — Madrid NW,
  relevant to Pedro. Concessionaire Castellana/Iberpistas. Ticket model.
- **AP-66** (León–Asturias), **AP-68** (Bilbao–Zaragoza), **AP-71** (León–Astorga),
  **AP-9** (Galicia), **AP-46** (Málaga), **AP-7** sections (Málaga–Guadiaro, Cartagena).
- **AP-7 Estepona–Guadiaro** — official per-barrier PDF confirmed at
  `cdnfomento.blob.core.windows.net/…/autopista-ap-7,-estepona---guadiaro-2026.pdf`
  (Manilva troncal €2.45, acceso €1.20). **SEASONAL**: summer "special" tariff (Jun–Sep
  + ~17 Easter days) raises non-habitual prices ~+65% → store normal in `price`,
  summer in `price_high`, `variable:true`.
- Source pattern for concession autopistas: ministry "peajes-actuales" PDFs on
  `cdnfomento.blob.core.windows.net/portal-web-transportes/carreteras/nuestrared/autopistaspeaje/peajes-actuales/autopista-<road>-<year>.pdf`
  — **not a guaranteed complete index** (that stronger claim was refuted); probe per road.
- `es-*` note: **most Spanish AP went free in 2021**; the tolled set is small — this is
  finishable.

### PT — Portugal (defer; medium effort)
- IMT HTML tables: `imt-ip.pt/…/taxas-de-portagem/` — 2026 Class-1 per-section prices,
  HTML only (scrape). Covers Brisa/Brisal/Douro Litoral + Lusoponte. Per-section (lanço), ticket-like.
- Ex-SCUT electronic-only roads NOT on IMT → Infraestruturas de Portugal.
- **Single-toll-route trick** (Pedro's idea) for the electronic network: IP's route
  calculator `portagens.infraestruturasdeportugal.pt` returns a route TOTAL. Request a
  short route that crosses exactly ONE gantry → total = that gantry's price. Backend is
  an undocumented ASMX POST (`Portagens.asmx/ObterCustoP…`) consumed by the map UI;
  routing itself is OSRM+OSM. Locations: OSM `barrier=toll_booth` (409 nodes in PT).
- No open dataset on dados.gov.pt. Annual update, CPI per concession (~2% band).

### FR — France (defer; hardest)
- Locations (machine-readable): data.gouv.fr **"Gares de péage du réseau routier
  national concédé"** — CSV/ZIP, open licence, Lambert93 coords + PR points. **No prices.**
- Prices: ASFA `autoroutes.fr/fr/les-principaux-tarifs.htm` — 2026 trajet (OD) tariffs
  as HTML + a journey simulator; no CSV/API. Full per-gare grids only in individual
  concessionaire PDFs (Vinci/ASF, APRR, Sanef). Entry×exit ticket system → section model.
  2026 rise ~0.86%, effective **1 Feb**. Same single-toll-route trick applies via the simulator.

### Buy-vs-build
Commercial APIs (TollGuru etc.) cover ES/PT/FR but charge per-request + restrict
caching → not worth it for this small, annually-static, Spain-heavy scope. Build.

## STATUS (2026-07-18): tolls-es.json is `complete: true` — READY TO SERVE
34 ES entries (12 state AGE + 8 SEITT + 5 Catalonia + 2 Galician autonomic + 1 Navarra
+ 3 Gipuzkoa Bidegi + 3 Bizkaia Interbiak), each with an official source + quoted 2026
light-vehicle price. State list cross-checked against the ministry's 30-12-2025 release
— no still-tolled 2026 state road is missing (the "AP-8 Bilbao–Solares state toll" is a
phantom: that corridor is the free state A-8; AP-7 Circunvalación de Alicante confirmed
free by BOE-A-2025-25961). Entries needing later precision work: **AP-9** (segmented, no
single full-run price — modelled with the largest OD €8.80), **M-12** (open two-point
toll — computed sum), **AP-636** (free-flow — computed sum of 3 segments). Watch items:
**AP-68** concession ends 10-11 Nov 2026 (re-verify); **AP-15** concession ends Jun 2029.

Hard rule (Pedro): **100% coverage for a country or the toll feature is OFF for that
country.** Partial coverage = a wrong total on some route = broken trust. The app must
gate the toll UI on `complete === true` per country.

## Change log
- **2026-07-18 (b)** — ES completed: added AP-15 (Audenasa, BON 258), Gipuzkoa Bidegi
  (AP-8/AP-1/AP-636, official 2026 PDF) and Bizkaia Interbiak (AP-8/Supersur/Artxanda,
  DF 147/2025) → 34 entries, flipped `complete: true`. State-list re-check vs the
  ministry 30-12-2025 release: nothing missing — "AP-8 Bilbao–Solares" confirmed a
  phantom (free state A-8); AP-7 Circ. Alicante free per BOE-A-2025-25961. AP-68 notes
  flagged with the Nov-2026 concession end. 1.4.2 re-distributed to tester
  alourenco77@gmail.com (address confirmed by Pedro).
- **2026-07-18** — expanded ES to 27 entries via 4 parallel research agents (state AGE,
  SEITT, Catalonia, completeness sweep). All prices from official ministry PDFs /
  operator sites, quoted in notes. Marked `complete:false` pending Navarra + Basque.
  Excluded (confirmed free/shadow): AP-7 Aumar (2020), AP-4 (2020), AP-7 Acesa & AP-2
  (2021), C-32 Maresme & C-33 (2021), AP-1 Burgos (2018), Túnel de Sóller (2017),
  C-25 & Eix del Llobregat C-16 Manresa–Berga (shadow tolls, users pay nothing).
- **2026-07-17** — initial build. AD (Envalira) + ES (Cadí, Vallvidrera, R-2, R-4).
  Schema v1. Prices from deep-research (10 findings, 3-0 verified) + direct PDF pulls.
