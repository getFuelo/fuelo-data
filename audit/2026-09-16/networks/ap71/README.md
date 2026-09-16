# AP71 reference corpus — 2026-09-16

Incomplete development candidate; not a country release.

Twelve directed journeys among four published zones match day and night
fares. Full León–Astorga journeys cost 6.20 EUR both ways; app-generated entry
exclusions keep the N-120 alternative open at zero. Terminal entry cuts precede
exit splits, and logical exit cuts follow ramp merges. Adjacent-access trips pay
at ramp plazas and do not necessarily cross the mainline collection booth.
The provider extends toll maneuvers over free N-6 approach geometry; these ways
are retained with explicit free coverage evidence. Via-T without monthly trip rank uses a 50..100% interval of the applicable
day/night fare, supported by https://www.autopistas.com/descuento/cliente-frecuente-4/.
General reference payment excludes monthly rebates; physical-card rebates need
a separate explicit profile. All-lane/boundary review remains open.

Rebuild the named builder, explicitly run `fetch_od_routes.py ap71`,
then `export_app_fixtures.py APP_CHECKOUT`. Source ways/versions and probe
locations are in `provenance.json`; official tariff URLs and hashes are in the
corresponding tariff reference. API fetching never runs inside the app.
