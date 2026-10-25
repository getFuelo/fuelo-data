#!/usr/bin/env node
// Terminal and continuation sweep: real router journeys generated from the
// catalog itself, replayed through the app's production matcher.
//
// Retained cases (national replay) end at the mapped cuts. Real journeys carry
// on past them, and OSM can tag a motorway toll=yes beyond its last plaza or
// across the join between two sections. The router then reports tolled
// geometry outside the catalog and the app (correctly) fails closed. This sweep
// finds those spans before users do.
//
//   node scripts/coverage/sweep_terminals.cjs generate        # journeys.json from the catalog
//   node scripts/coverage/sweep_terminals.cjs fetch           # cache missing router responses
//   node scripts/coverage/sweep_terminals.cjs check [app]     # replay, report, exit 1 on anything new
//   node scripts/coverage/sweep_terminals.cjs accept [app]    # record reviewed prices as the baseline
//
// accepted.json holds the reviewed baseline: each priced journey's cents and
// each unavailable journey's status with the reason it must stay unavailable.
// `check` fails on a new gap, a newly unavailable journey, a changed price or a
// priced journey that drives through a main-line plaza without crossing it.
// After a reviewed change (e.g. January tariffs), run `accept`: it keeps the
// existing reasons and refuses while any unavailable journey has none.
//
// Journeys per road (coverage of all networks sharing a tollId): through both
// ways between points 12 km beyond each end of the road's main axis, and from a
// point 5 km beside the road's middle to beyond each end and back. Plus seeds.json (named real trips). Responses
// are cached in pricing-candidates/terminal-sweep/responses (trimmed to what the
// app reads), so `check` is offline and reproducible.
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '../..');
const dir = path.join(root, 'pricing-candidates/terminal-sweep');
const read = p => JSON.parse(fs.readFileSync(p));
const write = (p, v) => { fs.mkdirSync(path.dirname(p), {recursive: true}); fs.writeFileSync(p, JSON.stringify(v, null, 1) + '\n'); };
const ROUTER = process.env.FUELO_ROUTER || 'https://routing.fuelo.agilitza.com/route';
const BEYOND_KM = 12, SIDE_KM = 5, NEAR_GATE_KM = .04, TOLERANCE_KM = .012, DEPARTURE = '2026-10-25T10:00:00Z';
const [mode = 'check', appArg] = process.argv.slice(2);

const R = 6371;
const toXY = (p, lat0) => [p.lng * Math.PI / 180 * R * Math.cos(lat0 * Math.PI / 180), p.lat * Math.PI / 180 * R];
const fromXY = ([x, y], lat0) => ({lat: +(y / R * 180 / Math.PI).toFixed(6), lng: +(x / (R * Math.cos(lat0 * Math.PI / 180)) * 180 / Math.PI).toFixed(6)});

function roads(catalog) {
 const byToll = new Map();
 for (const n of catalog.pricing) {
  const road = byToll.get(n.tollId) ?? {tollId: n.tollId, networks: new Set(), ways: new Map()};
  road.networks.add(n.id);
  for (const w of n.coverageWays) road.ways.set(w.id, w.line);
  byToll.set(n.tollId, road);
 }
 return [...byToll.values()];
}

