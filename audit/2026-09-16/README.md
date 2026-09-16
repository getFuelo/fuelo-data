# Auditoría de peajes — 16 de septiembre de 2026

**Revisadas las 36 entradas existentes (35 ES, 1 AD). No se puede certificar que el catálogo calcule correctamente cualquier ruta.** Se han corregido 12 referencias numéricas y varias descripciones. Fuentes: tarifas oficiales 2026; 33 documentos/páginas descargados, con huellas SHA-256. Se consultaron también los 36 puntos en OSM y las vías a las que pertenecen.

Todo queda en la rama local `feat/toll-catalog-audit`, sobre la corrección AUTEMA anterior. Sin push, CDN, instalación ni cambios en OSM. Estas modificaciones no afectan a la app instalada.

## Problemas confirmados

- **Elegibilidad:** 8 entradas SEITT usaban telepeaje por defecto; AP-66 y AP-15 también asumían bonificaciones. Ahora la referencia es general/efectivo-tarjeta. Los descuentos se conservan como condiciones, no se presuponen.
- **AP-51:** el máximo 2.95 correspondía a otro origen. Para conexión AP-6–Ávila es 2.90.
- **AP-8:** Bizkaia 5.93 es correcto hasta la muga; Gipuzkoa 11.52 comenzaba antes, en Ermua. Se alinea la referencia Gipuzkoa a la muga: 7.88 + 3.15 = 11.03. La suma de referencias pasa de 17.45 a 16.96; coincide con 13.81 Acceso Oeste–Donostia + 3.15 hasta Behobia. Esto es una comprobación del corredor de referencia, no una regla para sumar cualquier OD. [Tabla conjunta Arabat](https://www.arabat.eus/es/ap-1/tarifas-ap-1/).
- **Coordenadas:** R-3 coincide con nodo1062290642 de MP-203, abandonada/en construcción, acceso prohibido; M-12 con nodo364900137 **Parking T4 Entrada**, operador Aena; Artxanda con nodo3196925975 en vía de servicio de acceso a clientes. AP-636 coincide con una cabina de enlace, no con los tres pórticos cuyo importe se suma. No se han inventado coordenadas sustitutas.
- **Recorridos:** C-32 8.42 es Vallcarca, no todo Castelldefels–Vendrell (ambas troncales: 13.45). AG-55 2.05 es Arteixo–Carballo, no A Coruña–Carballo. R-2 5.20 es Ajalvir–Taracena, no Aeropuerto–Taracena. AP-1 7.56 parte de Bergara H/S e incluye Álava; no parte de Maltzaga.
- **Tiempo:** siguen pendientes las reglas de horas/temporadas y gratuidad nocturna. AP-71 cuesta 2.50 de noche y 6.20 de día; las SEITT son gratuitas 00–06. Conservar dos cifras no hace que la app elija automáticamente la adecuada. [Ministerio, tarifas 2026, pp. 1–2](https://cdn.transportes.gob.es/portal-web-transportes/recursos-web/transportes/media/press_release/251230-np-nacional-revision-tarifas-autopistas-estatales-y-seitt.pdf).

## Metadatos

Se corrigen las concesionarias de AP-6/AP-51/AP-61 (Castellana), AP-53 (ACEGA), AP-46 (Autopista del Guadalmedina) y la denominación de AUSOL, AVASA y Túnel d’Envalira. Fuentes corporativas adicionales en `entries.json`, campo `metadata_sources`. Envalira usa la referencia vial CG-2a de los caminos OSM de la plaza. Las referencias societarias restantes no constituyen una certificación registral de propiedad.

## Cobertura y efecto al publicar

`tolls-es.json` pasa a `complete: false`: enumerar carreteras no cubre todos sus accesos, barreras y trayectos. Falta desglosar, entre otras, AP-9, AP-15, M-12, AP-636 y varias AP-7/C-32. La AP-636 deja de estar marcada como tarifa fija por cruce. Se mantienen IDs y esquema 1; `ticket` señala una referencia dependiente del trayecto, también para sumas de barreras.

**Si se publicara este archivo, los clientes que respetan `complete` desactivarían los peajes de España.** No se ha publicado. Hay que resolver los bloqueos antes de volver a declarar cobertura completa. AD conserva cobertura de su único túnel y tarifa general 8.10; esta auditoría no sustituye las pruebas de rutas en ambos sentidos. Francia y Portugal no tienen catálogo aquí y no quedan cubiertos.

## Comprobación de cada entrada

Los importes siguientes son referencias bajo las condiciones descritas, **no presupuestos universales de viaje**. Cada fila enlaza su fuente; `entries.json` conserva cambios, alcance, condiciones y bloqueos por ID. Los errores anteriores no se reintroducen en las notas operativas.

| ID | Referencia EUR | Alcance y resultado |
|---|---:|---|
| [es-ap6](https://cdnfomento.blob.core.windows.net/portal-web-transportes/carreteras/nuestrared/autopistaspeaje/peajes-actuales/autopista-ap-6,-villalba---adanero-2026.pdf) | 15.70 | **Villalba–Adanero**. 15.70; Villalba–San Rafael 5.65 y Villalba–Villacastín 10.10. Una cabina no determina entrada y salida. |
| [es-ap51](https://cdnfomento.blob.core.windows.net/portal-web-transportes/carreteras/nuestrared/autopistaspeaje/peajes-actuales/autopista-ap-51,-conexion-ap-6---avila-2026.pdf) | 1.05 / 2.90 | **Conexión AP-6–Ávila**. 1.05 valle / 1.75 normal / 2.90 punta. 2.95 pertenece al acceso Villacastín, cuyo valle es 1.10. No mezclar filas. Valle 23–07; calendario punta en PDF. |
| [es-ap61](https://cdnfomento.blob.core.windows.net/portal-web-transportes/carreteras/nuestrared/autopistaspeaje/peajes-actuales/autopista-ap-61,-conexion-ap-6---segovia-2026.pdf) | 1.95 / 4.80 | **El Espinar (AP-6)–Segovia**. 1.95 valle / 2.95 normal / 4.80 punta. San Rafael–Segovia tiene otra fila: 2.00 / 3.05 / 4.95. Requiere hora y calendario. |
| [es-ap53](https://cdnfomento.blob.core.windows.net/portal-web-transportes/carreteras/nuestrared/autopistaspeaje/peajes-actuales/autopista-ap-53,-santiago---alto-de-santo-domingo-2026.pdf) | 7.25 | **Santiago–Alto de Santo Domingo**. 7.25 general. Santiago–Silleda 4.35. Bonificaciones por recurrencia requieren elegibilidad. |
| [es-ap66](https://cdnfomento.blob.core.windows.net/portal-web-transportes/carreteras/nuestrared/autopistaspeaje/peajes-actuales/autopista-ap-66,-campomanes---leon-2026.pdf) | 16.20 | **Campomanes–León**. 16.20 general. 13.75 requiere condiciones de pago electrónico/bonificación; no es la tarifa general. El número de pasos también modifica el descuento. |
| [es-ap68](https://cdnfomento.blob.core.windows.net/portal-web-transportes/carreteras/nuestrared/autopistaspeaje/peajes-actuales/autopista-ap-68,-bilbao---zaragoza-2026.pdf) | 39.90 | **Bilbao–Zaragoza**. 39.90 general para este OD. No equivale al coste de cualquier paso por el punto de Logroño. Revisar cambios concesionales en noviembre de 2026; no programar gratuidad total basándose en noticias. |
| [es-ap71](https://cdnfomento.blob.core.windows.net/portal-web-transportes/carreteras/nuestrared/autopistaspeaje/peajes-actuales/autopista-ap-71,-leon---astorga-2026.pdf) | 2.50 / 6.20 | **León–Astorga**. 2.50 de 23–07; 6.20 de 07–23. Ambos importes son correctos, pero usar siempre el bajo infravalora el viaje diurno. |
| [es-ap9](https://cdnfomento.blob.core.windows.net/portal-web-transportes/carreteras/nuestrared/autopistaspeaje/peajes-actuales/autopista-ap-9,-ferrol---frontera-portuguesa-2026.pdf) | 8.80 | **A Coruña–Santiago**. 8.80 corresponde a este OD, no Ferrol–Tui. La AP-9 tiene varios tramos tarifarios y tramos gratuitos; no existe aquí un precio único de todo el corredor. |
| [es-ap46](https://cdnfomento.blob.core.windows.net/portal-web-transportes/carreteras/nuestrared/autopistaspeaje/peajes-actuales/autopista-ap-46,-alto-de-las-pedrizas---malaga-2026.pdf) | 4.35 / 6.60 | **Barrera Casabermeja**. 4.35 temporada baja / 6.60 alta; gratuito 00–06. Alta mayo–octubre, fines de semana y periodo de Semana Santa del PDF. Hora y temporada pendientes de aplicación. |
| [es-ap7-malaga-estepona](https://cdnfomento.blob.core.windows.net/portal-web-transportes/carreteras/nuestrared/autopistaspeaje/peajes-actuales/autopista-ap-7,-malaga---estepona-2026.pdf) | 9.55 / 15.50 | **Calahonda + San Pedro de Alcántara troncales**. Suma 5.70 + 3.85 = 9.55 normal; 9.25 + 6.25 = 15.50 especial. Existen accesos laterales con otra tarifa. Deben identificarse las barreras realmente atravesadas. |
| [es-ap7-estepona-guadiaro](https://cdnfomento.blob.core.windows.net/portal-web-transportes/carreteras/nuestrared/autopistaspeaje/peajes-actuales/autopista-ap-7,-estepona---guadiaro-2026.pdf) | 2.45 / 4.05 | **Manilva troncal**. 2.45 normal / 4.05 especial. Acceso Manilva 1.20 / 2.00: falta como barrera diferenciada; la cabina del catálogo es un enlace, pendiente asignación troncal/lateral. |
| [es-ap7-alicante-cartagena](https://cdnfomento.blob.core.windows.net/portal-web-transportes/carreteras/nuestrared/autopistaspeaje/peajes-actuales/autopista-ap-7,-alicante---cartagena-2026.pdf) | 5.70 / 10.20 | **Los Montesinos + La Zenia troncales**. 2.85 + 2.85 = 5.70 baja; 5.10 + 5.10 = 10.20 alta. Es un sistema de barreras, también hay acceso La Zenia; no cobrar la suma por cualquier acceso. Diferente de la circunvalación gratuita de Alicante. |
| [es-r2](https://cdn.transportes.gob.es/portal-web-seitt/media/document/tarifas_r2_2026.pdf) | 5.20 | **Ajalvir–NII Taracena**. 4.60 telepeaje / 5.20 efectivo-tarjeta. La celda es Ajalvir, no Aeropuerto. Las filas independientes Aeropuerto y Alcobendas no quedan cubiertas por esta referencia. Gratuito 00–06; Guadalajara Norte–Taracena bonificado. |
| [es-r3](https://cdn.transportes.gob.es/portal-web-seitt/media/document/precios_web_r3_2026.pdf) | 3.40 | **M-40/M-602–conexión A-3**. 3.05 telepeaje / 3.40 efectivo-tarjeta. Gratuito 00–06. Coordenada actual sobre MP-203 en construcción, no validada para R-3. |
| [es-r4](https://cdn.transportes.gob.es/portal-web-seitt/media/document/tarifas_r4_2026_0.pdf) | 6.15 | **M-50–Ocaña/A-40**. 5.50 telepeaje / 6.15 efectivo-tarjeta. Gratuito 00–06. Matriz entrada/salida necesaria. |
| [es-r5](https://cdn.transportes.gob.es/portal-web-seitt/media/document/precios_web_r5_2026.pdf) | 3.65 | **M-40/M-45–conexión A-5**. 3.25 telepeaje / 3.65 efectivo-tarjeta. Gratuito 00–06. Matriz entrada/salida necesaria. |
| [es-m12](https://cdn.transportes.gob.es/portal-web-seitt/media/document/tarifa_m12_2026.pdf) | 1.55 | **Barajas + Alcobendas**. Suma de dos puntos: 0.90 + 0.50 = 1.40 telepeaje; 1.00 + 0.55 = 1.55 efectivo-tarjeta. Gratuito 00–06. Coordenada incorrecta: nodo364900137 es Parking T4 Entrada (Aena), no un peaje M-12. |
| [es-ap7-cartagena-vera](https://cdn.transportes.gob.es/portal-web-seitt/media/document/tarifas_ap7cv_2026.pdf) | 11.35 | **Vera–Cartagena**. 10.15 telepeaje / 11.35 efectivo-tarjeta. Gratuito 00–06. Matriz entrada/salida necesaria. |
| [es-ap36](https://cdn.transportes.gob.es/portal-web-seitt/media/document/tarifas_ap36_2026.pdf) | 13.85 | **Corral de Almaguer–San Clemente**. 12.35 telepeaje / 13.85 efectivo-tarjeta. Gratuito 00–06. Matriz entrada/salida necesaria. |
| [es-ap41](https://cdn.transportes.gob.es/portal-web-seitt/media/document/precios_web_ap41_2026.pdf) | 5.95 | **R-5–Toledo**. 5.30 telepeaje / 5.95 efectivo-tarjeta. Gratuito 00–06. Matriz entrada/salida necesaria. |
| [es-cadi](https://tunels.cat/es/tarifas-tuneles-del-cadi/) | 14.56 | **Túnel del Cadí, categoría 2**. 14.56 general. No aplicar bonificación de residentes sin acreditar elegibilidad. Nodo del catálogo pertenece a C-16. |
| [es-vallvidrera](https://tunels.cat/es/tuneles-de-vallvidrera/) | 4.70 / 5.28 | **Túnels de Vallvidrera, categoría 2**. 4.70 valle / 5.28 punta. Punta laborables 07:30–10:30 y 17–21. Nodo del catálogo pertenece a C-16; falta seleccionar tarifa por hora. |
| [es-c16-sant-cugat-terrassa](https://www.autema.com/es/tarifas-y-descuentos/tarifas/) | 3.19 | **Les Fonts, categoría II general**. 3.19 general; 1.43 es condicional. No suponer Via-T/Satelise ni registro. Debe comprobarse cruce de la plaza. |
| [es-c16-terrassa-manresa](https://www.autema.com/es/tarifas-y-descuentos/tarifas/) | 9.76 | **Manresa troncal, categoría II general**. 9.76 general. Calculador AUTEMA Berga/Lleida/Girona–C58, turismo II, tarjeta, sin descuentos: 9.76. No confundir con lateral C55 4.90. |
| [es-c32-castelldefels-vendrell](https://www.autopistas.com/wp-content/uploads/2025/12/26_001-Aucat-C32-Castelldefels-Vendrell-T26.pdf) | 8.42 | **Vallcarca troncal, categoría II**. 8.42 es solo Vallcarca; Cubelles troncal 5.03, acceso Cubelles 2.69, acceso Calafell 0.79. El recorrido completo por ambas troncales suma 13.45. El punto del catálogo pertenece a Peatge de Vallcarca; falta cobertura Cubelles y accesos. |
| [es-ag55](https://www.autoestradas.com/la-autopista/tarifas/) | 2.05 | **Arteixo–Carballo**. 2.05 es Arteixo–Carballo, no A Coruña–Carballo. A Coruña–Arteixo 0.55; Paiosaco–Carballo 1.35. No aplicar descuentos por familia, retorno u horario automáticamente. |
| [es-ag57](https://www.autoestradas.com/la-autopista/tarifas/) | 1.75 | **Vigo–Baiona**. 1.75 general. Vigo–Vincios 0.40, Vigo–Gondomar 0.90, Vigo–Nigrán 1.20. No aplicar beneficios personales automáticamente. |
| [es-ap15](https://www.audenasa.es/wp-content/uploads/Tarifas-2026-Recorrido.pdf) | 14.05 | **Sarasa + Oriz/Tiebas + Marcilla troncales**. 2.65 + 4.55 + 6.85 = 14.05 general. 9.23 no debe ser valor predeterminado: requiere bonificación. Marcilla acceso 3.45 es otro punto. Una coordenada en Marcilla no representa tres plazas. |
| [es-ap8-gipuzkoa](https://www.arabat.eus/es/ap-1/tarifas-ap-1/) | 11.03 | **Muga Bizkaia-Gipuzkoa–Behobia**. Referencia alineada con el final de Bizkaia: 7.88 hasta Zarautz barrera/Donostia + 3.15 Donostia–Behobia = 11.03. La antigua referencia Ermua–Behobia 11.52 se solapaba con Bizkaia. Para viajes reales usar matriz conjunta; los ODs no son arbitrariamente aditivos. |
| [es-ap1-gipuzkoa](https://www.arabat.eus/es/ap-1/tarifas-ap-1/) | 7.56 | **Bergara H/S–Etxabarri-Ibiña (Gipuzkoa y Álava)**. 7.56 corresponde a Bergara H/S, no al enlace AP-8 de Maltzaga. Maltzaga–Etxabarri-Ibiña es 9.73 en tabla Arabat. El recorrido incluye Álava; no afirmar que todo Álava es gratuito. |
| [es-ap636](https://www.bidegi.eus/documents/42696171/0/2026__AP-8_AP-1_AP-636_tarifak.pdf/0c9dbcf3-f3e7-e6f6-709b-8cbb7d9da9d5) | 2.79 | **Tres tramos completos Beasain–Bergara**. 0.42 + 0.82 + 1.55 = 2.79. No es tarifa fija de una cabina. Falta mapear pórticos y recorridos parciales; nodo2125622899 está en un enlace hacia AP-636/GI-627, no prueba cruce de los tres pórticos. |
| [es-ap8-bizkaia](https://www.arabat.eus/es/ap-1/tarifas-ap-1/) | 5.93 | **Acceso Oeste–Muga Bizkaia-Gipuzkoa**. 5.93 verificado en tabla conjunta de Arabat. 4.60 corresponde a Ermua, que es otro extremo. Conservar 5.93 y alinear referencia Gipuzkoa con la muga. Descuentos requieren elegibilidad. |
| [es-supersur](https://interbiak.bizkaia.eus/fitxategiak/Dokumentuak/Tarifas/Bidesariak%20VSM%2001-01-2026.pdf) | 2.05 | **Arrigorriaga–Santurtzi**. 2.05 general, confirmado en PDF 2026. Arrigorriaga–Ortuella 1.85; Arrigorriaga–Bilbao Sur 1.20. El PDF aplica tarifa día/noche; no asumir gratuidad nocturna antigua. |
| [es-artxanda](https://interbiak.bizkaia.eus/fitxategiak/Dokumentuak/Tarifas/Bidesariak%20TA%2001-01-2026.pdf) | 1.55 | **Cruce Túneles de Artxanda, ligero**. 1.55 general en tabla 2026, día y noche. El punto almacenado está sobre vía de servicio, no demuestra cruce del túnel/pórtico. Retirada nota de cierre temporal sin verificar estado actual. |
| [es-c16-sant-vicenc-c55](https://www.autema.com/es/tarificador/) | 4.90 | **Lateral Sant Vicenç–C55, categoría II general**. 4.90 general. Calculador AUTEMA Castellbell i el Vilar–C58, turismo II, tarjeta, sin descuentos: 4.90. Nodo2024620547/way515278833 contrastados con ruta de validación anterior. |
| [ad-envalira](https://tuneldenvalira.com/en/rates) | 8.10 | **Túnel d’Envalira, tipo 1**. 8.10 general turismo tipo 1 (hasta 2 m de altura, hasta 3.5 t). No aplicar descuentos de residentes. Punto sobre plaza CG-2a, ambas direcciones deben seguir comprobándose mediante rutas. |

## Qué falta para darlo por correcto en la app

1. Asociar cada plaza/pórtico a su carretera, sentidos y accesos. Sustituir las coordenadas incorrectas con evidencia de topología; no buscar simplemente la cabina más cercana. Una cabina en un enlace puede cobrar una tarifa lateral distinta o no ser atravesada por el recorrido principal.
2. Modelar matrices entrada/salida y barreras individuales; evitar sumas de referencias solapadas y cobros de un corredor completo por un acceso parcial.
3. Aplicar calendario, hora prevista de paso y perfil de pago/bonificación. Si falta información, mostrar incertidumbre o un rango justificable; nunca presentar una referencia como importe exacto.
4. Validar rutas completas/parciales en ambos sentidos, accesos y exclusiones; casos de noche/día y pago general. Publicar app/datos juntos con invalidación de caché solo después de estas pruebas.

## Evidencia y validación reproducible

- `source-fetch.json`: URL, fecha y SHA-256 de 33 documentos oficiales. PDFs/HTML descargados permanecen temporalmente en `/private/tmp/fuelo-toll-audit`; no se incluyen copias completas en Git. Las URLs pueden cambiar sus contenidos; la huella permite detectar ese cambio, no recuperar una versión histórica.
- `geometry-audit.json`: evidencia OSM de los 36 puntos y vías padre. Todos respondieron mediante consultas pequeñas de la API; las consultas generales Overpass fallaron/agotaron el tiempo. La evidencia comprueba identidad del nodo, no todas las vías y sentidos de cada plaza. © OpenStreetMap contributors, ODbL 1.0.
- `python3 scripts/validate_tolls.py`: comprueba cobertura del informe, referencias auditadas, monedas, fechas, fuentes, coordenadas y coherencia de `complete`/modelos. **Pasar este validador no certifica los precios de rutas** ni verifica de nuevo las webs.
- Revisión visual de las tablas complejas AP-51, R-2, C-32, AP-15, Bidegi/AP-1 y AP-8 Bizkaia; los demás valores se cotejaron en las tablas oficiales extraídas. No se han probado cambios de motor de precios ni rutas nuevas: no hay cambios de app en esta rama.

## Subsequent conversion evidence (same-day checkpoint)

The table above records the original scalar catalog audit, not the final runtime
price model. See `pricing-candidates/README.md` and `coverage-status.json` for the
new conversion evidence and release blockers. In particular M-12 through routes
cost EUR 1.00 general daytime: the Alcobendas ramp is not part of that journey.
Artxanda's real plazas have now been mapped; their old catalog coordinate remains
an audit finding rather than the coordinate used by the development candidate.
The production ES catalog has not been promoted. Vallcarca has a retained real
Valhalla geometry disagreement requiring resolution before activation.


### AP-8/AP-1 checkpoint — 2026-09-16

Bizkaia now has 20 published directed journeys, including the explicit zero
Iurreta–Abadiño row from Arabat (Bidegi's blank cell was not treated as zero).
Western Gipuzkoa adds 28 directed journeys. Itziar's N-634-D/service approaches
are explicitly covered; geometry tolerances were not widened. Ermua's initial
inside-plaza probes are retained separately from the corrected public access.

The schema-4 joint AP-8/AP-1 candidate settles all 260 published directed
non-self physical-zone journeys once, with separate road markers, including
Bergara Norte and Bizkaia–Gipuzkoa–AP-1 crossings. Published joint fares govern;
regional prices are not added. The unconstrained Ermua–Eibar local route costs
zero; the 122-cent motorway movement has its own through-point probe.

Eastern Gipuzkoa adds 12 directed general-price journeys. Oiartzun's west-facing
plaza and east-facing motorway ramps are distinct financial accesses. The
public GI-2132 approach is retained from the same PBF, alongside rejected
inside-plaza probes. Orio and Zarautz Este each charge once on both directions:
six source-lane probes and six real traversals. Oñaurre remains conditional-only
reference data, not an invented cash fare. Full east/west corridor integration,
all public/free approaches, rebates, selective avoidance and Supersur are open.

Validation: full app suite 1,785 tests / 55 suites passed, plus 14 new local-ramp
tests; TypeScript passes. All 73 candidate JSON files pass offline integrity.
Spain and all 35 manifest entries remain disabled. Local changes only.

## National integration and Supersur checkpoint

`python3 scripts/coverage/build_spain_candidate.py` assembles 57 financial
systems across the 35 existing road entries, without enabling release.
`node scripts/coverage/audit_spain_integration.cjs <app-checkout>` compares
1,459 retained route expectations against that combined candidate in both
catalog orders. 1,458 pass; Vallcarca remains an explicit failed reference
journey (see `networks/c32/valhalla-mismatch.json`). The audit exits nonzero;
it does not count the uncertain bypass as a verified free journey.

Supersur has 16 directed published general journeys, day/night checks and
three retained unconstrained alternatives. Guísamo's 16 internal highway probes
were replaced with real N-6 approaches; originals remain under each subsystem's
`initial-internal-guisamo/`. Native AP-9 Ferrol/norte and the six independently
published combined journeys pass together.

Coverage ownership is corrected at Zarautz Este, León (AP-66/AP-71) and R-5/AP-41.
The app additionally recognizes exact source vertices at junctions, and exact
source segments shared by financial subsystems of the same displayed road,
without increasing its 12 m matching tolerance or accepting truncated trips.
National integration now includes fixed corridors, public approaches, retained
free alternatives and selective-avoidance examples. It is still not exhaustive
national certification. Country completeness and all 35 readiness flags remain
false; the release validator must fail. No publication is authorized here.
