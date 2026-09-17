# Spanish road-toll release

Scope approved 2026-09-17: general passenger-car road tolls, with ordinary
season/time variations. No driver questionnaire or personal discounts.

## Included

35 displayed roads, 56 settlement networks, assembled from retained official
2026 tariffs and mapped charging/access geometry. Repeated crossings, joint
AP-8/AP-1 and AP-6/AP-51/AP-61 settlements, partial journeys, Cadí, Vallcarca,
AP-68 service-area return and supported whole-road avoidance are covered by
retained regression cases. Pricing uses local data, with no paid pricing API
or per-station tariff requests.

## Explicit limitations

- Unmapped special return movements (including AP-9 same-zone and Itziar
  special returns) must remain unknown when their entry/exit fare is absent.
- AP-8 GI-20 has an avoidance boundary but no independently verified fare row;
  journeys requiring that entry remain unknown. Do not alias it to another entry.
- Oñaurre payment-restricted cases have no invented general-payment fare.
- Vallvidrera can return a tariff range where the holiday rule is unresolved.
- Some road families still lack verified whole-road avoidance boundaries;
  retain the app's unsupported state rather than inventing a polygon.
- Uncovered provider toll geometry, missing entries/exits, expired tariff data
  and ambiguous charging passages remain unavailable, never an exact saving.
- Local parking/tourist/forest fees are outside the product scope. The remaining
  nine inventory points are preserved for future work, not marked free.

These are bounded limitations, not a claim that every possible trip is certified.
Provider routing errors and stale OSM data cannot be eliminated by a tariff file.

## Reproduce release checks

1. `python3 scripts/coverage/build_spain_candidate.py`
2. `python3 scripts/coverage/validate_candidates.py`
3. `python3 scripts/validate_tolls.py`
4. `python3 -m unittest discover -s scripts/coverage/tests -v`
5. `node scripts/coverage/audit_spain_integration.cjs /path/to/app`
6. `node scripts/coverage/audit_general_avoidance.cjs /path/to/app`
7. In the app: TypeScript and pricing, matching, cache/revocation, preview,
   clock, savings and route-status regression tests.

The integration audit checks the development candidate and the actual schema-6
production entry point, each in both network orders. Retained provider responses
make these reproducible tests; they are not a claim of new live traffic tests.
Publish `tolls-es-reviewed.json` before releasing the app which fetches it.
Withdrawing the file (404/410) or removing its coverage policy revokes coverage
when clients refresh, subject to the existing seven-day cache lifetime.

## Verified local result (2026-09-17)

- National replay: 1,647/1,647 passed through both audit and production pricing,
  with both network orders; eight intentionally incomplete journeys stayed unknown.
- Whole-road avoidance replay: 20/20 passed.
- App change regressions: 62/62 passed across eight suites; TypeScript passed.
- Candidate integrity: 76 files; reference consistency: 36 records;
  inventory classification safety: seven tests passed.

These changes are local and have not been pushed or installed on the phone.