function generate() {
 const catalog = read(path.join(root, 'tolls-es-reviewed.json'));
 const journeys = [];
 for (const road of roads(catalog)) {
  const pts = [...road.ways.values()].flat();
  const lat0 = pts.reduce((s, p) => s + p.lat, 0) / pts.length;
  const xy = pts.map(p => toXY(p, lat0));
  const mx = xy.reduce((s, p) => s + p[0], 0) / xy.length, my = xy.reduce((s, p) => s + p[1], 0) / xy.length;
  let sxx = 0, syy = 0, sxy = 0;
  for (const [x, y] of xy) { sxx += (x - mx) ** 2; syy += (y - my) ** 2; sxy += (x - mx) * (y - my); }
  const angle = Math.atan2(2 * sxy, sxx - syy) / 2, ax = [Math.cos(angle), Math.sin(angle)];
  const proj = xy.map(([x, y]) => (x - mx) * ax[0] + (y - my) * ax[1]);
  const iA = proj.indexOf(Math.min(...proj)), iB = proj.indexOf(Math.max(...proj));
  // A real trip joins through an access: start 5 km to the side of the
  // road's middle, never on the carriageway between two plazas.
  const iM = proj.map((v, i) => [Math.abs(v), i]).sort((a, b) => a[0] - b[0])[0][1];
  const mid = fromXY([xy[iM][0] - SIDE_KM * ax[1], xy[iM][1] + SIDE_KM * ax[0]], lat0);
  const beyond = (i, sign) => fromXY([xy[i][0] + sign * BEYOND_KM * ax[0], xy[i][1] + sign * BEYOND_KM * ax[1]], lat0);
  const A = beyond(iA, -1), B = beyond(iB, 1), id = road.tollId;
  journeys.push(
   {name: `${id}--through-ab`, road: id, from: A, to: B}, {name: `${id}--through-ba`, road: id, from: B, to: A},
   {name: `${id}--mid-a`, road: id, from: mid, to: A}, {name: `${id}--a-mid`, road: id, from: A, to: mid},
   {name: `${id}--mid-b`, road: id, from: mid, to: B}, {name: `${id}--b-mid`, road: id, from: B, to: mid});
 }
 const seeds = path.join(dir, 'seeds.json');
 if (fs.existsSync(seeds)) for (const s of read(seeds)) journeys.push({...s, road: s.road ?? 'seed'});
 write(path.join(dir, 'journeys.json'), journeys);
 console.log(journeys.length, 'journeys over', roads(catalog).length, 'roads');
}

