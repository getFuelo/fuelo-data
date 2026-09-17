#!/usr/bin/env node
// Use the app implementation for audit requests; never duplicate its geometry.
const fs = require('fs');
const path = require('path');
const [app, family] = process.argv.slice(2);
if (!app || !family) throw Error('usage: node export_exclusion_polygons.cjs APP FAMILY');
const ts = require(path.resolve(app, 'node_modules/typescript'));
require.extensions['.ts']=(m,f)=>m._compile(ts.transpileModule(fs.readFileSync(f,'utf8'),{
 compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,esModuleInterop:true},
}).outputText,f);
const {buildExcludePolygons}=require(path.resolve(app,'src/lib/excludePolygons.ts'));
const {roadAvoidanceLines}=require(path.resolve(app,'src/lib/tollMatching.ts'));
const root=path.resolve(__dirname,'../..');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'pricing-candidates',family+'.json')));
const integrated=JSON.parse(fs.readFileSync(path.join(root,'pricing-candidates/spain-integration.json')));
const roads=[...new Set(catalog.tolls.map(t=>t.id))];
const lines=roads.flatMap(id=>roadAvoidanceLines(integrated.pricing.filter(n=>n.tollId===id||n.sharedRoads?.some(r=>r.tollId===id)),id));
if (!lines.length) throw Error('No verified avoidance gates');
const polygons = buildExcludePolygons([{lat:0, lng:0, exclusionLines:lines}]);
fs.writeFileSync(path.join(root, 'audit/2026-09-16/networks', family, 'exclusion-polygons.json'),
  JSON.stringify(polygons.map(ring => ring.map(p => [p.lng,p.lat])), null, 2)+'\n');
