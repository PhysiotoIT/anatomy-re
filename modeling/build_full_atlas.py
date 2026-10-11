"""Build editable source-quality anatomy and the complete existing atlas.

blender -b --factory-startup --python modeling/build_full_atlas.py -- /path/to/Z-Anatomy
No decimation, subdivision or invented surface displacement is applied.
"""
import bpy
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(sys.argv[sys.argv.index('--') + 1])
REVISION = '6c7f9016bd5899ac8edafd31b9900c151df42ed6'
ATLAS = json.loads((ROOT / 'public/models/atlas.json').read_text())
COLORS = dict(skeletal='#e2d9ba', muscular='#a85b50', connective='#aec3bb',
              arterial='#c05245', venous='#527c9f', cardiac='#b96760', nervous='#d8b565',
              lymphatic='#879f7c', sensory='#b0c8ce', digestive='#b8916b',
              respiratory='#b98991', urinary='#b47961', endocrine='#c5a09a', reproductive='#bda098', integumentary='#ba9b7d')
FILES = ['SkeletalSystem100.fbx', 'Joints100.fbx', 'MuscularSystem100.fbx',
         'CardioVascular41.fbx', 'NervousSystem100.fbx', 'LymphoidOrgans100.fbx', 'VisceralSystem100.fbx']


def collection(name, parent=None):
    result = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(result)
    return result


def system_for(file, name):
    text = name.lower()
    if file.startswith('Skeletal'): return 'skeletal'
    if file.startswith('Joints'): return 'connective'
    if file.startswith('Muscular'):
        return 'connective' if re.search(r'bursa|ligament|retinacul|aponeuros|fascia|tendon|septum', text) else 'muscular'
    if file.startswith('Lymphoid'): return 'lymphatic'
    if file.startswith('Cardio'):
        if re.search(r'vein|venous|sinus|vena', text): return 'venous'
        if re.search(r'arter|aorta|trunk|branches|circulus', text): return 'arterial'
        return 'cardiac'
    if file.startswith('Nervous'):
        return 'sensory' if re.search(r'eyeball|cornea|iris|lens|retina|sclera|cochlea|cochlear|vestibule|tympan|zonular', text) else 'nervous'
    if re.search(r'bronch|lung|larynx|trachea|pleura|glottis|epiglott|vocal|carina', text): return 'respiratory'
    if re.search(r'kidney|renal|ureter|bladder|urethra', text): return 'urinary'
    if re.search(r'testis|epididym|prostate|penis|seminal|deferens|scrot|ejacul|prepuce|spermatic|glans', text): return 'reproductive'
    if re.search(r'pituitary|hypophys|thyroid|suprarenal|adrenal|pineal', text): return 'endocrine'
    return 'digestive'


def anatomical_name(name):
    name = re.sub(r'^\((.*)\)(\.[rl])?$', r'\1\2', name)
    if name.endswith('.r'): return 'right ' + name[:-2].lower()
    if name.endswith('.l'): return 'left ' + name[:-2].lower()
    return name.lower()


def canonical(name):
    return re.sub(r'[^a-z0-9]+', ' ', name.lower().replace(' disk', ' disc').replace(' muscle', '')).strip()


def coordinates(mesh, matrix):
    vertices = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get('co', vertices)
    vertices = vertices.reshape(-1, 3)
    m = np.array(matrix, dtype=float)
    return vertices @ m[:3, :3].T + m[:3, 3]


def atlas_coordinates(vertices):
    return np.column_stack((vertices[:, 0], vertices[:, 2], -vertices[:, 1]))


def packed_geometry(mesh, matrix):
    mesh.calc_loop_triangles()
    positions = atlas_coordinates(coordinates(mesh, matrix)).astype('<f4')
    normals = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get('normal', normals)
    normals = normals.reshape(-1, 3) @ np.linalg.inv(np.array(matrix)[:3, :3])
    normals /= np.maximum(np.linalg.norm(normals, axis=1)[:, None], 1e-20)
    normals = np.round(np.clip(atlas_coordinates(normals), -1, 1) * 32767).astype('<i2')
    indices = np.empty(len(mesh.loop_triangles) * 3, dtype='<u4')
    mesh.loop_triangles.foreach_get('vertices', indices)
    return positions, normals, indices


bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'METERS'
source_collection = collection('01 · Z-Anatomy · ORIGINAL topology · CC BY-SA 4.0')
current_collection = collection('02 · Existing atlas · COMPLETE · 2336 objects')
helper_collection = collection('03 · Source landmarks and attachments · optional')
helper_collection.hide_render = True
references = collection('04 · OpenStax references · CC BY 4.0')
references.hide_render = True
source_systems = {key: collection(key.title(), source_collection) for key in COLORS}
current_systems = {key: collection(key.title(), current_collection) for key in COLORS}
materials = {}
for system, color in COLORS.items():
    srgb = [int(color[i:i+2], 16) / 255 for i in [1, 3, 5]]
    rgb = tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in srgb)
    mat = bpy.data.materials.new(system)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes['Principled BSDF']
    shader.inputs['Base Color'].default_value = (*rgb, 1)
    shader.inputs['Roughness'].default_value = .5
    materials[system] = mat

parts, chunks, audit, blob = [], [], [], bytearray()
source_checksums = {}


def append(array):
    blob.extend(b'\0' * ((-len(blob)) % 4))
    start = len(blob)
    blob.extend(array.tobytes())
    return start


def flush():
    global blob
    if not blob: return
    filename = f'source-{len(chunks)}.bin'
    target = ROOT / 'public/models' / filename
    target.write_bytes(blob)
    compressed = gzip.compress(bytes(blob), compresslevel=6, mtime=0)
    target.with_suffix('.bin.gz').write_bytes(compressed)
    chunks.append(dict(url='/models/' + filename, bytes=len(blob),
                       gzip='/models/' + filename + '.gz', gzipBytes=len(compressed)))
    blob = bytearray()


