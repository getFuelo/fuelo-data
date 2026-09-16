# AP-636 development candidate

This remains disabled pending the national inventory and full boundary/access
corpus. It is not an enabled Spain release.

The 2026 Bidegi table publishes 42 cents for Beasain–Ormaiztegi, 82 cents for
Ormaiztegi–Zumarraga, and 155 cents for Legazpi/Urretxu–Bergara. The partial
Legazpi/Urretxu–Antzuola journey is 52 cents with TAG payment. Sources and hashes
are retained in `ap636-tariffs.json` and `provenance.json`.

Article 7 of Norma Foral 4/2020 assigns each charged section to its gantry and
requires TAG for the Antzuola partial journey. Section 10.2 of Bidegi's official
collection system specification describes the combined Deskarga/Antzuola-reader
condition. The partial amount replaces the full Deskarga amount. It is not a
fourth additive fee. Later annual rates supersede the historical document's
amounts. Registered Abiatu monthly rebates require separate eligibility/history;
they are not assumed merely from selecting Via-T.

## Geometry and accounting

- Beasain and Ezkio each have one directed cut per carriageway and one charge
  for the actual crossing. Both directions are checked with retained real routes.
- Deskarga is an OD subnetwork: Legazpi cuts lie at the charge gantry; Antzuola
  cuts lie on its separate entry/exit reader ramps; Bergara logical cuts lie
  beyond the Antzuola branch. The half interchange faces Deskarga. There are
  four legal direct OD fares, with no invented free Antzuola–Bergara fare.
- OD context coverage is restricted to the area between those cuts. Long source
  ways are clipped at actual source nodes. The two earlier independent sections
  must not require a Deskarga entry. Tunnel-interior truncated routes fail closed.
- Toll avoidance excludes Beasain, Ezkio and both Deskarga carriageways; it does
  not exclude Antzuola's discount readers. The app's actual polygon builder is
  used to produce the retained public requests.

## Corpus and reproduction

`build_ap636.py` builds 154 source coverage ways, 14 Deskarga context ways and ten
directed gates. `fetch_ap636_routes.py` retains twelve requests/responses:
four independent section traversals, four Deskarga OD routes, two full traversals
at 279 cents and two free alternatives. Initial hillside endpoints caused an
unrepresentative detour and are archived separately. The replacement Beasain
endpoint is vertex 226 on GI-2632 from the retained initial west route.

The free alternatives retain uncharged AP-636 movements around Ormaiztegi;
their zero quote is not a claim that the whole road is free. Provider durations
are not validated traffic estimates. Full public approach, alternate ramp and
repeat-crossing coverage remains open.

Run `build_ap636.py`, `export_exclusion_polygons.cjs APP ap636`,
`fetch_ap636_routes.py`, then `export_app_fixtures.py APP`. Network fetching is an
explicit offline audit action, never app runtime work. No paid routing APIs used.
