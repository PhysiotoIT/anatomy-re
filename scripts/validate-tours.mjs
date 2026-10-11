import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const read = relative => JSON.parse(readFileSync(new URL(relative, import.meta.url), 'utf8'));
const atlas = read('../public/models/atlas.json');
const tours = read('../app/study-tours.json');
const concepts = new Map(atlas.concepts.map(concept => [concept.id, concept]));
const parts = new Map(atlas.parts.map(part => [part.id, part]));
const views = new Set(['front', 'back', 'side', 'top', 'three-quarter']);
const systems = new Set(atlas.parts.map(part => part.system));

assert.ok(tours.length > 0, 'At least one guided tour is required');
assert.equal(new Set(tours.map(tour => tour.id)).size, tours.length, 'Tour IDs must be unique');
for (const tour of tours) {
  assert.ok(tour.title && tour.subtitle && tour.steps.length >= 2, `Incomplete tour: ${tour.id}`);
  assert.equal(new Set(tour.steps.map(step => step.conceptId)).size, tour.steps.length, `Repeated concept in ${tour.id}`);
  for (const step of tour.steps) {
    const concept = concepts.get(step.conceptId);
    assert.ok(concept?.elements.length, `Missing concept ${step.conceptId}`);
    assert.ok(step.title && step.note && views.has(step.view), `Incomplete step ${step.conceptId}`);
    assert.ok(step.systems.length && step.systems.every(system => systems.has(system)), `Unknown system in ${step.conceptId}`);
    assert.ok(concept.elements.some(id => step.systems.includes(parts.get(id)?.system)), `Concept ${step.conceptId} is hidden by its tour layers`);
  }
}
console.log(`Verified ${tours.length} guided tours and ${tours.reduce((count, tour) => count + tour.steps.length, 0)} steps against the atlas.`);
const source=read('../public/models/atlas-source.json');
const sourceTours=read('../app/study-tours-source.json');
const sourceConcepts=new Map(source.concepts.map(c=>[c.id,c]));
const sourceParts=new Map(source.parts.map(p=>[p.id,p]));
for(const tour of sourceTours){
 assert.ok(tour.steps.length>=2);
 for(const step of tour.steps){
  const concept=sourceConcepts.get(step.conceptId);
  assert.ok(concept?.elements.length,`Missing source concept ${step.conceptId}`);
  assert.ok(views.has(step.view)&&step.title&&step.note);
  assert.ok(concept.elements.some(id=>step.systems.includes(sourceParts.get(id)?.system)));
 }
}
const available=[...tours,...sourceTours].filter(t=>t.steps.every(s=>sourceConcepts.has(s.conceptId)));
assert.equal(available.length,4);
console.log(`Verified ${sourceTours.length} additional source tours; ${available.length} complete tours available in full geometry mode.`);
