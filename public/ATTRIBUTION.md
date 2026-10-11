# Anatomy data attribution

BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International.

- License: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html (updated 2025-02-27)
- Dataset: https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html
- License terms: https://creativecommons.org/licenses/by/4.0/
- Source geometry: `isa_BP3D_4.0_obj_99.zip`, BodyParts3D 4.0.
- English names and relationships: IS-A and PART-OF concept, element, and inclusion tables from the same archive.
- Publication: Mitsuhashi et al. (2009), BodyParts3D: 3D structure database for anatomical concepts. https://doi.org/10.1093/nar/gkn613

Adaptations: axes and units converted from millimeters/Z-up to meters/Y-up; translated to rest at the stage; geometry simplified using meshoptimizer with 0.2% relative error limit per structure; normals quantized to signed 16-bit; packed into binary chunks; curated display system groupings and colors. The source contains 2,234 individual OBJ meshes; all remain represented. The combined hierarchy contains 3,432 named FMA concepts, which may reference multiple meshes. Original source identity is preserved in the manifest.

Source OBJ comments mention an older CC BY-SA 2.1 Japan license. The official current database license linked above supersedes that legacy text and explicitly permits redistribution and adaptation under CC BY 4.0.

BodyParts3D represents an adult male reference anatomy based on TARO MRI and anatomical illustration refinements. It is not a complete model of every possible human anatomical structure or variation. This interface is educational and is not a clinical tool.

## Z-Anatomy additions

96 additional meshes (117,944 triangles) come from [Z-Anatomy](https://github.com/LluisV/Z-Anatomy), © its contributors, licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). They cover selected joint ligaments, menisci, labra and muscles missing from this BodyParts3D build. Z-Anatomy itself derives in part from BodyParts3D. The extracted source was converted from the project's FBX models to GLB, selected and aligned to the BodyParts3D reference, simplified, quantized and packed into `models/zanatomy.bin` by the conversion script at `PhysiotoIT/strona/_build/atlas_extra/zanatomy.mjs`. The adapted Z-Anatomy geometry and its metadata are redistributed under CC BY-SA 4.0. The application code remains MIT licensed.

The 96 parts retain their `ZA` identifiers and `source: Z-Anatomy` metadata in `atlas.json`. The 2,234 original BodyParts3D meshes retain their original `FJ` identifiers. The two source sets are separately credited in the viewer. Spatial alignment is approximate; this is an educational composite, not a patient scan.

## Full source geometry exported through Blender

`models/atlas-source.json` and `models/source-*.bin(.gz)` contain 2,913
anatomical meshes and 8,198,244 triangles from the original Z-Anatomy FBX
files at commit `6c7f9016bd5899ac8edafd31b9900c151df42ed6`:
https://github.com/LluisV/Z-Anatomy/tree/6c7f9016bd5899ac8edafd31b9900c151df42ed6/Resources/Models/FBX

© Z-Anatomy contributors, including Gauthier Kervyn and Lluís Vinent Juanico,
CC BY-SA 4.0; derived in part from BodyParts3D, © DBCLS. The original full
license is preserved in `references/zanatomy/LICENSE.txt`.

Adaptations: imported in Blender 4.3.2, source hierarchy world transforms
preserved, exported from meter/Z-up to meter/Y-up coordinates, normals packed
as signed 16-bit, anatomical mesh names normalized, display systems and
colors assigned, helper labels/landmarks and attachment surfaces separated,
and geometry packed into 29 binary chunks. No decimation or subdivision is
applied to these meshes. Local `ZS` IDs identify the original mesh names;
legacy concepts are included only for unambiguous normalized-name matches.
These matches do not constitute independent ontology or anatomy validation.

The adapted full source meshes, metadata, rendered previews and composed
`modeling/anatomy-full-source.blend` scene are redistributed under CC BY-SA
4.0. The scene contains a separate view layer of the existing atlas and
packed OpenStax references, with their CC BY 4.0 attribution retained.
Application and build-script code remain MIT licensed. Source detail varies
by structure and has not been reviewed by an anatomist in this project.

## Blender educational additions

Six schematic models were created in Blender 4.3.2 by the Anatomy RE project:
L4-L5 annulus fibrosus and nucleus pulposus, bilateral patellar ligaments and
bilateral prepatellar bursae. The adapted shapes and their metadata are
distributed under CC BY 4.0. Source spatial landmarks are from BodyParts3D;
reference illustrations are from OpenStax / Rice University, *Anatomy and
Physiology*, first edition, CC BY 4.0, repository snapshot
`fb2912b3c02522ef63c2306c8100119f20a5e31b`. Plates 716, 917 and 908 are
included with source URLs and license in `references/openstax/README.md`.

These are original schematic constructions based on the illustrations and
existing source landmarks, not reconstructions of measured internal anatomy.
They are marked `fidelity: schematic` and `reviewStatus: unreviewed`. The
editable Blender file, build script, preview renders and gap audit are in
`modeling/` and `docs/atlas-gaps.md`. When a modeled disc component is shown,
the overlapping coarse BodyParts3D disc is hidden by the viewer; its source
geometry remains in the dataset. Z-Anatomy data remain CC BY-SA 4.0.

## Historical assets (not included in the current release)

Earlier repository revisions included female reference anatomy: Kristen Browne and Heidi Schlehlein, Human Reference Atlas / HuBMAP, *3D Reference Organ Set for Female v1.5* (2023). CC BY 4.0. Geometry adapted for this viewer.

- Source DOI: https://doi.org/10.48539/HBM352.BTSQ.586
- Dataset: https://lod.humanatlas.io/ref-organ/united-female/v1.5
- Original GLB: https://cdn.humanatlas.io/digital-objects/ref-organ/united-female/v1.5/assets/3d-vh-f-united.glb
- License: https://creativecommons.org/licenses/by/4.0/

Adaptations: translated native meter/Y-up coordinates onto the stage, coincident vertices welded and source normals averaged, geometry simplified with a 0.2% per-structure relative error bound, and normals quantized. Colors and display systems are curated for this interface. All 888 source meshes are represented, with 1,073 source nodes available as selectable individual or compound concepts.

This is a reference assembly with whole-body surface and selected organs, including female reproductive anatomy. Its skeleton and muscle coverage is partial. It is not a complete model of every human structure or a single-person scan. Eight placenta/umbilical structures are classified under Pregnancy reference and hidden by default.
