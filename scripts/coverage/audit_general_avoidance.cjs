#!/usr/bin/env node
// Verify routing exclusions separately from independently known tariff totals.
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../..'),app=path.resolve(process.argv[2]);
const ts=require(path.join(app,'node_modules/typescript'));
require.extensions['.ts']=(m,f)=>m._compile(ts.transpileModule(fs.readFileSync(f,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,esModuleInterop:true}}).outputText,f);
const {auditMappedRoute}=require(path.join(app,'src/lib/routePricing.ts'));
const {decodePolyline6}=require(path.join(app,'src/lib/polyline.ts'));
const {roadAvoidanceLines}=require(path.join(app,'src/lib/tollMatching.ts'));
const {findGateCrossings}=require(path.join(app,'src/lib/tollPricing.ts'));
const read=p=>JSON.parse(fs.readFileSync(p));
const catalog=read(path.join(root,'pricing-candidates/spain-integration.json'));
const folder=path.join(root,'pricing-candidates/general-avoidance');
const report={complete:false,scope:'Public-endpoint selective avoidance; totals are diagnostic, not an independent fare oracle.',cases:[],failures:[]};
for(const file of fs.readdirSync(folder).filter(f=>f.includes('-public-')&&f.endsWith('-request.json'))){
 const request=read(path.join(folder,file)),name=file.replace('-request.json','');
 const family=read(path.join(root,'pricing-candidates',request.family+'.json'));
 const fileResponse=path.join(folder,name+'.json');
 if(!fs.existsSync(fileResponse)){report.failures.push({name,reason:'no_retained_route'});continue;}
 const response=read(fileResponse),leg=response.trip.legs[0];
 if(response.trip.legs.length!==1)throw Error('Expected one complete leg');
 const route={geometry:decodePolyline6(leg.shape),durationMin:response.trip.summary.time/60,distanceKm:response.trip.summary.length,hasTolls:response.trip.summary.has_toll,degraded:false,tollSegments:leg.maneuvers.filter(m=>m.toll).map(m=>({beginIdx:m.begin_shape_index,endIdx:m.end_shape_index}))};
 const roadIds=new Set(family.tolls.map(t=>t.id));
 const roadNetworks=catalog.pricing.filter(n=>roadIds.has(n.tollId)||n.sharedRoads?.some(r=>roadIds.has(r.tollId)));
 const lines=[...roadIds].flatMap(id=>roadAvoidanceLines(roadNetworks.filter(n=>n.tollId===id||n.sharedRoads?.some(r=>r.tollId===id)),id));
 if(!lines.length){report.failures.push({name,reason:'whole_road_avoidance_not_supported'});continue;}
 const fences=[{id:'selected-road',gates:lines.map((line,i)=>({id:String(i),line,direction:'both'}))}];
 const crossings=findGateCrossings(route.geometry,fences);
 const priced=auditMappedRoute(route,catalog,'2026-09-16T10:00:00Z');
 const targetEvents=priced.events.filter(e=>catalog.pricing.some(n=>n.id===e.networkId&&roadIds.has(n.tollId)&&!n.sharedRoads));
 const row={name,family:request.family,excludedFenceCrossings:crossings.length,targetPricingEvents:targetEvents.length,quote:priced.quote,distanceKm:route.distanceKm};report.cases.push(row);
 if(crossings.length||targetEvents.length||priced.quote.status==='unavailable')report.failures.push({...row,events:priced.events.map(e=>({network:e.networkId,gate:e.gateId}))});
}
fs.writeFileSync(path.join(root,'audit/2026-09-16/general-avoidance-results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({total:report.cases.length,failures:report.failures},null,2));
process.exitCode=report.failures.length?1:0;
