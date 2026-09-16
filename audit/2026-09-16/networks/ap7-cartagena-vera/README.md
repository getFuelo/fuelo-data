# AP7-CARTAGENA-VERA reference corpus — 2026-09-16

Incomplete development candidate. All 72 directed published OD pairs have
retained real route responses matching general, Via-T and 00–06 fares.
Source associations and probe locations are in `provenance.json`; tariff URLs,
PDF hashes and amounts are in `pricing-candidates/ap7-cartagena-vera-tariffs.json`.
Initial probes with endpoints inside Mota del Cuervo or Pulpí are retained
separately and are not part of the passing reference corpus.

Rebuild with `build_closed_plazas.py`, fetch explicitly with
`fetch_od_routes.py ap7-cartagena-vera`, and export with
`export_app_fixtures.py APP_CHECKOUT`. Network requests never run in the app.
All-lane, arbitrary partial/free boundaries and avoidance remain to be verified.
These reference cases do not establish complete Spanish coverage.
