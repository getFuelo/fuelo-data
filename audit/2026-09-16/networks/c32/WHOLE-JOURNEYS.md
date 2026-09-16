# Sitges–Castelldefels full journeys

Device testing exposed `toll_geometry_outside_catalog` in both directions:
the maneuver's toll flag included approaches outside the old coverage. The
Sitges ramp is a linked motorway access; the reverse journey begins on C-32LE
(ways 863608205 and 1393309353). These source ways exist in the retained national
graph. Include C-32LE and bounded connected motorway links, as already done for
Vallvidrera. No gate, tariff or matching radius changes.

`whole-journeys.json` retains two public-city Valhalla responses, expected EUR
8.42 each using the existing Vallcarca plaza tariff. They are exported to app
fixtures and included in both-order national integration (1493/1493 passed).
The coastal alternative was exercised on the Pixel: EUR 0, with a different
geometry, distance and duration. Device acceptance is recorded in the app's
`docs/qa/2026-09-16-device-usability.md`.