for filename in FILES:
    path = SOURCE / 'Resources/Models/FBX' / filename
    source_checksums[filename] = hashlib.sha256(path.read_bytes()).hexdigest()
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(path), use_custom_normals=True, use_anim=False)
    bpy.context.view_layer.update()
    imported = sorted(set(bpy.data.objects) - before, key=lambda obj: obj.name)
    # FBX hierarchy roots contain axis transforms. Freeze every world matrix
    # before removing any empty parent, or the anatomical assembly is lost.
    world_matrices = {obj: obj.matrix_world.copy() for obj in imported}
    kept, helper_count = 0, 0
    for obj in imported:
        for coll in list(obj.users_collection): coll.objects.unlink(obj)
        if obj.type != 'MESH':
            bpy.data.objects.remove(obj, do_unlink=True)
            continue
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        mesh = obj.data
        obj.parent = None
        obj.animation_data_clear()
        # Bake transforms to preserve shear and nonuniform parent scales too.
        # Matrix assignment alone can lose shear when Blender decomposes it.
        mesh.transform(world_matrices[obj])
        obj.matrix_world = Matrix.Identity(4)
        mesh.calc_loop_triangles()
        is_helper = bool(re.search(r'\.(?:j|i|[oe]\d*[rl]|\d{3})$', obj.name)) or not len(mesh.loop_triangles)
        if is_helper:
            helper_collection.objects.link(obj)
            helper_count += 1
            obj['role'] = 'source label/landmark/attachment, excluded from anatomy catalogue'
            continue
        source_name = obj.name
        name = anatomical_name(source_name)
        system = system_for(filename, name)
        source_systems[system].objects.link(obj)
        mesh.materials.clear()
        mesh.materials.append(materials[system])
        for polygon in mesh.polygons: polygon.use_smooth = True
        pid = f'ZS{len(parts)+1:04d}'
        obj.name = f'{pid} · {name}'
        obj['atlas_id'] = pid
        obj['source_name'] = source_name
        obj['source_file'] = filename
        obj['license'] = 'CC BY-SA 4.0'
        obj['geometry_policy'] = 'original source topology; no decimation or subdivision'
        positions, normals, indices = packed_geometry(mesh, obj.matrix_world)
        if len(blob) > 6_000_000: flush()
        part = dict(id=pid, name=name, conceptId=f'ZS:{pid}', system=system,
                    source='Z-Anatomy', sourceName=source_name, sourceFile=filename,
                    license='CC BY-SA 4.0', geometryQuality='source',
                    chunk=len(chunks), positions=append(positions), normals=append(normals),
                    indices=append(indices), vertexCount=len(positions), indexCount=len(indices),
                    bounds=[positions.min(axis=0).tolist(), positions.max(axis=0).tolist()])
        parts.append(part)
        audit.append(dict(id=pid, name=name, sourceFile=filename, sourceVertices=len(mesh.vertices),
                          sourceTriangles=len(mesh.loop_triangles), exportedTriangles=len(indices)//3))
        kept += 1
    print('IMPORTED ORIGINAL', filename, kept, 'anatomy;', helper_count, 'helpers', flush=True)
flush()

# One independently selectable concept per mesh; bilateral groups are local IDs.
concepts = [dict(id=p['conceptId'], name=p['name'], aliases=[p['sourceName']], elements=[p['id']]) for p in parts]
groups = {}
for p in parts:
    if p['name'].startswith(('right ', 'left ')):
        groups.setdefault(p['name'].split(' ', 1)[1], []).append(p['id'])
for i, (name, elements) in enumerate(sorted(groups.items())):
    concepts.append(dict(id=f'ZS:group{i:04d}', name=name, elements=elements))

# Reuse legacy concepts only for unambiguous name matches; never manufacture FMA assignments.
matches = {}
for c in concepts: matches.setdefault(canonical(c['name']), []).append(c)
mapped_legacy = 0
for old in ATLAS['concepts']:
    candidates = matches.get(canonical(old['name']), [])
    if len(candidates) == 1:
        concepts.append(dict(id=old['id'], name=old['name'], elements=candidates[0]['elements'],
                             aliases=old.get('aliases', [])))
        mapped_legacy += 1

manifest = dict(version='Z-Anatomy source topology 2024 · Blender export', sex='male',
    source='Z-Anatomy', sources=['Z-Anatomy contributors · CC BY-SA 4.0', 'Derived in part from BodyParts3D · DBCLS'],
    scope='Original source geometry; adult reference; labels and attachment overlays excluded',
    quality='source', sourceRevision=REVISION, parts=parts, concepts=concepts, chunks=chunks,
    triangles=sum(p['indexCount']//3 for p in parts))
(ROOT / 'public/models/atlas-source.json').write_text(json.dumps(manifest, separators=(',', ':'))+'\n')

# Reconstruct every existing mesh as its own editable object in a separate view layer.
buffers = {}
for part in ATLAS['parts']:
    ci = part['chunk']
    if ci not in buffers:
        buffers[ci] = (ROOT / 'public' / ATLAS['chunks'][ci]['url'].lstrip('/')).read_bytes()
    data = buffers[ci]
    vertices = np.frombuffer(data, '<f4', part['vertexCount']*3, part['positions']).reshape(-1, 3)
    vertices = np.column_stack((vertices[:, 0], -vertices[:, 2], vertices[:, 1]))
    indices = np.frombuffer(data, '<u4', part['indexCount'], part['indices']).reshape(-1, 3)
    assert int(indices.max()) < len(vertices), f"{part['id']}: invalid indices; rebuild/import additions before constructing the full scene"
    mesh = bpy.data.meshes.new(part['id'])
    mesh.from_pydata(vertices.tolist(), [], indices.tolist())
    mesh.materials.append(materials[part['system']])
    for polygon in mesh.polygons: polygon.use_smooth = True
    obj = bpy.data.objects.new(f"{part['id']} · {part['name']}", mesh)
    current_systems[part['system']].objects.link(obj)
    for key in ['id', 'conceptId', 'source', 'fidelity', 'reviewStatus', 'license']:
        obj[key] = part.get(key, 'BodyParts3D' if key == 'source' else 'CC BY 4.0' if key == 'license' else '')
    obj['geometry_policy'] = 'existing atlas geometry; optimized source, not recovered detail'
del buffers

for i, image_path in enumerate(sorted((ROOT / 'references/openstax').glob('*.jpg'))):
    picture = bpy.data.images.load(str(image_path))
    picture.pack()
    obj = bpy.data.objects.new(image_path.stem, None)
    obj.empty_display_type = 'IMAGE'
    obj.data = picture
    obj.location = (-.8 - i * .6, .2, 1)
    obj.empty_display_size = .5
    references.objects.link(obj)

report = dict(sourceRevision=REVISION, sourceChecksums=source_checksums,
    sourceParts=len(parts), sourceTriangles=manifest['triangles'], legacyConceptsMatched=mapped_legacy,
    existingParts=len(ATLAS['parts']), existingTriangles=ATLAS['triangles'],
    excludedHelperObjects=len(helper_collection.objects), parts=audit)
(ROOT / 'modeling/source-quality-audit.json').write_text(json.dumps(report, indent=2)+'\n')
for filename, content in [
    ('README · geometry and license', 'SOURCE QUALITY contains original Z-Anatomy topology without simplification.\n'
     'CURRENT ATLAS contains every existing browser mesh in its original coordinate frame.\n'
     'The two references have different placements; use separate view layers, never overlay them as registered scans.\n'
     'Higher geometric resolution does not establish anatomical correctness. No anatomist review performed.\n'
     'Z-Anatomy source: https://github.com/LluisV/Z-Anatomy/tree/'+REVISION+'\n'
     'Full composed scene: CC BY-SA 4.0. Individual BodyParts3D and OpenStax works remain CC BY 4.0.\n'
     'BodyParts3D: © The Database Center for Life Science. Z-Anatomy: contributors incl. Gauthier Kervyn and Lluís Vinent Juanico.\n'),
    ('Z-Anatomy LICENSE', (SOURCE / 'LICENSE').read_text()),
    ('Existing atlas ATTRIBUTION', (ROOT / 'public/ATTRIBUTION.md').read_text()),
]:
    bpy.data.texts.new(filename).write(content)

original_layer = scene.view_layers[0]
original_layer.name = 'SOURCE QUALITY · original geometry'
original_layer.layer_collection.children[current_collection.name].exclude = True
original_layer.layer_collection.children[helper_collection.name].exclude = True
existing_layer = scene.view_layers.new('CURRENT ATLAS · complete editable reference')
existing_layer.layer_collection.children[source_collection.name].exclude = True
existing_layer.layer_collection.children[helper_collection.name].exclude = True
existing_layer.use = False

scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.show_specular_highlight = True
scene.display.shading.background_type = 'WORLD'
scene.world.color = (.92, .95, .97)
scene.render.resolution_x, scene.render.resolution_y = 1800, 2200
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'Standard'
camera_data = bpy.data.cameras.new('Atlas · anterior overview')
camera_data.type = 'ORTHO'
camera_data.ortho_scale = 2.05
camera = bpy.data.objects.new(camera_data.name, camera_data)
scene.collection.objects.link(camera)
camera.location = (0, -3, .84)
camera.rotation_euler = (Vector((0, 0, .84)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = camera
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_distance = 2.1
            area.spaces.active.region_3d.view_location = (0, 0, .85)
            area.spaces.active.clip_start = .0001
            area.spaces.active.shading.color_type = 'MATERIAL'
bpy.context.window.view_layer = original_layer
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'modeling/anatomy-full-source.blend'), compress=True)
renderer = ROOT / 'modeling/render_full_scene.py'
exec(compile(renderer.read_text(), str(renderer), 'exec'), {'__file__': str(renderer), '__name__': '__main__'})
print('COMPLETE',len(parts),'original source meshes,',manifest['triangles'],'triangles;',len(ATLAS['parts']),'existing meshes',flush=True)
