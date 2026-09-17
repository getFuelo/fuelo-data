# Tolls dataset — audit and refresh runbook

Last tariff audit: **2026-09-16**, all 36 existing ES/AD entries, tariff year 2026.

Read [the complete audit](audit/2026-09-16/README.md) and its `entries.json` before
editing or publishing. It supersedes the July 2026 full-build claims and the
old cheaper-common-case convention. Historical details remain in Git history.

## Current scope — approved 2026-09-17

The user explicitly replaced the former “100% country or off” rule with
representative validation of road tolls for passenger cars at general fares.
Parking, monument admission and tourist/forest access fees are outside this
release. Personal, residency, frequent-user and Via-T discounts are deferred.
Date/time tariff bands remain supported. Unclassified local access points are
not asserted to be free and do not block reviewed motorway/tunnel journeys.

`tolls-es-reviewed.json` is the schema-6 release consumed by the updated app.
It deliberately retains `complete:false`, with explicit coverage policy:
`verified_routes`, `road_tolls`, `light`, `general`. This is not an arbitrary
partial-data bypass: malformed data, unknown schemas, missing policy and expired
fares remain rejected. Actual journeys still need covered geometry, valid entry
and exit, and an applicable fare. Unknown prices must not produce exact savings.

The older `tolls-es.json`, candidate `coverage-status.json`, and exhaustive
inventory reports remain historical evidence, not the current release gate.
Do not set their completeness flags to conceal unresolved cases.

Release checks and exceptions: [SCOPED_RELEASE.md](SCOPED_RELEASE.md).
Publish the reviewed data before distributing the updated app; this local work
has not published either artifact. Old apps continue using the old endpoint.

## Historical publication status (superseded scope)


- Branch `feat/toll-catalog-audit`: repository PR and merge authorized on
  2026-09-16. The experimental national catalog remains a candidate; merging
  does not certify or enable it for production.
- Spain `complete: false`: missing individual plazas/gantries and OD rules,
  time/calendar rules, and incorrect coordinate associations prevent certification.
- Andorra retains coverage of its only toll tunnel; general type-1 fare EUR8.10.
- **Pedro's coverage rule:** 100% coverage for a country or its toll feature is
  off. Publishing `complete:false` will disable ES tolls in clients honoring it.
- A successful source audit or validator run does not establish exact route prices.

## General-fare release scope — 2026-09-16

Product decision: quote the general light passenger-car fare without a driver
profile. Personal residency, registration, trip-history and Via-T discounts are
future work, not release blockers. Keep original tariff sources/candidates for
traceability, but the assembled national candidate removes eligibility bands.
Date/time and route-dependent general fares remain in scope. This does not
waive public-access, geometry, national-inventory or avoidance verification.

`python3 scripts/coverage/audit_access_inventory.py` reconciles the retained
mainland/Balearic and Canary booth inventories with source records and catalog
roads. Every point retains its exact reason and evidence. Source linkage or
membership of a catalog road is NOT a lane-crossing/price certificate.

## Schema 1 and conventions

`generated` is the data revision date, not an app fetch date. IDs are stable.
`country`, `currency`, `vehicle_class`, `source`, `verified` are explicit.
`verified` means the stated reference tariff was checked, not that every route,
coordinate, lane, discount or legal ownership detail was certified.

- `price`: light-car **general/unregistered payment reference**. Do not assume
  Via-T, residency, habitual-user benefits, return trips, vehicle emissions or
  registration. The app has no eligibility profile for those benefits.
- `price_high`: higher time/season variant of **the same reference journey**.
  Legacy off-peak/normal-season ranges remain conditional. They do not include
  every possible fare (e.g. night exemptions) and cannot replace tariff rules.
- `variable`: conditions can change the price; `false` never overrides the
  need to resolve entry/exit in a ticket system.
- `model=fixed`: reference to one crossing. Calendar/eligibility may still vary.
- `model=ticket`: route-dependent reference, including aggregate multi-gate
  amounts retained in this legacy schema; never charge the stored amount per gate.
- `lat/lng`: matching reference. Verify the physical road/plaza, lane direction,
  access and charged journey. **Never snap blindly to the nearest toll_booth**:
  airport parking, abandoned roads and private service entrances have that tag too.
- `notes`: reference scope, conditions and unresolved issues, with no speculative
  future tariff changes. See the audit for source locators and before/after changes.

AUTEMA: EUR9.76 Manresa mainline, EUR3.19 Les Fonts, EUR4.90 Sant Vicenç–C55 lateral
are general category-II fares. The lateral is node2024620547 on way515278833,
not the mainline. Operator calculator was checked for card/no-discount/no-register
on 2026-09-16. Both directions and all lane matches still require route tests.

