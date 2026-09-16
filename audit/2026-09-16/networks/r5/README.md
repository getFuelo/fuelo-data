# R5 directed journey candidate

Disabled candidate: 427 source ways, 16 directed physical gates and
42 physical-gate fare pairs. The retained 26 published priced journeys
pass the app's actual geometry matcher, event sequence, general price, Via-T
price and midnight–06:00 zero-price checks. These are synthetic routing requests
to the public Valhalla service, not receipts or exhaustive public approach tests.

Tariff source: https://cdn.transportes.gob.es/portal-web-seitt/media/document/precios_web_r5_2026.pdf
The parser retains the published rows; normalized gate identifiers are mapped
explicitly in build_closed_plazas.py. An omitted fare is not interpreted as zero.

Logical terminal cuts are distinct from collection booths, so a through journey
does not pay twice merely because it crosses multiple booths. All initial
request/response probes are retained; corrections are documented below.

Remaining work: public approaches and all lanes, unsupported free/partial cases,
repeated journeys, avoidance and adjacent-network/country integration. Country
coverage remains incomplete; the app must not consume this candidate as a
complete national catalog.

Both M-50 exit cuts initially intersected the nearby through carriageway. The
south exit now uses the final source vertex before the M-50/M-506 fork; the north
exit lies farther along its separate ramp. Four destination probes were moved
beyond these cuts; initial-close-ramp-cuts retains the originals and catalog.
M-50/AP-41 and M-404/A-5 unlisted movements still require explicit free-scope
review. AP-41 connection ramps do not add an AP-41 journey charge here.
