# AP-53 OD conversion — 2026-09-16

Development candidate only; Spain remains incomplete.

The official 2026 matrix is retained with its URL, PDF hash and printed rows in
`pricing-candidates/ap53-tariffs.json`. ACEGA and BOE-A-2025-7166 document Via-T
return/monthly benefits and terminal aliases. Without journey history, schema 3
preserves an explicit 0..general Via-T interval; general payment is an exact fare.
An older app rejects schema 3 instead of reading the lower bound as a zero price.

The candidate maps 212 versioned source ways and 11 directed gates. Shared ramp
plazas have opposite entry/exit roles. One-way terminal collection uses logical
entry cuts on the opposite carriageway. Silleda's separate southbound entry is
mapped independently. Gate evidence is in `provenance.json`.

Retained real Valhalla evidence:

- 20 directed inter-zone journeys match published general fares.
- Two nearby N-525 alternatives and both AP-53/AG-59 directions cost zero.
- Eight journeys between Santiago and the four individual southern accesses
  match the terminal fare; twelve internal southern-zone movements are free.
- Four baseline/exclusion cases preserve the N-525 alternative. The southern
  baseline costs 5.35 EUR; the north baseline already chooses the free road.
  Both excluded routes cost zero. Tests compare the request polygons with the
  actual app implementation.

BOE-A-2008-16770 documents the northern exemption. The 1999 concession decision
(https://www.lamoncloa.gob.es/consejodeministros/referencias/paginas/1999/c2910990.aspx)
documents the free southern internal movements. Individual coverage ways carry
source evidence; AG-53 and N-525 approach evidence is distinguished from AP-53.
Free coverage never exempts an actual charged gate crossing.

Rebuild with `build_ap53.py`; explicitly fetch with `fetch_ap53_routes.py`,
`fetch_ap53_free_routes.py`, `fetch_ap53_northern_free.py`,
`fetch_ap53_terminal_routes.py`, and `fetch_ap53_avoidance.py`. Export using
`export_app_fixtures.py APP_CHECKOUT`; run `ap53Routes.test.ts`. These fetchers
skip retained responses, run outside the app, and do not call a paid routing API.

Remaining: all-lane approach review, remaining Tras do Eixo/northern boundary
cases, national inventory and release integration. Passing reference journeys
are not a claim that every Spanish road or arbitrary partial journey is verified.
