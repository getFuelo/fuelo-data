# AP-66 development candidate

Four economic access zones, eight directed cuts, twelve published OD fares.
The official 2026 Ministry PDF publishes both general and reduced light-vehicle
amounts. `import_ministry.py` extracts both tables from the locked PDF; the
discounted fare cannot be calculated from the rounded general charge.

For Via-T without known monthly history, the candidate reports an interval from
the published maximum-discount fare through the general initial charge. The
operator's policy includes later reimbursement of early journeys after meeting
the usage threshold; ownership of Via-T alone does not establish the monthly tier.
Sources:

- https://www.aucalsa.com/la-autopista/tarifas-y-descuentos/
- https://www.aucalsa.com/wp-content/uploads/Descuentos_Telepeaje_2024.pdf
- https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-21198
- The tariff PDF and its hash are recorded in `ap66-tariffs.json`.

La Magdalena's main collection plaza is not the logical León access: some side
access movements also pass the collection barrier. Campomanes cuts are south of
the bridge over N-630. The initially chosen bridge cut produced a false second
entry when a completed northbound trip continued below the bridge into town.
The unchanged full-trip response now verifies this does not recur. Old exclusion
requests are retained under `initial-bridge-cut`, separate from passing evidence.

Reproduce: `build_closed_plazas.py`, `fetch_od_routes.py ap66`,
`export_exclusion_polygons.cjs APP ap66`, `fetch_ap66_avoidance.py`, then
`export_app_fixtures.py APP`. Network calls are explicit, sequential and retained.
Twelve OD routes and four full/avoidance routes pass; the N-630 route is preserved
in both directions. All-lane/partial boundary review and national release remain
open. The candidate is schema 3 and `complete:false`.
