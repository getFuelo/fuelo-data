# AG-57 directional journey candidate

Disabled schema-3 candidate: 87 source ways, six published economic zones,
14 directed physical gates and 32 physical-gate fare pairs covering the 24
published directed journeys. The extra pairs represent the separate north/south
Ramallosa ramps, not extra charges. Collection points at Vincios and Baiona are
not independently added to the OD fare.

The retained 24 Valhalla request/response pairs pass through the real app matcher
and reproduce each published general tariff. Both Ramallosa south movements
use the south ramp gates; Gondomar remains a north-facing half interchange.
No missing Gondomar–southern-zone row was invented as a zero tariff.

Published tariffs: https://www.autoestradas.com/la-autopista/tarifas/
2026 system diagram: https://www.autoestradas.com/storage/pdf/tarifas/2026/Tarifas-20260101.pdf
2025 maintenance plans: https://www.autoestradas.com/wp-content/uploads/pdf/pliegos/2025/PPTP-Conservacion-y-mantenimiento-AG-55-AG-57.pdf
Via-T rules: https://www.xunta.gal/dog/Publicados/2025/20251231/AnuncioG0765-291225-0001_es.html

Via-T ranges preserve unknown return history and outward whole-cent bounds
where the legal percentage produces fractional cents. They are not published
exact settlement amounts. Large-family registration is not assumed.

Nigrán is represented by logical cuts on AG-57N west of the Gondomar and mainline
splits; it is not a guessed collection booth. Free Porto Molle/Praia América and
Sabarís/Baredo terminal journeys, full public approaches, avoidance, lane coverage
and country integration remain pending. These tests do not certify completeness.
