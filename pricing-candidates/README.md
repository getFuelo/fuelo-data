# Incomplete pricing candidates

These files are development evidence, not served country catalogs. Do not set
Spain complete or copy partial candidates to the production endpoint.

- `m12.json`: three physical gates, geometry provenance and real short Valhalla
  routes. Barajas has different northbound/southbound plazas. General daytime
  fares are 1.00/0.55 EUR; explicitly selected Via-T 0.90/0.50 EUR; 00–06 free.
  Full-road coverage and all approaches remain pending.
- `ap51-tariffs.json`: official light-vehicle general tariff references, seasonal
  calendar and direct/reverse OD rows. AP-6 joint fares are complete journey
  references and must not be added to separate AP-6 charges. Entry/exit geometry
  remains pending; the main plaza alone cannot determine the applicable row.

Source URLs, validity and evidence are recorded alongside each candidate.
App tests distinguish tariff-rule checks from actual reference-route checks.
Neither establishes country completeness. Frequent-user/resident discounts
remain unavailable unless their additional requirements are explicitly modeled.

## Expanded Spain conversion checkpoint — 2026-09-16

`coverage-status.json` tracks all 35 current ES catalog entries and the remaining
release blockers. This is **not** a claim that those entries exhaust the national
road inventory. There are 27 tariff reference files, containing 820 explicit OD
rows and 24 barrier rows; some rows are bidirectional or joint-system references,
so these counts must not be presented as distinct independently priced journeys.

Physical candidates now include M-12, Artxanda, Cadí, AP-46, Autema, C-32 and
AP-15. M-12 through traffic crosses Barajas but not the Alcobendas ramp plaza:
its standard daytime through quote is EUR 1.00, not the sum EUR 1.55. The full
M-12 approach audit remains open. Cadí uses the official 2026 PDF, not the stale
webpage footer. AP-46 includes low/high season and the 00–06 exemption.

The national graph inventory contains 756 booth/gantry nodes in 294 review groups.
Groups are geographic/connectivity review aids, **not** pricing networks. Some
are parking, obsolete infrastructure or private entrances. The 22 MB derived
`graph.json.gz` is ignored; its source hash, extraction script and review inventory
are versioned. Recreate it with `extract_spain_graph.py` using pyosmium and the
source PBF specified in `audit/2026-09-16/spain-graph/provenance.json`.

### Reproduction and release checks

- Run `import_seitt.py`, `import_ministry.py`, `import_regional.py`,
  `import_seasonal.py` and `import_reviewed_regional.py` with the directory of
  downloaded source documents. PDF text is extracted from the hashed PDF itself.
  Source changes require re-review; blank table cells never imply free travel.
- `build_barrier_families.py` builds open-plaza candidates from the local graph.
  Lane probes follow unique legal continuations through internal OSM way splits;
  they are topological traversals, not live Valhalla results.
- `fetch_barrier_probes.py` explicitly makes sequential public Valhalla requests;
  request and response evidence is retained. It is never called by the app.
- `export_app_fixtures.py APP_CHECKOUT` refreshes the app's lane/route fixtures.
- `python3 scripts/coverage/validate_candidates.py` checks offline integrity.
  `--release` must currently fail: the national mapping and corpus are incomplete.

**Known real-route disagreement:** Vallcarca returns an unflagged Valhalla
geometry south of the current OSM toll roof and misses the physical gate. See
`audit/2026-09-16/networks/c32/valhalla-mismatch.json`. Ten other open-plaza real
traversals quote their expected amounts; Vallcarca is explicitly unresolved,
not counted as a successful EUR 8.42 route. The app regression verifies that an
incomplete country cannot turn this unflagged route into a production zero quote.

Outstanding work includes closed-system entry/exit mapping and joint settlement,
AP-636 partial trips, eastern Gipuzkoa tariffs, Vallvidrera holidays, recurrence
eligibility, inventory classification and exhaustive free-road/avoidance cases.
No national dataset is ready for publication or device release.

The AP-53 follow-up now adds a mapped OD candidate and 22 real reference routes
(20 general paid zone pairs and two nearby N-525 alternatives). See
`audit/2026-09-16/networks/ap53/README.md` for source identities, reproduction and
remaining terminal-zone, eligibility and avoidance gaps. This does not change
Spain's incomplete status.
