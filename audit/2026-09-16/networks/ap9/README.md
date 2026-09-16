# AP-9 directed journey mapping — 2026-09-16

Disabled development candidates: five independent pricing systems, 84 retained
single-system journeys (82 priced, two exempt) and six published cross-system
Coruña totals. Full journeys match four gate events and are invariant under
network order. Via-T with unknown history remains 0..general, including at night;
no automatic Puxeiros–Tui 50% discount is assumed without the qualifying return.

Sources: Ministry AP-9 2026 tariff rows, Audasa's 2026 diagram/table and current
light-vehicle discount conditions. The operator table explicitly exempts
Morrazo–Vigo/Puxeiros and A Coruña–A Barcala. Only the former free pair is mapped
and tested here. The original 46-row tariff reference is preserved unchanged.

The SIGÜEIRO–SIGÜEIRO (25 cents) and SANTIAGO–SANTIAGO (455 cents) rows remain
unmapped: their exact access context must be established, not treated as zero.
Local Guísamo/Santa Marta accesses, the full free A Coruña/Barcala approaches,
Pontevedra and Santiago free urban sections, Vigo/Puxeiros approaches, all lanes,
repeated trips and avoidance remain release blockers. Mainline terminal probes
are not exhaustive tests from every public road. The five subsystem candidates
and their combined file all remain complete:false.

Norte's initial Sigüeiro entry cut crossed the adjacent exit ramp. Moving it to
the source entry booth fixed the false event without widening tolerances. The
original failing catalog and route are retained in ap9-norte/initial-close-ramp-cut.
The AP-9 M spelling and the eastern AP-9F extent were also added to coverage.

Guísamo is the logical interface between Ferrol and Norte. The six separately
published cross-system totals verify the decomposition: Fene–Coruña 615 cents,
Cabanas–Coruña 465 and Miño–Coruña 350, each in both directions. This does not
establish a fare for an unlisted arbitrary combined journey.
