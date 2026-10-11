import fs from 'node:fs';
import assert from 'node:assert/strict';
import {gunzipSync} from 'node:zlib';

const root=new URL('../',import.meta.url);
const read=name=>JSON.parse(fs.readFileSync(new URL(name,root)));
const atlas=read('public/models/atlas-source.json');
const audit=read('modeling/source-quality-audit.json');
assert.equal(atlas.sourceRevision,'6c7f9016bd5899ac8edafd31b9900c151df42ed6');
assert.equal(atlas.parts.length,2913);
assert.equal(atlas.triangles,8198244);
assert.equal(atlas.chunks.length,29);
assert.equal(audit.sourceParts,atlas.parts.length);
assert.equal(audit.sourceTriangles,atlas.triangles);
assert.equal(audit.existingParts,2336);
assert.equal(audit.existingTriangles,read('public/models/atlas.json').triangles);
const buffers=atlas.chunks.map(chunk=>{
 const bytes=fs.readFileSync(new URL(`public${chunk.url}`,root));
 assert.equal(bytes.length,chunk.bytes);
 const zipped=fs.readFileSync(new URL(`public${chunk.gzip}`,root));
 assert.equal(zipped.length,chunk.gzipBytes);
 assert.deepEqual(gunzipSync(zipped),bytes);
 return bytes;
});
const records=new Map(audit.parts.map(part=>[part.id,part]));
const ids=new Set();
let total=0;
for(const part of atlas.parts){
 assert.ok(!ids.has(part.id));ids.add(part.id);
 assert.equal(part.source,'Z-Anatomy');assert.equal(part.license,'CC BY-SA 4.0');
 assert.equal(part.geometryQuality,'source');
 assert.ok(!/\.(j|i|[oe]\d*[rl]|\d{3})$/.test(part.sourceName));
 assert.ok(part.vertexCount>0&&part.indexCount>0&&part.indexCount%3===0);
 const record=records.get(part.id);
 assert.equal(part.vertexCount,record.sourceVertices);
 assert.equal(part.indexCount/3,record.sourceTriangles);
 assert.equal(record.sourceTriangles,record.exportedTriangles);
 const buffer=buffers[part.chunk];
 for(const [offset,length] of [[part.positions,part.vertexCount*12],[part.normals,part.vertexCount*6],[part.indices,part.indexCount*4]]){
  assert.equal(offset%4,0);assert.ok(offset+length<=buffer.length);
 }
 const positions=new Float32Array(buffer.buffer,buffer.byteOffset+part.positions,part.vertexCount*3);
 const indices=new Uint32Array(buffer.buffer,buffer.byteOffset+part.indices,part.indexCount);
 for(const index of indices)assert.ok(index<part.vertexCount,`${part.id}: index out of range`);
 const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
 for(let i=0;i<positions.length;i++){
  assert.ok(Number.isFinite(positions[i]));
  min[i%3]=Math.min(min[i%3],positions[i]);max[i%3]=Math.max(max[i%3],positions[i]);
 }
 assert.deepEqual(part.bounds,[min,max]);
 total+=part.indexCount/3;
}
assert.equal(total,atlas.triangles);
assert.equal(new Set(atlas.concepts.map(c=>c.id)).size,atlas.concepts.length);
for(const concept of atlas.concepts){assert.ok(concept.name&&concept.elements.length);for(const id of concept.elements)assert.ok(ids.has(id));}
for(const name of ['nucleus pulposus l4-l5','right articular capsule of knee joint','right subcutaneous prepatellar bursa']){
 assert.ok(atlas.concepts.some(c=>c.name===name),`Missing source addition: ${name}`);
}
console.log(`Verified ${ids.size} original source meshes, ${total.toLocaleString()} triangles, source/export topology counts and all ${buffers.length} binary/gzip buffers.`);