## Refresh procedure

1. Fetch each official source and verify tariff year, vehicle class, entry/exit,
   barrier and payment/calendar conditions. For PDF matrices inspect the row and
   column together, visually when extraction is ambiguous. Record URL, retrieval
   date, locator and SHA-256; numbers without the exact journey are insufficient.
2. Compare the same journey with the old reference. Apply only source-supported
   corrections; retain unresolved fields as audit blockers rather than guesses.
3. Audit geographic topology separately. Save OSM node/way IDs and versions,
   direction/access evidence and route fixtures. Booth proximity is not coverage.
4. Update the audit snapshot and generated/verified dates, then run
   `python3 scripts/validate_tolls.py` and `git diff --check`.
5. Before publication, validate entry/exit matrices, individual barriers, both
   directions, partial journeys, exclusions, dates/hours and general-payment
   profiles in the app. Do not turn `complete` back on until blockers are closed.
6. Local commits were authorized by Pedro for this work; **no push was authorized**.
   Publication requires coordinated app/data cache invalidation and verification
   of CDN contents. Never change shared OSM data as part of a tariff refresh.

## Remaining countries and watch items

France and Portugal have no toll catalogue here and must remain unsupported.
AP-68 requires a new official-source review at the November 2026 concession
transition; do not infer that the whole corridor becomes free. Remove temporary
road-closure claims unless their current operational status is independently
verified. Full current per-entry findings are in the linked audit, not duplicated
in this runbook.

## Schema-2 local candidate checkpoint (2026-09-16)

`tolls-ad.json` now includes verified pricing networks: finite directed gates,
integer-cent tariffs, validity/timezone, OSM way versions and geometry provenance.
Envalira has real route tests in both directions plus the free mountain route and
an exact polygon exclusion. See `audit/2026-09-16/envalira-v2/README.md`.
This supersedes the earlier note that both directions were still untested.

`pricing-candidates/` contains incomplete M-12 and AP-51 work, never country
coverage. Spain stays `complete: false`. Schema 1 scalar prices remain audit
references; the new app will not present them as verified route totals.

Run the offline catalog validator and the app's schema/route/tariff tests before
any future publication. Device validation and explicit release remain separate.
No CDN update is part of this checkpoint.

## Schema 5: unresolved physical passages

Schema 5 preserves schema-4 shared settlements and adds optional country-level
`unresolvedPassages`: each has a unique `id`, known `tollId`, finite two-point
`line`, HTTPS `source` and `checked` date. A passage is an uncertainty guard,
not a fee, an exemption, an access restriction or an avoidance instruction.
Crossing/touching it invalidates the route quote even when routing reports no
tolls. Legacy clients must reject schema 5 rather than ignore these guards.

The development Spain assembly includes the unclassified Vallcarca bypass.
Its cut is generated from way 265459454/v9 and retained under
`audit/2026-09-16/networks/c32/unresolved-passages.json`; paid source lanes are
regression-tested separately. Publication remains blocked until the condition
is resolved. Neither the guard nor a passing behavior test certifies that the
bypass is legal, free or subject to the normal plaza tariff.

## Current local validation checkpoint (2026-09-16)

See `audit/2026-09-16/integration-validation.json` for the current hashes and
results: 1,998 distinct app tests, TypeScript, 76 candidate integrity checks, and
1,488 national integration cases in both catalog orders. Nine integration
cases deliberately return unavailable. The command still exits nonzero because
Vallcarca's physical passage remains unverified. All 35 readiness entries remain
false. Device acceptance and performance measurement have not been performed.
These results supersede the earlier checkpoint counts, not the open blockers.


### Vallcarca resolution (2026-09-16; supersedes unresolved-passage notes above)

The outer carriageway is Via 1 AALT in Generalitat project MT-14042-A2,
June 2019, drawing 2.3, PDF page 370. It has separate toll equipment outside
the canopy. July 2026 Street View corroborates the exclusive Via-T sign and
barrier. The operator explains that the circular T denotes exclusive Via-T
payment. It is a paid plaza lane, not a free bypass or an unknown exemption.
See `audit/2026-09-16/networks/c32/valhalla-mismatch.json` in the data repository
for source links and the official PDF hash. No Google geometry was traced.

The existing OSM way 265459454/v9 is included in the same plaza crossing plane,
extended only to cover that physical lane. All existing mapped lane crossings
remain single charges. The retained Valhalla toll=false trace now quotes the
published general 842 cents once. Payment-device lane guidance is not added;
conditional customer discounts must not be inferred from the chosen lane.

