# scripts/coverage

## Current flow (graph-free)

Routine updates and new fixes work from the committed catalog
(`pricing-candidates/*.json`, assembled into `tolls-es-reviewed.json`) plus small
committed evidence files. Nothing large, nothing that lives on one disk.
Run everything with `scripts/tolls/update.sh` (see the top of TOLLS_RUNBOOK.md).

| Script | What it does |
| --- | --- |
| `sweep_terminals.cjs` | Real router journeys generated from the catalog (both ways past each road end, from beside its middle) plus `seeds.json`, replayed through the app's matcher. Reports coverage gaps with coordinates, priced journeys that drive through a main-line plaza without crossing it, and any change against the reviewed baseline `accepted.json`. |
| `fetch_area_coverage.py` | Freezes the OSM ways behind one sweep gap, fetched for that area only from Overpass at the catalog snapshot, into `audit/area-coverage/<area>.json`. Refuses unmapped booths/gantries, ways the route does not drive on, and gaps that do not join the network. |
| `fetch_plaza_gate.py` | Widens a main-line plaza gate over its mapped booth lanes into `audit/area-gates/<plaza>.json`. Refuses if the line would cut a non-motorway road. |
| `build_area_coverage.py` | Applies both kinds of evidence to the candidates (coverage only; gates only over the exact line they were measured from). |
| `build_ap6_adanero_terminal.py` | The first per-area fix (AP-6 past Adanero), kept in its original format. |
| `build_spain_candidate.py` | Assembles the candidates into `spain-integration.json` and the schema-6 `tolls-es-reviewed.json`. |
| `validate_candidates.py`, `../validate_tolls.py`, `tests/` | Integrity checks. |
| `audit_spain_integration.cjs`, `audit_general_avoidance.cjs` | National and avoidance replays of the retained journeys. |
| `export_app_fixtures.py` | Copies fixtures and the sweep's regression cases into an app checkout. |
| `import_*.py` | Tariff importers from the operators' and Ministry's published tables (hash-locked in `source-lock.json`). Graph-free. |

Evidence is additive: build steps never remove ways. To withdraw an area, delete
its evidence file and restore the affected `pricing-candidates/*.json` from Git
before rebuilding.

## One-off September 2026 build (needs a national extract that is not kept)

These scripts built the reviewed catalog in September 2026 from a national
graph (`audit/2026-09-16/spain-graph/graph.json.gz`, extracted by
`extract_spain_graph.py` from Geofabrik's `spain-260915.osm.pbf`). That extract
is no longer published and the graph file was not retained, so they cannot be
rerun as they are. Their outputs are committed and remain the source of truth;
keep the scripts as the record of how each network was derived. New coverage or
gate work uses the per-area scripts above instead.

- `audit_access_inventory.py`
- `build_ap41.py`
- `build_ap53.py`
- `build_ap636.py`
- `build_ap68_service_area.py`
- `build_ap71.py`
- `build_ap8_ap1.py`
- `build_barrier_families.py`
- `build_cadi_approaches.py`
- `build_closed_plazas.py`
- `build_iberpistas.py`
- `build_iberpistas_ap61.py`
- `build_reviewed_terminal_cuts.py`
- `build_unresolved_passages.py`
- `extract_oiartzun_access.py`
- `extract_spain_graph.py`
- `fetch_ag55_port_routes.py`
- `fetch_ap53_northern_free.py`
- `fetch_ap53_routes.py`
- `fetch_ap53_terminal_routes.py`
- `fetch_ap636_routes.py`
- `fetch_ap68_public.py`
- `fetch_ap6_adanero_terminal.py`
- `fetch_open_lane_acceptance.py`
- `find_coverage_gaps.py`
- `inventory_accesses.py`
