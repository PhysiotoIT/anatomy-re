import fs from 'node:fs';
import assert from 'node:assert/strict';
const root=new URL('../',import.meta.url);
const path=name=>new URL(name,root);
const atlas=JSON.parse(fs.readFileSync(path('public/models/atlas.json')));
const additions=JSON.parse(fs.readFileSync(path('modeling/generated.json')));
assert.equal(additions.parts.length,6);
assert.equal(additions.concepts.length,9);
const existing=atlas.parts.filter(p=>p.id.startsWith('AR'));
atlas.triangles-=existing.reduce((total,p)=>total+p.indexCount/3,0);
atlas.parts=atlas.parts.filter(p=>!p.id.startsWith('AR'));
atlas.concepts=atlas.concepts.filter(c=>!c.id.startsWith('AR:'));
const previous=atlas.chunks.findIndex(c=>c.url==='/models/blender-additions.bin');
if(previous>=0){assert.equal(previous,atlas.chunks.length-1);atlas.chunks.pop();}
const chunk=atlas.chunks.length;
const binary=fs.readFileSync(path('public/models/blender-additions.bin'));
const compressed=fs.readFileSync(path('public/models/blender-additions.bin.gz'));
atlas.chunks.push({url:'/models/blender-additions.bin',bytes:binary.length,
  gzip:'/models/blender-additions.bin.gz',gzipBytes:compressed.length});
const existingIds=new Set(atlas.parts.map(p=>p.id));
for(const part of additions.parts){
  assert.ok(!existingIds.has(part.id));assert.equal(part.fidelity,'schematic');
  assert.ok(part.references.length&&part.reviewStatus==='unreviewed');
  for(const id of part.replaces??[])assert.ok(existingIds.has(id));
  atlas.parts.push({...part,chunk});
}
const aliases={
 'AR:annulus_fibrosus_L4_L5':['pierścień włóknisty L4-L5','annulus fibrosus'],
 'AR:nucleus_pulposus_L4_L5':['jądro miażdżyste L4-L5','nucleus pulposus'],
 'AR:right_patellar_ligament':['prawe więzadło rzepki'],
 'AR:left_patellar_ligament':['lewe więzadło rzepki'],
 'AR:patellar_ligament':['więzadło rzepki'],
 'AR:right_prepatellar_bursa':['prawa kaletka przedrzepkowa'],
 'AR:left_prepatellar_bursa':['lewa kaletka przedrzepkowa'],
 'AR:prepatellar_bursa':['kaletka przedrzepkowa'],
 'AR:L4_L5_disk_internal':['budowa krążka L4-L5','krążek międzykręgowy L4-L5'],
};
atlas.concepts.push(...additions.concepts.map(c=>({...c,aliases:aliases[c.id]})));
atlas.triangles+=additions.triangles;
atlas.sources=[...(atlas.sources??[]).filter(s=>!s.startsWith('Anatomy RE')),
  'Anatomy RE Blender schematics · CC BY 4.0'];
atlas.scope='Adult male reference anatomy · 2,330 source meshes + 6 optional educational schematics';
fs.writeFileSync(path('public/models/atlas.json'),JSON.stringify(atlas)+'\n');
console.log(`Imported ${additions.parts.length} Blender models; ${atlas.parts.length} meshes, ${atlas.concepts.length} concepts.`);