The national candidate no longer emits the historical Vallcarca uncertainty
cut; generic schema-5 guard regressions remain. National integration: 1,488/1,488
pass in both orders, eight partial-journey safeguards, no unresolved passage in
this retained corpus, exit 0. Focused regressions: 194 passed. All 76 catalog
integrity checks and TypeScript pass. Spain readiness remains false pending
the other documented coverage checks and device acceptance. No push or OSM edit.

### General-fare coverage follow-up

- General-only assembly passes 1,497 retained journeys in both catalog orders;
  eight intentionally incomplete journeys remain explicitly unavailable.
- Puigcerdà–Berga exposed missing GIV-4034 entrance geometry at Cadí. Run
  `python3 scripts/coverage/build_cadi_approaches.py` after the fixed-network and
  free-corridor builders, before assembling Spain. The gate/fare/tolerance stay
  unchanged. Four public-endpoint paid/avoided cases are retained.
- The operator's 2026 AP-6/AP-51/AP-61 matrix marks starred cross-branch cells
  as non-realizable; they are not missing prices to invent or add together.
- Access reconciliation currently leaves 39 point records to review across the
  mainland/Balearic and Canary extracts. Reconciled source/road links are NOT
  exhaustive access/route certification. Spain remains incomplete.

### AP-68 service-area and AP-53 urban acceptance

AP-68 now prices the published Bilbao–Arrigorriaga service area–Bilbao return
at 235 cents. The physical booth settles the outbound journey and a downstream
logical cut opens the already-paid continuation to Bilbao. No generic same-origin
fare is added; unknown entries still fail closed. Run `build_ap68_service_area.py`
after `build_closed_plazas.py`, before country assembly. Its retained local graph
contains the source road, booth and versions. Public A-8 approach geometry is
marked free only on the three reviewed source ways.

Public Santiago–Silleda routes now verify 435 cents, or zero with exact app
exclusions, in both directions. National integration passes 1,502/1,502 cases
in both catalog orders; eight intentionally partial journeys remain unavailable.
AP-68 regressions: 467 passed. AP-53 regressions: 54 passed. TypeScript and
76 candidate integrity checks pass. No release, push or device install.

Access review now retains all incident ways (including local roads) and their
node tags, rather than relying on the major-road extract alone. The current
report has 13 remaining unclassified points; linked points do not by themselves
certify a route total. Spain remains incomplete.

Cadí general-fare network acceptance is now closed: source-backed single plaza,
both public paid/avoided directions, GIV-4034 approach, partial travel after the
plaza, missing provider flag, and repeated-crossing composition. The last three
are pricing regressions over retained geometry, not new live driving trials.
`fixedNetworkBoundaries.test.ts`: ten checks pass for Cadí and AP-46. Spain
publication remains blocked by other network/inventory entries.

## Public avoidance checkpoint — 2026-09-16

- 145 additional retained provider lane traversals pass against the assembled
  candidate, including exactly one expected financial event per open barrier.
- 20 public-endpoint selective-avoidance responses cover ten systems in both
  directions. Exclusions now call the app's `roadAvoidanceLines` against the
  assembled catalog: AG-55 includes Pastoriza; Gipuzkoa includes shared AP-8/AP-1
  boundaries and independent open plazas. Regional fences alone are insufficient.
- Santurtzi entry moved after its western ramp merge. Oiartzun AP-8 exit moved
  before the local-road merge, preserving all twelve published eastern journeys.
- The GI-20 entry is explicitly mapped but has no fabricated OD fares. A route
  requiring that unsupported fare must remain unavailable. This is still an
  eastern-corridor pricing blocker, even though the public avoidance cases pass.
- AP-68 Bilbao service-area return closes at its physical booth for 235 cents,
  then opens an already-paid zero-additional continuation; no generic self fare.
- Inventory now has nine unclassified source points. Country readiness remains
  false; these changes do not satisfy every other road's release checklist.

After rebuilding base candidates, run the postprocessors in this order:

```sh
python3 scripts/coverage/build_ap68_service_area.py
python3 scripts/coverage/build_reviewed_terminal_cuts.py
python3 scripts/coverage/build_pastoriza_urban_approach.py
python3 scripts/coverage/build_general_avoidance.py
python3 scripts/coverage/build_spain_candidate.py
python3 scripts/coverage/export_app_fixtures.py /path/to/app
```

Run `audit_general_avoidance.cjs /path/to/app` separately from the independent
published-fare integration audit. Its route totals are diagnostic; its assertions
are full-road exclusion, no target pricing events, and available pricing of the
result. Avoiding Supersur can legitimately retain a different AP-68 charge.
