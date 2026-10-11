# Coverage audit and first Blender additions

This is a targeted audit of the current musculoskeletal catalogue, not an
exhaustive inventory of human anatomy. A missing name means that no separately
selectable concept or mesh was found under the checked synonyms. It does not
prove that the tissue is absent from every compound source mesh.

Baseline: 2,234 BodyParts3D meshes plus 96 Z-Anatomy meshes, 3,589 concepts.

| Structure / detail | Catalogue before this batch | Result / next action |
|---|---|---|
| Intervertebral discs (`disc`, `disk`) | Present, including lumbar discs | Preserve the source meshes |
| Annulus fibrosus and nucleus pulposus | No separately named concepts | Added schematic L4-L5 components `AR001`, `AR002` |
| Patellar ligament (`patellar ligament`, `ligamentum patellae`) | No separately named concepts | Added right/left schematics `AR003`, `AR004` |
| Prepatellar bursa | No separately named concept | Added right/left schematics `AR005`, `AR006` |
| Suprapatellar and infrapatellar bursae | No separately named concepts | Pending; require attachment and extent review |
| Articular cartilage of knee | No separately named concepts | Pending; requires a surface fit to joint cartilage regions |
| Articular capsules | No separately named joint capsules | Pending; avoid representing each capsule as a generic enclosing sphere |
| ACL, PCL, medial/lateral menisci | Present in Z-Anatomy additions | Preserve; approximate alignment still requires anatomical review |
| Achilles / calcaneal tendon | Present under `calcaneal tendon` | No duplicate added |
| Female reference anatomy and anatomical variants | Not included in current reference | Separate dataset integration required |

## Modeling evidence and limits

Three OpenStax first-edition illustrations were opened and analyzed; their
snapshot and CC BY 4.0 license are recorded in `references/openstax/README.md`.
The disc illustration supplies the annulus/nucleus relationship and the knee
illustrations supply the ligament attachment and prepatellar bursa position.
BodyParts3D `FJ3216`, both patellae and tibiae supply the spatial landmarks.

`modeling/build_additions.py` creates an editable Blender file with reference
images packed inside, context meshes, six modeled objects and two preview
renders. Geometry is exported from the exact Blender objects used in the file.
The annulus is an elliptical shell with 14 illustrative concentric grooves;
the nucleus is an ellipsoid fitted to the L4-L5 reference disc plane. The
ligament is a flattened tapered strip with diagrammatic longitudinal ridges
and the bursa is a thin sac. All six now total 206,072 triangles. These shapes
approximate gross relationships; groove count is not measured anatomy.
Lamellar histology, fiber mechanics, patient variation and pathological
anatomy are not modeled. All six are marked `schematic` and `unreviewed`.

The new components are optional in the viewer. When the modeled disc parts
are displayed, the overlapping coarse source disc is hidden; the original
source data and concept remain available. `AR:` concept IDs are local and
are not presented as verified FMA identifiers.

Rebuild with:

```sh
blender --background --factory-startup --python modeling/build_additions.py
node scripts/import-blender-models.mjs
npm run validate:atlas
```

## Full-source audit update

The initial absence checks above applied to the imported 96 Z-Anatomy meshes.
The complete original FBX import now provides 2,913 source meshes and
8,198,244 triangles in a separate, internally consistent catalogue. It includes
nuclei of multiple discs, joint capsules and distinct subcutaneous, subfacial
and subtendinous prepatellar bursae. These structures do not require inventing
new generic shapes. See `docs/blender-source-quality.md` for the full import,
detail limits, editable scene and validation. The earlier source atlas is
preserved as the light mode.
