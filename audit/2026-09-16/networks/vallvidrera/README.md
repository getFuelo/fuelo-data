# Vallvidrera development candidate

One physical plaza, four source lane traversals and six real Valhalla routes:
two plaza directions, two Sarrià–Sant Cugat journeys and their excluded versions.
The latter use the actual app's finite gate exclusion polygon and preserve the
free alternative in both directions. Coverage includes the tunnel approaches
and connected C-16 ramps; no matching-radius expansion is used.

The official 2026 category-II prices are 470 cents valley and 528 cents peak.
Peak windows are weekday 07:30–10:30 and 17:00–21:00 in Europe/Madrid, excluding
holidays. The applicable holiday calendar is unresolved: schema 3 preserves
470..528 during those windows, and exact 470 outside them and at weekends.
Trips spanning a tariff transition retain their time uncertainty too.

No frequency/ECO/VAO discount is assumed from generic Via-T ownership. These
have separate enrollment, vehicle, occupancy and usage requirements.

Source: https://tunels.cat/es/tuneles-de-vallvidrera/
PDF: https://tunels.cat/wp-content/uploads/2025/12/Tunels_tarifes_2026.pdf
Earlier calendar investigation is retained in `calendar-investigation.json`.

Reproduce with `build_barrier_families.py`,
`export_exclusion_polygons.cjs APP vallvidrera`, `fetch_vallvidrera_routes.py`,
and `export_app_fixtures.py APP`. Partial access review and national integration
remain open. The candidate stays `complete:false`.
