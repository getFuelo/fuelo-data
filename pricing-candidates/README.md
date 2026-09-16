# Incomplete pricing candidates

These files are development evidence, not served country catalogs. Do not set
Spain complete or copy partial candidates to the production endpoint.

- `m12.json`: three physical gates, geometry provenance and real short Valhalla
  routes. Barajas has different northbound/southbound plazas. General daytime
  fares are 1.00/0.55 EUR; explicitly selected Via-T 0.90/0.50 EUR; 00–06 free.
  Full-road coverage and all approaches remain pending.
- `ap51-tariffs.json`: official light-vehicle general tariff references, seasonal
  calendar and direct/reverse OD rows. AP-6 joint fares are complete journey
  references and must not be added to separate AP-6 charges. Entry/exit geometry
  remains pending; the main plaza alone cannot determine the applicable row.

Source URLs, validity and evidence are recorded alongside each candidate.
App tests distinguish tariff-rule checks from actual reference-route checks.
Neither establishes country completeness. Frequent-user/resident discounts
remain unavailable unless their additional requirements are explicitly modeled.
