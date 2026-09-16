#!/usr/bin/env node
// Compare independently retained journey expectations against the assembled
// country. This deliberately calls the app's development audit, not production.
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '../..');
const app = path.resolve(process.argv[2] || path.join(root, '../toll-correctness'));
const ts = require(path.join(app, 'node_modules/typescript'));
require.extensions['.ts'] = (mod, file) => mod._compile(ts.transpileModule(fs.readFileSync(file, 'utf8'), {compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, esModuleInterop: true}}).outputText, file);
const {auditMappedRoute} = require(path.join(app, 'src/lib/routePricing.ts'));
const {decodePolyline6} = require(path.join(app, 'src/lib/polyline.ts'));
const {isValidTollFile} = require(path.join(app, 'src/lib/tollValidation.ts'));
const read = p => JSON.parse(fs.readFileSync(p));
const catalog = read(path.join(root, 'pricing-candidates/spain-integration.json'));
if (!isValidTollFile({...catalog, complete: true}, 'es') || isValidTollFile(catalog, 'es')) throw Error('Invalid integration schema/readiness guard');
const fixtures = path.join(app, 'src/lib/__tests__/fixtures');
const families = ['ap41','ap71','ap36','ap7-cartagena-vera','ap66','r2','ag55','ag57','r3','r5','r4','ap9-frontera','ap9-centro','ap9-sur','ap9-ferrol','ap9-norte','ap61','ap68','ap1-closed','ap8-bizkaia','ap8-gipuzkoa-west','ap8-gipuzkoa-east','supersur','ap53','ap636','ap9-combined','ap8-ap1-shared','iberpistas-ap61'];
const cases = families.flatMap(family => read(path.join(fixtures, family, 'cases.json')).map(c => ({...c, family, expected: c.expectedCents ?? c.expectedGeneralCents ?? c.sourceTariff?.baseCents})));
for (const group of read(path.join(fixtures, 'open-barrier-routes.json'))) {
 for (const row of group.routes) cases.push({family: group.family, name: row.network, response: row.route, expected: row.expectedHighCents});
}
for (const group of read(path.join(fixtures, 'ap8-local-ramps.json'))) {
 for (const row of group.routes) cases.push({...row, family: group.family, expected: row.expectedGeneralCents});
}
// Supplemental public approaches, whole corridors and retained avoidance paths.
for (const [family, file] of [['ap53','terminals'],['ag55','port'],['ag55','extra-lanes'],['r2','full'],['ap68','public-approaches']]) {
 for (const row of read(path.join(fixtures, family, file + '.json'))) cases.push({...row, family, name: file + '/' + row.name, expected: row.expectedCents});
}
for (const family of ['ap53','ap66','ap71','r2','vallvidrera']) {
 const file = family === 'vallvidrera' ? 'cases' : 'avoidance';
 for (const row of read(path.join(fixtures, family, file + '.json'))) {
  const free = row.name.endsWith('-excluded') || family === 'r2';
  const expected = free ? 0 : family === 'ap53' ? (row.name === 'south-baseline' ? 535 : 0) : ({ap66:1620,ap71:620,vallvidrera:470})[family];
  cases.push({...row, family, name: file + '/' + row.name, expected});
 }
}
for (const [family, rows] of Object.entries({
 ap46: {'north-to-south':660,'south-to-north':660,'north-to-south-free':0,'south-to-north-free':0},
 cadi: {'north-to-south':1456,'south-to-north':1456},
 artxanda: {inbound:155,outbound:155,'ugasko-north':155,'lasalve-south':155},
 'm12-v2': {'m12-route-34401539':100,'m12-route-156043989':100,'m12-route-34795820':55,'south-to-north':100,'north-to-south':100,'north-to-t4':0,'middle-to-north':0}
})) for (const [name, expected] of Object.entries(rows)) cases.push({family, name, expected, response:read(path.join(fixtures,family,name+'.json'))});
for (const [family, file] of [['ap61','free-n603'],['ap8-ap1-shared','free-local']]) cases.push({family,name:file,expected:0,response:read(path.join(fixtures,family,file+'.json'))});
// Isolated AP-61 connection probes start/end inside the combined toll system.
// Preserve them as partial-journey safety checks, not complete-journey prices.
for (const c of cases) if (c.family === 'ap61' && c.name.split('--').includes('AP6')) c.expectedUnavailable = c.name.startsWith('AP6--') ? 'missing_entry' : 'missing_exit';
for (const c of cases) if (c.family === 'c32' && c.name === 'es-c32-vallcarca') { c.expectedUnavailable = 'unverified_toll_passage'; c.externalBlocker = true; }
const catalogs = [catalog, {...catalog, pricing: [...catalog.pricing].reverse()}];
const report = {catalogOrdersChecked: 2, complete: false, total: cases.length, passed: 0, safelyUnavailable: 0, unresolvedPassages: [], failures: [], byFamily: {}};
for (const c of cases) {
 if (!Number.isInteger(c.expected)) throw Error(`Missing independent expectation: ${c.family}/${c.name}`);
 const {trip} = c.response, leg = trip.legs[0];
 const route = {geometry: decodePolyline6(leg.shape), durationMin: trip.summary.time / 60, distanceKm: trip.summary.length, hasTolls: trip.summary.has_toll, degraded: false, tollSegments: leg.maneuvers.filter(m => m.toll).map(m => ({beginIdx: m.begin_shape_index, endIdx: m.end_shape_index}))};
 const results = catalogs.map(file => auditMappedRoute(route, file, '2026-09-16T10:00:00Z'));
 const matches = result => c.expectedUnavailable ? result.quote.status === 'unavailable' && result.quote.reasons.includes(c.expectedUnavailable) : result.quote.status === 'quoted' && result.quote.minCents === c.expected && result.quote.maxCents === c.expected;
 const ok = results.every(matches);
 const result = results.find(result => !matches(result));
 const counts = report.byFamily[c.family] ??= {passed: 0, failed: 0};
 if (ok) {report.passed++; counts.passed++; if (c.expectedUnavailable) report.safelyUnavailable++; if (c.externalBlocker) report.unresolvedPassages.push({family:c.family,name:c.name,referenceCents:c.expected,reason:c.expectedUnavailable,source:'audit/2026-09-16/networks/c32/valhalla-mismatch.json'});} else {
  counts.failed++;
  report.failures.push({family: c.family, name: c.name, expectedCents: c.expected, order: results.indexOf(result) === 0 ? 'forward' : 'reverse', actual: result.quote, events: result.events.map(e => ({network: e.networkId, gate: e.gateId}))});
 }
}
const target = path.join(root, 'audit/2026-09-16/spain-integration-results.json');
fs.writeFileSync(target, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({total: report.total, passed: report.passed, failed: report.failures.length, safelyUnavailable: report.safelyUnavailable, unresolved: report.unresolvedPassages.length, byFamily: report.byFamily}, null, 2));
process.exitCode = report.failures.length || report.unresolvedPassages.length ? 1 : 0;
