# Tolls dataset — audit and refresh runbook

Last tariff audit: **2026-09-16**, all 36 existing ES/AD entries, tariff year 2026.

Read [the complete audit](audit/2026-09-16/README.md) and its `entries.json` before
editing or publishing. It supersedes the July 2026 full-build claims and the
old cheaper-common-case convention. Historical details remain in Git history.

## Current publication status

- Local branch `feat/toll-catalog-audit`; no push/CDN publication in this task.
- Spain `complete: false`: missing individual plazas/gantries and OD rules,
  time/calendar rules, and incorrect coordinate associations prevent certification.
- Andorra retains coverage of its only toll tunnel; general type-1 fare EUR8.10.
- **Pedro's coverage rule:** 100% coverage for a country or its toll feature is
  off. Publishing `complete:false` will disable ES tolls in clients honoring it.
- A successful source audit or validator run does not establish exact route prices.

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
