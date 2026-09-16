# Canary Islands inventory — 2026-09-16

The separate dated Geofabrik extract closes the geographic omission in the
peninsula/Balearic graph. Reproduce using `extract_spain_graph.py PBF --source URL
--out audit/2026-09-16/canary-islands-graph`; see `provenance.json` for the hash.

There are nine booth nodes, 42 toll-tagged or booth-connected ways, and no
motorway/trunk/link ways tagged `toll=yes` in this snapshot. This is not proof
that all access by car is free. `inventory.json` preserves relevant source tags;
`nearby-context.json` retains parking/tourism context for classification.

Review categories:

- 299769558: Los Ajaches/Papagayo vehicle access. Yaiza confirms EUR 3 for
  nonresidents, card payment. Hours in OSM are not independently verified.
  https://yaiza.es/playas/playas-punta-del-papagayo/
- 380643551 and 1514305765: Timanfaya visitor entry/exit. The operator sells
  visitor tickets, not a fixed motorway fare; OSM's per-person amount is stale.
  https://cactlanzarote.com/es/visita/montanas-del-fuego
- 317987018: San Antonio visitor centre, Fuencaliente. Nearby source way
  199211740 identifies the centre. Visitor pricing needs separate verification.
- 313503669 and 1484652559: Puerto Colón area; fee-paying parking context
  (ways 1022012472/1022012473), exact access classification still needs review.
- 1658380851 and 11559677442: Tenerife Norte parking access context with
  multiple mapped parking entrances; not a motorway collection plaza.
- 11560220394: Tenerife Sur airport parking/service access context; exact
  fee/access policy is not a fixed road toll.
- Barranco del Infierno toll-tagged paths are pedestrian visitor admission,
  not car-road toll segments.

National motorway inventory and visitor/parking fees must remain distinct. The
remaining scope/classification decisions are explicit blockers, not zero fares.
