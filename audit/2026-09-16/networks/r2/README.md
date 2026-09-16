# R-2 mapped development corpus

`r2.json` has six OD zones, twelve directed cuts and all thirty published pairs.
`r2-open.json` separately models the two urban open-system plazas. Their source
lanes and short real traversals are in the `r2-open` audit directory. General,
Via-T and 00–06 prices come from the locked official 2026 PDF:
https://cdn.transportes.gob.es/portal-web-seitt/media/document/tarifas_r2_2026.pdf

Guadalajara Norte–NII/Taracena is explicitly 100% rebated in both directions.
The logical Taracena cuts lie beyond the Guadalajara ramps so those trips close
correctly even though they bypass the trunk collection booth. Valhalla reports
tolls on these two routes; the verified published fare is nevertheless zero.

Alcalá's entry is source way 37520682 through booth 439206819, toward the R-2.
The adjacent eastbound way 329638924 is the exit. Initial close-lane probe points
were on the wrong side of the charging boundary and created an extra access loop;
replacement points lie on the public M-100 approaches. Old responses remain in
`initial-close-lane-probes`. The initial interpretation as merely a snap ambiguity
was incomplete: correctly assigning the entry/exit source ways is also necessary.

Whole journeys combine the OD candidate with both open networks. The Aeropuerto
approach crosses both urban plazas; Alcobendas-only crosses one. Expected totals
are inferred from actual source-mapped crossings and the published open-system
charges, not an operator calculator response. `full-journey-review.json` records
the corrected initial one-barrier assumption. M-50 geometry is covered because
Valhalla carries the preceding toll maneuver through the free shared section;
it has no additional charging gate. The Ministry's historical system description
confirms that shared M-50 section is free:
https://publicaciones.transportes.gob.es/downloadcustom/sample/1345

Reproduce: `build_closed_plazas.py`, `build_barrier_families.py`,
`fetch_od_routes.py r2`, `fetch_barrier_probes.py`, `fetch_r2_full_routes.py`,
`export_app_fixtures.py APP`. Requests are explicit, sequential and retained.

Remaining: all-lane/partial boundaries and avoidance that preserves the rebated
Guadalajara–Taracena link. Do not blindly fence all entry gates: that would also
block a free movement. Both candidates and the country remain disabled.

## Avoidance follow-up

The four shared plaza cross-sections at Ajalvir, Alcalá, Meco and Cabanillas
intercept every paid OD pair. Guadalajara Norte and Taracena are deliberately
excluded from the avoidance list: their mutual journey is fully rebated. This
uses the existing app polygon builder, not a new geometry approximation.

All thirty directed OD avoidance probes now quote zero. The two rebated routes
retain byte-identical polylines to their original baselines. Several alternatives
use this rebated movement even though Valhalla flags it tolled; the explicit
zero fare correctly distinguishes it from a missing toll flag.

Ajalvir's original near-plaza origin was already beyond the last free exit;
Valhalla correctly returned no path with its only onward barrier excluded. The
Meco and Cabanillas exit-ramp destinations likewise required approaching through
the plaza. Avoidance now uses public junction nodes 255960167 (M-113),
276998168 (M-116), and 280428859 (N-320), respectively. Original failures and
requests are retained in avoidance-probe-review. These replacements apply only
to the avoidance corpus, not the earlier priced OD reference routes.

Full public journeys combining the two urban plazas and closed-system avoidance,
and exhaustive boundary/lane review, remain pending.