async function fetchAll() {
 const journeys = read(path.join(dir, 'journeys.json'));
 let fetched = 0, failed = 0;
 for (const j of journeys) {
  const file = path.join(dir, 'responses', j.name + '.json');
  if (fs.existsSync(file)) continue;
  const body = {locations: [j.from, j.to].map(p => ({lat: p.lat, lon: p.lng})), costing: 'auto', costing_options: {auto: {use_tolls: 1}}, directions_options: {units: 'kilometers'}};
  const res = await fetch(ROUTER, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
  const json = await res.json().catch(() => ({error: `HTTP ${res.status}`}));
  if (!res.ok || !json.trip) { failed++; write(file, {error: json.error ?? `HTTP ${res.status}`, request: body}); }
  else { fetched++; write(file, {request: body, trip: {summary: {length: json.trip.summary.length, time: json.trip.summary.time, has_toll: json.trip.summary.has_toll}, legs: json.trip.legs.map(l => ({shape: l.shape, toll_segments: l.toll_segments}))}}); }
  await new Promise(r => setTimeout(r, 400)); // polite: our own server, shared with users
 }
 console.log({fetched, failed, cached: journeys.length - fetched - failed});
}

function check(appDir) {
 const app = path.resolve(appDir || process.env.FUELO_APP || path.join(root, '../app'));
 const ts = require(path.join(app, 'node_modules/typescript'));
 require.extensions['.ts'] = (mod, file) => mod._compile(ts.transpileModule(fs.readFileSync(file, 'utf8'), {compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, esModuleInterop: true}}).outputText, file);
 const {scanRouteTolls} = require(path.join(app, 'src/lib/tollMatching.ts'));
 const {findGateCrossings} = require(path.join(app, 'src/lib/tollPricing.ts'));
 const {decodePolyline6} = require(path.join(app, 'src/lib/polyline.ts'));
 // FUELO_CATALOG compares another catalog (e.g. the published one) on the same journeys.
 const files = {es: read(process.env.FUELO_CATALOG || path.join(root, 'tolls-es-reviewed.json')), ad: read(path.join(root, 'tolls-ad.json'))};
 // Segment grid over every covered way, for reporting uncovered runs only
 // (pricing itself is the app's decision above).
 const cell = .02, grid = new Map();
 for (const n of files.es.pricing) for (const w of n.coverageWays) for (let i = 1; i < w.line.length; i++) {
  const a = w.line[i - 1], b = w.line[i];
  for (let la = Math.floor(Math.min(a.lat, b.lat) / cell); la <= Math.floor(Math.max(a.lat, b.lat) / cell); la++)
   for (let ln = Math.floor(Math.min(a.lng, b.lng) / cell); ln <= Math.floor(Math.max(a.lng, b.lng) / cell); ln++) {
    const k = la + ',' + ln; if (!grid.has(k)) grid.set(k, []); grid.get(k).push([a, b]);
   }
 }
 const near = p => {
  const segs = grid.get(Math.floor(p.lat / cell) + ',' + Math.floor(p.lng / cell)) || [];
  return segs.some(([a, b]) => {
   const k = Math.cos(p.lat * Math.PI / 180) * 111.32, ax = (a.lng - p.lng) * k, ay = (a.lat - p.lat) * 110.57, bx = (b.lng - p.lng) * k, by = (b.lat - p.lat) * 110.57;
   const dx = bx - ax, dy = by - ay, t = dx || dy ? Math.max(0, Math.min(1, -(ax * dx + ay * dy) / (dx * dx + dy * dy))) : 0;
   return Math.hypot(ax + t * dx, ay + t * dy) <= TOLERANCE_KM;
  });
 };
 const journeys = read(path.join(dir, 'journeys.json'));
 const accepted = fs.existsSync(path.join(dir, 'accepted.json')) ? read(path.join(dir, 'accepted.json')) : {};
 const results = [], byStatus = {}, gaps = [], regressions = [], nearMisses = [];
 for (const j of journeys) {
  const file = path.join(dir, 'responses', j.name + '.json');
  if (!fs.existsSync(file)) { results.push({name: j.name, road: j.road, status: 'not_fetched'}); continue; }
  const rec = read(file);
  if (!rec.trip) { results.push({name: j.name, road: j.road, status: 'no_route'}); byStatus.no_route = (byStatus.no_route ?? 0) + 1; continue; }
  const geometry = [], tollSegments = [];
  for (const leg of rec.trip.legs) {
   const off = geometry.length; geometry.push(...decodePolyline6(leg.shape));
   for (const s of leg.toll_segments ?? []) tollSegments.push({beginIdx: off + s.begin_shape_index, endIdx: off + s.end_shape_index});
  }
  const route = {distanceKm: rec.trip.summary.length, durationMin: rec.trip.summary.time / 60, geometry, tollSegments, hasTolls: rec.trip.summary.has_toll, degraded: false};
  const r = scanRouteTolls(route, files, DEPARTURE);
  const q = r.quote;
  const status = !tollSegments.length ? 'no_tolls' : q?.status === 'quoted' ? 'quoted' : `unavailable:${(q?.reasons ?? ['no_quote']).join('+')}`;
  byStatus[status] = (byStatus[status] ?? 0) + 1;
  const row = {name: j.name, road: j.road, status, cents: q?.status === 'quoted' ? [q.minCents, q.maxCents] : undefined, km: Math.round(rec.trip.summary.length)};
  if (status.includes('toll_geometry_outside_catalog')) {
   row.uncovered = [];
   for (const s of tollSegments) {
    let run = null;
    for (let i = s.beginIdx; i <= s.endIdx; i++) {
     const p = geometry[i], out = !near(p);
     if (out && !run) run = {from: p, to: p, points: 0, begin: i, end: i};
     if (out) { run.to = p; run.end = i; run.points++; }
     if ((!out || i === s.endIdx) && run) { row.uncovered.push({from: run.from, to: run.to, points: run.points, begin: run.begin, end: run.end}); run = null; }
    }
   }
   for (const u of row.uncovered) gaps.push({journey: j.name, ...u});
  }
  // A route that drives through a main-line plaza without crossing its gate
  // line is priced as if the plaza were not there (a short line that misses
  // the outer booth lanes). Flag any such plaza passed within NEAR_GATE_KM.
  if (tollSegments.length) {
   // A plaza's entry and exit lines sit on opposite carriageways, so crossing
   // one always passes near the other: judge plazas (zones), not lines.
   const zone = id => id.replace(/-(entry|exit)$/, '');
   const crossed = new Set(findGateCrossings(geometry, files.es.pricing).map(e => e.networkId + '/' + zone(e.gateId)));
   for (const n of files.es.pricing) for (const g of n.gates) {
    // Only main-carriageway plazas: a slip-road gate runs alongside the
    // carriageway, so passing it uncrossed is normal.
    const mainline = n.pricing.kind === 'gates' || /troncal/i.test(g.id);
    if (!mainline || !g.line || crossed.has(n.id + '/' + zone(g.id))) continue;
    const c = {lat: (g.line[0].lat + g.line[1].lat) / 2, lng: (g.line[0].lng + g.line[1].lng) / 2};
    const k = Math.cos(c.lat * Math.PI / 180) * 111.32;
    let best = Infinity;
    for (let i = 1; i < geometry.length; i++) {
     const a = geometry[i - 1], b = geometry[i];
     if (Math.abs(a.lat - c.lat) > .01 || Math.abs(a.lng - c.lng) > .01) continue;
     const ax = (a.lng - c.lng) * k, ay = (a.lat - c.lat) * 110.57, bx = (b.lng - c.lng) * k, by = (b.lat - c.lat) * 110.57;
     const dx = bx - ax, dy = by - ay, t = dx || dy ? Math.max(0, Math.min(1, -(ax * dx + ay * dy) / (dx * dx + dy * dy))) : 0;
     best = Math.min(best, Math.hypot(ax + t * dx, ay + t * dy));
    }
    if (best <= NEAR_GATE_KM && !row.nearMisses?.some(m => m.network === n.id && zone(m.gate) === zone(g.id))) (row.nearMisses ??= []).push({network: n.id, gate: g.id, metres: Math.round(best * 1000)});
   }
   // Only a priced journey can be under-charged; an unavailable one is safe.
   if (row.nearMisses && status === 'quoted') nearMisses.push({journey: j.name, status, cents: row.cents, nearMisses: row.nearMisses});
  }
  const ok = accepted[j.name];
  if (status.startsWith('unavailable') && !(ok && ok.status === status)) regressions.push(row);
  if (ok && ok.status === 'quoted' && (status !== 'quoted' || ok.cents?.join() !== row.cents?.join())) regressions.push({...row, expected: ok});
  if (!ok && status === 'quoted' && Object.keys(accepted).length) regressions.push({...row, expected: {status: 'not in baseline'}});
  results.push(row);
 }
 write(path.join(dir, 'results.json'), {departure: DEPARTURE, byStatus, gaps, nearMisses, results});
 console.log(JSON.stringify(byStatus, null, 1));
 for (const g of gaps) console.log(`GAP ${g.journey}: ${g.from.lat},${g.from.lng} -> ${g.to.lat},${g.to.lng} (${g.points} pts)`);
 for (const m of nearMisses) console.log(`NEAR MISS ${m.journey} (${m.status}${m.cents ? ' ' + m.cents[0] : ''}): ` + m.nearMisses.map(x => `${x.gate} ${x.metres} m`).join(', '));
 for (const r of regressions) console.log(`NOT ACCEPTED ${r.name}: ${r.status}${r.cents ? ' ' + r.cents[0] : ''}${r.expected ? ' (baseline ' + r.expected.status + (r.expected.cents ? ' ' + r.expected.cents[0] : '') + ')' : ''}`);
 if (nearMisses.length) console.log(`FAIL: ${nearMisses.length} journeys pass a main-line plaza without crossing its gate (possible under-charge)`);
 console.log(regressions.length ? `FAIL: ${regressions.length} journeys unavailable or changed without an accepted reason` : 'PASS: matches the reviewed baseline (prices, accepted unavailable journeys, no plaza near misses)');
 process.exitCode = regressions.length || nearMisses.length ? 1 : 0;
 return {results, nearMisses, accepted};
}

