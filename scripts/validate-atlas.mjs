import fs from 'node:fs';
import assert from 'node:assert/strict';
import {gunzipSync} from 'node:zlib';
const filename=process.argv[2]??'atlas.json';
const base=new URL('../public/models/',import.meta.url),atlas=JSON.parse(fs.readFileSync(new URL(filename,base)));
assert.equal(atlas.parts.length,2336);assert.equal(atlas.concepts.length,3598);assert.equal(atlas.chunks.length,17);
const ids=new Set(atlas.parts.map(p=>p.id));assert.equal(ids.size,2336);
assert.equal(atlas.parts.filter(p=>p.source==='Z-Anatomy').length,96);
assert.equal(atlas.parts.filter(p=>p.id.startsWith('FJ')).length,2234);
assert.equal(atlas.parts.filter(p=>p.fidelity==='schematic').length,6);
const files=atlas.chunks.map(c=>{const b=fs.readFileSync(new URL(c.url.split('/').pop(),base));assert.equal(b.length,c.bytes);if(c.gzip){const compressed=fs.readFileSync(new URL(c.gzip.split('/').pop(),base));assert.equal(compressed.length,c.gzipBytes);assert.deepEqual(gunzipSync(compressed),b);}return b;});
let tris=0;
for(const p of atlas.parts){assert.ok(p.name.trim()&&p.name!=='-'&&!p.name.includes('Bounds('));assert.ok(p.conceptId!=='-');assert.ok(p.system);const b=files[p.chunk];assert.ok(p.indices+p.indexCount*4<=b.length);const pos=new Float32Array(b.buffer,b.byteOffset+p.positions,p.vertexCount*3),indices=new Uint32Array(b.buffer,b.byteOffset+p.indices,p.indexCount);assert.ok(indices.length>=3);for(const i of indices)assert.ok(i<p.vertexCount,`${p.id}: invalid vertex`);for(const value of pos)assert.ok(Number.isFinite(value));tris+=p.indexCount/3;}
for(const c of atlas.concepts){assert.ok(c.elements.length);for(const id of c.elements)assert.ok(ids.has(id),`${c.id}: missing ${id}`);}
const additions=JSON.parse(fs.readFileSync(new URL('../modeling/generated.json',import.meta.url)));
assert.equal(tris,atlas.triangles);assert.equal(tris,2406212+additions.triangles);
assert.equal(atlas.parts.filter(p=>p.fidelity==='schematic').reduce((sum,p)=>sum+p.indexCount/3,0),additions.triangles);
for(const part of atlas.parts.filter(p=>p.fidelity==='schematic')){
 assert.ok(part.references?.length&&part.reviewStatus==='unreviewed'&&part.license==='CC BY 4.0');
 for(const id of part.replaces??[])assert.ok(ids.has(id));
 const b=files[part.chunk],pos=new Float32Array(b.buffer,b.byteOffset+part.positions,part.vertexCount*3),idx=new Uint32Array(b.buffer,b.byteOffset+part.indices,part.indexCount);
 const edges=new Map();for(let t=0;t<idx.length;t+=3){const triangle=Array.from(idx.subarray(t,t+3));assert.equal(new Set(triangle).size,3);for(let j=0;j<3;j++){const a=triangle[j],c=triangle[(j+1)%3],key=a<c?`${a}:${c}`:`${c}:${a}`;edges.set(key,(edges.get(key)??0)+1);}}
 assert.ok([...edges.values()].every(count=>count===2),`${part.id}: modeled surface must be closed and manifold`);
 for(let axis=0;axis<3;axis++){const values=Array.from({length:part.vertexCount},(_,i)=>pos[i*3+axis]);assert.ok(Math.abs(Math.min(...values)-part.bounds[0][axis])<1e-6);assert.ok(Math.abs(Math.max(...values)-part.bounds[1][axis])<1e-6);}
}
const modeled=new Map(atlas.parts.map(p=>[p.id,p]));
for(const [bursa,patella] of [['AR005','FJ3381'],['AR006','FJ3275']])assert.ok(modeled.get(bursa).bounds[0][2]>modeled.get(patella).bounds[1][2],`${bursa}: prepatellar model must lie anterior to the source patella`);
for(let axis=0;axis<3;axis++){assert.ok(modeled.get('AR002').bounds[0][axis]>=modeled.get('AR001').bounds[0][axis]);assert.ok(modeled.get('AR002').bounds[1][axis]<=modeled.get('AR001').bounds[1][axis]);}
console.log(`Verified ${ids.size} individually indexed meshes, ${atlas.concepts.length} complete concept mappings, ${tris.toLocaleString()} triangles, and every binary and gzip buffer.`);
