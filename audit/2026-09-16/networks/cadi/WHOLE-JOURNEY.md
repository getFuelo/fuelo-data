# Cadí: full Andorra–Barcelona regression

The device showed both Cadí and AUTEMA as unknown, despite their short plaza
fixtures passing. A public-city request reproduced `toll_geometry_outside_catalog`.
Valhalla's maneuver `toll` means **any portion**, not every edge; the 54 km
maneuver included the free C-16 north of Manresa. The C-55 alternative also
included free conventional-road geometry omitted from the major-road graph.

The correction retains versioned source ways from the same dated Spain PBF:
non-tolled C-16 north of AUTEMA and C-55, within the bounds in the builder.
No radius is widened, no route shape is used as coverage, and no tariff/gate
is changed. Source hash and all way versions/tags are in `free-corridor.json`.
Existing plaza crossings continue to determine each fee. Country completeness
remains false; the APK uses the explicitly labelled local preview only.

Reproduce after rebuilding the ordinary Cadí candidate:

```sh
python scripts/coverage/build_fixed_networks.py DOWNLOAD_DIRECTORY
python scripts/coverage/build_cadi_corridor.py /path/to/spain-260915.osm.pbf
python scripts/coverage/build_spain_candidate.py
python scripts/coverage/export_app_fixtures.py /path/to/app
node scripts/coverage/audit_spain_integration.cjs /path/to/app
```

`build_cadi_corridor.py` requires pyosmium. Retained public-city journeys in
`andorra-barcelona.json` expect Cadí 1456 + Manresa 976 = 2432 cents;
Cadí 1456 + Sant Vicenç 490 = 1946 cents; and the free alternative = 0.
The app regression exercises `scanRouteTolls`, including country selection,
individual Cadí pricing, legacy short-coverage failure and completeness guards.
National integration: 1491/1491 cases, both network orders, eight expected
partial-journey unavailable outcomes. TypeScript and 13 targeted tests pass.

Provider semantics: https://valhalla.github.io/valhalla/api/turn-by-turn/api-reference/
Public-road context: https://web.manresa.cat/web/menu/6629-comment-se-rendre-a-manresa

Device verification: installed the bundled local release on Pixel 11 Pro with
retained data. Existing GPS origin → Barcelona rendered Cadí EUR 14.56 and total
EUR 24.32 (198 km); selecting the second route rendered EUR 14.56 + EUR 4.90 =
EUR 19.46 (206 km). Both screens had no unknown-price badge. Targeted test total
including preview isolation: 15 passed.