function accept(appDir) {
 const {results, nearMisses, accepted} = check(appDir);
 if (nearMisses.length) { console.error('Refusing: priced journeys pass a plaza uncrossed (fix the gate first).'); process.exitCode = 1; return; }
 const next = {}, missing = [];
 for (const r of results) {
  if (r.status === 'quoted') next[r.name] = {status: r.status, cents: r.cents};
  else if (r.status.startsWith('unavailable') || r.status === 'no_route') {
   const reason = accepted[r.name]?.status === r.status ? accepted[r.name].reason : null;
   if (!reason) missing.push(r.name);
   next[r.name] = {status: r.status, reason: reason ?? 'TODO: why this journey must stay unavailable'};
  }
 }
 write(path.join(dir, 'accepted.json'), next);
 if (missing.length) { console.error('Add a reason in accepted.json for: ' + missing.join(', ')); process.exitCode = 1; }
 else { console.log(`Baseline recorded: ${Object.keys(next).length} journeys`); process.exitCode = 0; }
}

if (mode === 'generate') generate();
else if (mode === 'fetch') fetchAll().catch(e => { console.error(e); process.exitCode = 2; });
else if (mode === 'check') check(appArg);
else if (mode === 'accept') accept(appArg);
else { console.error('usage: sweep_terminals.cjs generate|fetch|check|accept [app]'); process.exitCode = 2; }
