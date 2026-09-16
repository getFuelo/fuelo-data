# Envalira schema-2 reference corpus

Local dataset candidate, checked 2026-09-16; not published to the CDN.
General light-vehicle fare: 8.10 EUR, valid in the candidate through 2026-12-31.
Tariff source: https://tuneldenvalira.com/en/rates

`geometry-provenance.json` records the OSM API boxes, lane booths and the
finite cross-section derivation. The catalog retains 40 complete CG-2a way
geometries and their OSM versions. Attribution: © OpenStreetMap contributors,
ODbL 1.0. This is a derived geometry snapshot, not live map validation.

Real responses from https://valhalla1.openstreetmap.de/route:

| Fixture | Planned route | Expected fare |
| --- | --- | --- |
| envalira-east | 3.651 km, tunnel | 8.10 EUR |
| envalira-west | 3.698 km, tunnel | 8.10 EUR |
| envalira-free | 12.046 km, mountain pass | 0 EUR |
| envalira-excluded | 12.046 km, exact polygon exclusion | 0 EUR |

The last request is retained in `envalira-excluded-request.json`. It uses the
same six-metre padding around the verified cross-section as the app's polygon
builder, with normal toll costing. Valhalla still flags part of the approach
as tolled; actual charge-gate crossings, not that flag alone, establish the fare.

The app branch tests these responses against the schema-2 catalog. These cases
validate both directions and the nearby free alternative. They do not establish
live traffic accuracy or replace device testing. No resident/subscription rate
is assumed. Spain remains incomplete.
