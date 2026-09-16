# R4 directed journey candidate

Disabled candidate: 190 source ways, 18 directed physical gates and
46 physical-gate fare pairs. The retained 34 published priced journeys
pass the app's actual geometry matcher, event sequence, general price, Via-T
price and midnight–06:00 zero-price checks. These are synthetic routing requests
to the public Valhalla service, not receipts or exhaustive public approach tests.

Tariff source: https://cdn.transportes.gob.es/portal-web-seitt/media/document/tarifas_r4_2026_0.pdf
The parser retains the published rows; normalized gate identifiers are mapped
explicitly in build_closed_plazas.py. An omitted fare is not interpreted as zero.

Logical terminal cuts are distinct from collection booths, so a through journey
does not pay twice merely because it crosses multiple booths. All initial
request/response probes are retained; corrections are documented below.

Remaining work: public approaches and all lanes, unsupported free/partial cases,
repeated journeys, avoidance and adjacent-network/country integration. Country
coverage remains incomplete; the app must not consume this candidate as a
complete national catalog.

Seseña and Villaseca face the northern system; Ontígola faces Ocaña. These partial
interchanges are not expanded into a complete eight-by-eight matrix. Valdemoro
has distinct ramp gates per direction, while Villaseca/Ontígola use opposite
crossing directions on their shared bidirectional approach. Pinto's logical cuts
lie before its many collection lanes and do not cross the mainline plaza.
