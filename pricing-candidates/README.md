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

**Known unresolved bypass:** the Vallcarca trace uses OSM way 265459454, a
separate carriageway south of the roof, without toll or access restrictions in
current OSM. This is not a shifted copy of the paid lane. Its access/payment
conditions remain unresolved; the IGN orthophoto alone cannot establish them.
See `audit/2026-09-16/networks/c32/valhalla-mismatch.json`. Production cannot
turn this unflagged response into a zero quote while country data is incomplete.

Outstanding work includes closed-system entry/exit mapping and joint settlement,
AP-636 partial trips, eastern Gipuzkoa tariffs, Vallvidrera holidays, recurrence
eligibility, inventory classification and exhaustive free-road/avoidance cases.
No national dataset is ready for publication or device release.

The AP-53 follow-up now adds a mapped OD candidate and 22 real reference routes
(20 general paid zone pairs and two nearby N-525 alternatives). See
`audit/2026-09-16/networks/ap53/README.md` for source identities, reproduction and
remaining terminal-zone, eligibility and avoidance gaps. This does not change
Spain's incomplete status.

## Latest validated checkpoint — 2026-09-16

This supersedes the earlier AP-53-only checkpoint. AP-53 now has 48 real probes,
including individual southern accesses, internal free movements, AG-59 and exact
app exclusions. AP-41 has 56 OD journeys; AP-71 has twelve OD journeys and four
full/avoidance cases; AP-36 has thirty OD journeys; Cartagena–Vera has 72.
Nine additional open AP-7 plazas/ramps have 41 source-lane traversals and real
plaza responses with normal, summer and Easter rates.

Schema 3 carries explicit unknown-history intervals and source-backed free
coverage. AP-53 Via-T uses 0..general; AP-71 uses 50..100% of its day/night fare.
Payment exclusion conditions prevent a general band from conflicting with its
Via-T interval. General reference prices exclude unselected rebates.

App validation: 542 passing tests in 30 suites and TypeScript. Offline validation:
42 candidate JSON files and all 36 original tariff/geometry snapshot records.
The release validator still fails, and additionally requires an explicit ready
flag for every entry, a complete national manifest and a complete served schema.
No push, deployment, country activation or device installation.

## AP-66, Vallvidrera and R-2 checkpoint — 2026-09-16

- AP-66: twelve OD cases and four full/avoidance routes. Campomanes cuts now
  avoid the N-630 grade-separated crossing. Via-T intervals use the published
  reduced cents, including EUR 6.47 rather than a rounded percentage of EUR 16.20.
- Vallvidrera: four source lanes and six real routes, including free alternatives
  with the app's exact exclusions. Unresolved weekday holidays retain EUR 4.70–5.28.
- R-2: thirty OD journeys, two verified zero-fare Guadalajara Norte–Taracena
  directions, two urban plazas/four lanes, and four full journeys. Corrected
  Alcalá entry/exit associations. Full urban totals are inferred from mapped
  crossings and published open-plaza fees; no operator receipt was verified.
  Avoidance must still preserve the free Guadalajara movement.
- Canary Islands now have a separately hashed OSM extract and nine reviewed
  booth contexts. Parking/visitor admission is separated from motorway tariffs;
  Papagayo's vehicle access fee and remaining access classification are explicit.

Validation: 610 tests in 33 suites and TypeScript pass; 46 candidate JSON files
and 36 original audit records pass offline integrity. National release remains
blocked, all networks remain not-ready, and Spain stays disabled. Local only.

## AP-636 and R-2 avoidance checkpoint — 2026-09-16

- AP-636 now has twelve retained real routes: four independent gantry traversals,
  four Deskarga OD journeys, two whole-road traversals and two free alternatives.
  The 52-cent Antzuola TAG journey replaces the 155-cent Deskarga charge.
  Two truncated tunnel regressions reject missing journey context.
- All thirty R-2 directed avoidance probes quote zero. The Guadalajara Norte–
  Taracena pair retains its original polyline exactly. Four shared paid-plaza
  cuts cover paid pairs while preserving both ends of that free movement.
- Avoidance endpoints on committed approaches/one-way exit ramps were moved
  to identified public junctions. Initial no-path responses remain auditable.

Validation: all 656 tests in 34 suites and TypeScript pass; 47 candidate JSON
files and 36 original snapshot records pass offline integrity. National release
remains blocked. All changes are local; no country activation or publication.

### AG-55 / AG-57 candidate checkpoint (2026-09-16)

AG-55 now has 12 closed-system OD routes, independent Pastoriza pricing and
four source-backed exempt AC-15 directions; combined trips are invariant under
network order. AG-57 adds 24 directed OD routes with separate Ramallosa ramp
gates. Both preserve unknown Via-T return history as bounded prices. All remain
disabled pending the explicit access, avoidance and national release worklist.

### R-3 / R-4 / R-5 route mapping (2026-09-16)

86 published paid OD directions and two source-backed R-3 free directions now
match their expected gates and general/Via-T/night prices. Close-ramp false
crossings are corrected without widening matching tolerance. Original failing
probes are retained. Access, avoidance and national-release work remains open;
these three candidates remain disabled.

### AP-9 ordinary published journeys (2026-09-16)

Five subsystem candidates retain 84 single-system routes, including the free
Morrazo–Vigo pair. Six independent Coruña totals verify Ferrol/Norte composition
and catalog-order invariance. Unknown Via-T history is a bounded price. Two
same-origin/destination rows and the documented access, free-section, avoidance
and release checks remain open. Spain remains disabled; all work is local.

### AP-6 / AP-51 / AP-61 isolated journey mapping (2026-09-16)

42 native directed pairs now have retained route probes, including Vicolozano–
Ávila and Hontoria–Segovia exemptions. The N-603 alternative to Ortigosa–Otero
is a separate zero-price regression. Night/peak variations remain distinct.
Twelve AP-6/AP-51 combined routes are retained for integration; they are not yet
certified by the isolated-system tests. Shared settlement and the remaining
access/avoidance work keep all three candidates and Spain disabled.
