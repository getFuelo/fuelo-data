# AP-53 general OD conversion

This is an incomplete development candidate, not a published country catalog.

## Evidence

- Ministry 2026 light-vehicle matrix: source URL, PDF hash and printed rows in
  `pricing-candidates/ap53-tariffs.json`; checked against https://acega.es/tarifas/.
- National OSM snapshot: `../../spain-graph/provenance.json`. Each mapped gate
  records its source way/version and booth or logical-boundary node in
  `provenance.json`. Geometry is © OpenStreetMap contributors, ODbL.
- Lalín Oeste/Centro/Este and Alto de Santo Domingo have identical published
  rates from every other zone. They share the southern tariff-zone identity.
  https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-7166 also specifies the Lalín
  journey equivalence. This is not a license to turn blank matrix cells into zero.

## Geometry and settlement

11 directed gates cover five economic zones: Santiago, Ribadulla, Bandeira,
Silleda and the Lalín terminal. Intermediate plazas share a finite cut with
opposite entry/exit roles. Terminal collection is one-way: entry uses a separate
logical cut on the actual opposite carriageway. Silleda also has a southbound
entry ramp which bypasses the ticket booth; it must still establish an origin.

Coverage is 174 source ways. Connectivity expansion includes internal OSM way
nodes as well as endpoints: a ramp can join the middle of a mapped way.
The original Silleda probes started after the directional split and could force
a detour. They are preserved under `initial-directed-ramp-probes`, not used as
correct OD-route fixtures. The current probes start before that split.

## Checks

All 20 directed inter-zone pairs have retained public Valhalla request/response
fixtures and match the general light-vehicle tariff in the app audit harness.
Two actual N-525 routes verify zero on the nearby free alternative. Truncating a
paid fixture after entry yields `missing_entry`, rather than an invented fare.
Runtime structural validation passes when the test-only copy is marked complete;
the actual incomplete candidate is rejected by production validation.

Reproduce with `build_ap53.py`, explicitly fetch with `fetch_ap53_routes.py` and
`fetch_ap53_free_routes.py`, then `export_app_fixtures.py APP_CHECKOUT`. Network
fetches skip existing results and never execute inside the app. Run the app's
`ap53Routes.test.ts` and the offline candidate validator.

## Still required before release

- Actual full access-to-access trips for the individual Lalín exits and Tras do
  Eixo, including entirely free movements within those terminal zones.
- Via-T return-trip and monthly recurrence eligibility. These are history-based;
  Via-T ownership alone must not imply a confirmed discounted or general quote.
- Exclusion/avoidance route verification, all lane approaches and boundary cases.
- Complete Spanish inventory and the remaining country-level release gates.

The passing corpus establishes these concrete general-tariff reference journeys,
not every possible journey on AP-53 or national completeness.
