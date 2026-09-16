# AP41 reference corpus — 2026-09-16

Incomplete development candidate; not a country release.

56 directed journeys among eight published zones match general, Via-T and
00–06 rates. Six intermediate ramp plazas and two terminal pairs form 16 gates.
Carranque is a two-way approach: the public side is on way 903010659, rather
than the internal continuation 946522412. Original inside-plaza probes are
retained separately. All-lane/boundary/avoidance review remains open.

Rebuild the named builder, explicitly run `fetch_od_routes.py ap41`,
then `export_app_fixtures.py APP_CHECKOUT`. Source ways/versions and probe
locations are in `provenance.json`; official tariff URLs and hashes are in the
corresponding tariff reference. API fetching never runs inside the app.
