# R3 directed journey candidate

Disabled candidate: 278 source ways, 18 directed physical gates and
64 physical-gate fare pairs. The retained 26 published priced journeys
pass the app's actual geometry matcher, event sequence, general price, Via-T
price and midnight–06:00 zero-price checks. These are synthetic routing requests
to the public Valhalla service, not receipts or exhaustive public approach tests.

Tariff source: https://cdn.transportes.gob.es/portal-web-seitt/media/document/precios_web_r3_2026.pdf
The parser retains the published rows; normalized gate identifiers are mapped
explicitly in build_closed_plazas.py. An omitted fare is not interpreted as zero.

Logical terminal cuts are distinct from collection booths, so a through journey
does not pay twice merely because it crosses multiple booths. All initial
request/response probes are retained; corrections are documented below.

Remaining work: public approaches and all lanes, unsupported free/partial cases,
repeated journeys, avoidance and adjacent-network/country integration. Country
coverage remains incomplete; the app must not consume this candidate as a
complete national catalog.

M-50–M-208 has two additional verified free directions (28 reference routes in
all). The 2026 table uses dashes, corroborated explicitly by the municipal road
noise account: https://ayto-velilla.es/la-direccion-general-de-carreteras-incluira-la-m-208-en-su-tramo-proximo-a-la-calle-frascuelo-en-los-planes-de-accion-contra-el-ruido/
M-300–A-3 is unlisted and remains unknown, not free by inference.

The first M-50/M-208 cuts intersected nearby through carriageways. The corrected
cuts use separated ramp geometry and preserve the full mainline routes as
regressions. The M-300 exit has a nonstandard OSM ref "Salida M 300", now included
explicitly. Two M-50 destinations were moved beyond the corrected exit cut;
the originals and pre-correction catalog are in initial-close-ramp-cuts.
