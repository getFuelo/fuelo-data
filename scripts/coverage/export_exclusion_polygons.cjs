#!/usr/bin/env node
// Use the app implementation for audit requests; never duplicate its geometry.
const fs = require('fs');
const path = require('path');
const Module = require('module');
const [app, family] = process.argv.slice(2);
if (!app || !family) throw Error('usage: node export_exclusion_polygons.cjs APP FAMILY');
const ts = require(path.resolve(app, 'node_modules/typescript'));
const filename = path.resolve(app, 'src/lib/excludePolygons.ts');
const mod = new Module(filename);
mod._compile(ts.transpileModule(fs.readFileSync(filename, 'utf8'), {
  compilerOptions: {module: ts.ModuleKind.CommonJS},
}).outputText, filename);
const root = path.resolve(__dirname, '../..');
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'pricing-candidates', family+'.json')));
const lines = catalog.pricing.flatMap(net => net.gates.filter(g =>
  net.pricing.kind === 'gates' || net.avoidanceGateIds?.includes(g.id)).map(g => g.line));
if (!lines.length) throw Error('No verified avoidance gates');
const polygons = mod.exports.buildExcludePolygons([{lat:0, lng:0, exclusionLines:lines}]);
fs.writeFileSync(path.join(root, 'audit/2026-09-16/networks', family, 'exclusion-polygons.json'),
  JSON.stringify(polygons.map(ring => ring.map(p => [p.lng,p.lat])), null, 2)+'\n');
