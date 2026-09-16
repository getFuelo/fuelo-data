# AG-55 candidate and AC-15 access review

Disabled development work. The reference corpus does not certify national or
exhaustive access coverage.

## Independent systems

The candidate `ag55.json` covers the Arteixo–Carballo closed subsystem with four
zones, eight directed cuts and twelve directed fares. Bidueira and Carballo have
opposite collection directions, so pricing uses journey context rather than
charging both collection points. Paiosaco uses a shared bidirectional approach;
Laracha's entry and exit are separate. Cuts retain exact OSM nodes/way versions.

`ag55-pastoriza.json` separately models the 55-cent Pastoriza plaza. The operator's
2026 diagram and station inventory place it outside the closed subsystem.
Two complete A Coruña–Carballo probes add 55 + 205 = 260 cents, with one plaza
crossing and one completed OD journey, in both directions.

The 2026 operator table is the general tariff reference. Generic valid Via-T
uses an explicit range for unknown return history: daytime 50–100% and nighttime
25–50%, since the 50% night rebate precedes return rebates. Whole-cent bounds are
rounded outward because settlement of fractional cents is not specified by the
reviewed source. These are bounds, not published exact discounted amounts.
Registered large-family benefits are outside this generic profile.

## Port compensation is not a driver charge

[BOE-A-2025-490](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-490)
establishes compensation for the exempt AC-15 connection movements toward A
Coruña and Arteixo, in both directions. The operator's published 25-cent port
rows therefore cannot by themselves establish direct user liability. The four
retained AC-15 routes take distinct bypasses and quote zero. The agreement has
early-termination conditions tied to new road connections; those conditions and
the current authorized access scope must remain part of release review.

The general A Coruña–Arteixo movement still crosses the plaza and costs 55 cents.
No blank tariff cell was interpreted as zero: the port exception has an explicit
separate official source. Port endpoints are on AC-15, outside port facilities.

## Evidence and remaining work

- Twelve directed closed-system routes pass general pricing checks.
- Eight additional routes cover four port exemptions, two Pastoriza traversals
  and two combined whole journeys. One extra real plaza probe and two source-lane
  traversals supplement them.
- [2026 operator tariff PDF](https://www.autoestradas.com/storage/pdf/tarifas/2026/Tarifas-20260101.pdf)
  corroborates the source HTML and the system diagram.
- [Decree 125/2025](https://www.xunta.gal/dog/Publicados/2025/20251231/AnuncioG0765-291225-0001_es.html)
  preserves the 2025 user rates during 2026 and governs return/night eligibility.

All-lane/public-approach, partial boundary, repeated journey and exclusion tests
remain pending. The price corpus deliberately uses different entry/exit source
nodes, so opposite-direction route lengths are not a travel-time comparison.

Reproduce with `import_regional.py DOWNLOADS`, `build_closed_plazas.py`,
`build_barrier_families.py`, `fetch_od_routes.py ag55`,
`fetch_ag55_port_routes.py`, and `export_app_fixtures.py APP`.

The two public Arteixo slip roads 795695668 and 795695678 belong only to the
Pastoriza coverage. Removing their duplicate closed-system ownership prevents
false missing-OD failures on port movements. All eight combined cases are also
tested with the network order reversed.
