"""Run with: blender --background --factory-startup --python modeling/build_additions.py

Educational models based on OpenStax 1e plates and BodyParts3D landmarks.
Atlas coordinates: meters, Y up; Blender coordinates: meters, Z up.
"""
import bpy
import bmesh
import gzip
import json
import math
import struct
from pathlib import Path

import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
ATLAS = json.loads((ROOT / 'public/models/atlas.json').read_text())
PARTS = {p['id']: p for p in ATLAS['parts']}
GENERATED = []
CHUNKS = {}


def to_blender(points):
    p = np.asarray(points)
    return np.column_stack((p[:, 0], -p[:, 2], p[:, 1]))


def to_atlas(points):
    p = np.asarray(points)
    return np.column_stack((p[:, 0], p[:, 2], -p[:, 1]))


def source_mesh(pid):
    p = PARTS[pid]
    if p['chunk'] not in CHUNKS:
        CHUNKS[p['chunk']] = (ROOT / 'public' / ATLAS['chunks'][p['chunk']]['url'].lstrip('/')).read_bytes()
    blob = CHUNKS[p['chunk']]
    vertices = np.frombuffer(blob, '<f4', p['vertexCount'] * 3, p['positions']).reshape(-1, 3).astype(float)
    faces = np.frombuffer(blob, '<u4', p['indexCount'], p['indices']).reshape(-1, 3)
    return vertices, faces


def make_mesh(name, vertices, faces, color, collection):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(to_blender(vertices).tolist(), [], [list(f) for f in faces])
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*color, 1)
    mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .65
    mesh.materials.append(mat)
    obj.color = (*color, 1)
    return obj


def add_model(pid, name, concept, vertices, faces, color, refs, replaces=()):
    obj = make_mesh(name, vertices, faces, color, models)
    obj['source'] = 'Anatomy RE · Blender'
    obj['fidelity'] = 'schematic; not anatomist reviewed'
    obj['references'] = ', '.join(refs)
    obj['license'] = 'CC BY 4.0'
    info = dict(id=pid, name=name, conceptId=concept, system='connective',
                source='Anatomy RE · Blender', fidelity='schematic',
                reviewStatus='unreviewed', license='CC BY 4.0',
                color='#' + ''.join(f'{round(c * 255):02x}' for c in color),
                references=refs, replaces=list(replaces))
    GENERATED.append((obj, info))
    return obj


def ellipsoid(center, axes, radii, segments=192, rings=64):
    vertices = [center + axes[2] * radii[2]]
    for ring in range(1, rings):
        phi = math.pi * ring / rings
        for i in range(segments):
            theta = 2 * math.pi * i / segments
            vertices.append(center + axes[0] * radii[0] * math.sin(phi) * math.cos(theta)
                            + axes[1] * radii[1] * math.sin(phi) * math.sin(theta)
                            + axes[2] * radii[2] * math.cos(phi))
    bottom = len(vertices)
    vertices.append(center - axes[2] * radii[2])
    faces = []
    for i in range(segments):
        faces.append((0, 1 + i, 1 + (i + 1) % segments))
    for ring in range(rings - 2):
        for i in range(segments):
            a = 1 + ring * segments + i
            b = 1 + ring * segments + (i + 1) % segments
            faces.append((a, a + segments, b + segments, b))
    last = 1 + (rings - 2) * segments
    for i in range(segments):
        faces.append((bottom, last + (i + 1) % segments, last + i))
    return vertices, faces


bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
models = bpy.data.collections.new('Educational additions · CC BY 4.0')
context = bpy.data.collections.new('BodyParts3D context · CC BY 4.0')
references = bpy.data.collections.new('OpenStax 1e reference illustrations · CC BY 4.0')
for collection in [models, context, references]:
    bpy.context.scene.collection.children.link(collection)

for pid in ['FJ3165', 'FJ3168', 'FJ3381', 'FJ3387', 'FJ3275', 'FJ3282']:
    vertices, faces = source_mesh(pid)
    make_mesh(PARTS[pid]['name'], vertices, faces, (.73, .68, .55), context)

# Disc: derive orientation and outer footprint from the existing L4-L5 disc.
vertices, _ = source_mesh('FJ3216')
center = (vertices.min(axis=0) + vertices.max(axis=0)) / 2
eigenvalues, eigenvectors = np.linalg.eigh(np.cov((vertices - center).T))
normal = eigenvectors[:, 0]
if normal[1] < 0:
    normal *= -1
u = np.array([1., 0., 0.])
u -= normal * np.dot(u, normal)
u /= np.linalg.norm(u)
v = np.cross(u, normal)
projected = np.column_stack(((vertices - center) @ u, (vertices - center) @ v))
radii = (projected.max(axis=0) - projected.min(axis=0)) / 2
half_height = float(np.quantile(np.abs((vertices - center) @ normal), .9))
inner_center = center - v * radii[1] * .08
segments = 256
ring_vertices = []
# A closed annular cross-section, with 14 illustrative concentric lamellar
# grooves on both end surfaces. Groove count/depth are diagrammatic; neither
# histology nor the real alternating collagen orientation is reconstructed.
cross_section = []
for scale in np.linspace(.46, 1, 85):
    relative = (scale - .46) / .54
    groove = .035 * (1 - math.cos(relative * 14 * 2 * math.pi)) / 2
    rim = .06 * (abs(2 * relative - 1) ** 12)
    cross_section.append((float(scale), 1 - groove - rim))
cross_section.extend((1., float(level)) for level in np.linspace(.8, -.8, 9))
cross_section.extend((scale, -height) for scale, height in reversed(cross_section[:85]))
cross_section.extend((.46, float(level)) for level in np.linspace(-.8, .8, 9))
for scale, level in cross_section:
    origin = center * ((scale - .46) / .54) + inner_center * ((1 - scale) / .54)
    for i in range(segments):
        theta = 2 * math.pi * i / segments
        notch = 1 - .10 * max(0, -math.sin(theta)) ** 6
        ring_vertices.append(origin + u * radii[0] * scale * math.cos(theta)
                             + v * radii[1] * scale * math.sin(theta) * notch
                             + normal * half_height * level)
ring_faces = []
for row in range(len(cross_section)):
    next_row = (row + 1) % len(cross_section)
    for i in range(segments):
        j = (i + 1) % segments
        ring_faces.append((row * segments + i, row * segments + j,
                           next_row * segments + j, next_row * segments + i))
add_model('AR001', 'annulus fibrosus of L4-L5 intervertebral disk (schematic)',
          'AR:annulus_fibrosus_L4_L5', ring_vertices, ring_faces,
          (.48, .71, .79), ['openstax-716', 'bodyparts3d-FJ3216'], ['FJ3216'])
core_vertices, core_faces = ellipsoid(inner_center, [u, v, normal],
                                     [radii[0] * .45, radii[1] * .44, half_height * .92])
add_model('AR002', 'nucleus pulposus of L4-L5 intervertebral disk (schematic)',
          'AR:nucleus_pulposus_L4_L5', core_vertices, core_faces,
          (.20, .50, .62), ['openstax-716', 'bodyparts3d-FJ3216'], ['FJ3216'])

for side, patella_id, tibia_id, ligand_id, bursa_id in [
        ('right', 'FJ3381', 'FJ3387', 'AR003', 'AR005'),
        ('left', 'FJ3275', 'FJ3282', 'AR004', 'AR006')]:
    patella, _ = source_mesh(patella_id)
    tibia, _ = source_mesh(tibia_id)
    apex = patella[np.argsort(patella[:, 1])[:7]].mean(axis=0)
    target_height = tibia[:, 1].max() - .047
    candidates = tibia[np.abs(tibia[:, 1] - target_height) < .009]
    insertion = candidates[np.argsort(candidates[:, 2])[-3:]].mean(axis=0)
    ligament_vertices, ligament_faces = [], []
    long_steps, around = 96, 96
    width_axis = np.array([1., 0., 0.])
    for row in range(long_steps + 1):
        t = row / long_steps
        point = apex * (1 - t) + insertion * t + np.array([0, 0, .003 * math.sin(math.pi * t)])
        tangent = insertion - apex + np.array([0, 0, .003 * math.pi * math.cos(math.pi * t)])
        depth_axis = np.cross(width_axis, tangent)
        depth_axis /= np.linalg.norm(depth_axis)
        half_width = .0075 * (1 - .16 * math.sin(math.pi * t))
        for i in range(around):
            theta = 2 * math.pi * i / around
            # Small longitudinal ridges communicate a fibrous band; these
            # diagrammatic grooves are not measured individual collagen fibers.
            depth = .0015 + .00008 * math.cos(18 * theta) * math.sin(math.pi * t)
            ligament_vertices.append(point + width_axis * half_width * math.cos(theta)
                                     + depth_axis * depth * math.sin(theta))
    for row in range(long_steps):
        for i in range(around):
            j = (i + 1) % around
            a, b = row * around + i, row * around + j
            ligament_faces.append((a, b, b + around, a + around))
    ligament_faces += [tuple(reversed(range(around))), tuple(long_steps * around + i for i in range(around))]
    add_model(ligand_id, f'{side} patellar ligament (schematic)',
              f'AR:{side}_patellar_ligament', ligament_vertices, ligament_faces,
              (.87, .83, .66), ['openstax-917', patella_id, tibia_id])
    lo, hi = patella.min(axis=0), patella.max(axis=0)
    bursa_center = (lo + hi) / 2
    bursa_center[2] = hi[2] + .0018
    bv, bf = ellipsoid(bursa_center, np.eye(3),
                        [(hi[0] - lo[0]) * .36, (hi[1] - lo[1]) * .39, .0013])
    add_model(bursa_id, f'{side} prepatellar bursa (schematic)',
              f'AR:{side}_prepatellar_bursa', bv, bf,
              (.45, .75, .80), ['openstax-908', 'openstax-917', patella_id])

# Keep the actual reference illustrations in the editable Blender file.
for i, filename in enumerate(['716_Intervertebral_Disk.jpg', '917_Knee_Joint.jpg', '908_Bursa.jpg']):
    image = bpy.data.images.load(str(ROOT / 'references/openstax' / filename))
    image.pack()
    obj = bpy.data.objects.new(filename, None)
    obj.empty_display_type = 'IMAGE'
    obj.data = image
    obj.empty_display_size = .5
    obj.location = (-.7 - i * .55, 0, 1)
    obj.hide_render = True
    references.objects.link(obj)

# Export the same meshes used in Blender into the atlas binary format.
blob = bytearray()


def append(array):
    blob.extend(b'\0' * ((-len(blob)) % 4))
    start = len(blob)
    blob.extend(array.tobytes())
    return start


parts = []
for obj, info in GENERATED:
    mesh = obj.data
    mesh.calc_loop_triangles()
    positions = to_atlas([vertex.co[:] for vertex in mesh.vertices]).astype('<f4')
    normals = to_atlas([vertex.normal[:] for vertex in mesh.vertices])
    indices = np.array([triangle.vertices[:] for triangle in mesh.loop_triangles], dtype='<u4').reshape(-1)
    p = dict(info, chunk=0, positions=append(positions),
             normals=append(np.round(np.clip(normals, -1, 1) * 32767).astype('<i2')),
             indices=append(indices), vertexCount=len(positions), indexCount=len(indices),
             bounds=[positions.min(axis=0).tolist(), positions.max(axis=0).tolist()])
    parts.append(p)
concepts = [dict(id=p['conceptId'], name=p['name'], elements=[p['id']]) for p in parts]
concepts.extend([
    dict(id='AR:patellar_ligament', name='patellar ligament (schematic)', elements=['AR003', 'AR004']),
    dict(id='AR:prepatellar_bursa', name='prepatellar bursa (schematic)', elements=['AR005', 'AR006']),
    dict(id='AR:L4_L5_disk_internal', name='L4-L5 disk internal anatomy (schematic)', elements=['AR001', 'AR002']),
])
binary_path = ROOT / 'public/models/blender-additions.bin'
binary_path.write_bytes(blob)
with (ROOT / 'public/models/blender-additions.bin.gz').open('wb') as raw:
    with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as stream:
        stream.write(blob)
(ROOT / 'modeling/generated.json').write_text(json.dumps(dict(parts=parts, concepts=concepts,
    triangles=sum(p['indexCount'] // 3 for p in parts)), indent=2) + '\n')

# Inspectable render cameras for the disc and right knee.
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 64
scene.cycles.use_denoising = False
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.world.color = (.8, .8, .8)
scene.view_settings.view_transform = 'Standard'
for location, energy, size in [((0, -2, 3), 110, 2), ((1, 1, 2), 85, 2)]:
    light_data = bpy.data.lights.new('Softbox', 'AREA')
    light_data.energy, light_data.size = energy, size
    light = bpy.data.objects.new('Softbox', light_data)
    scene.collection.objects.link(light)
    light.location = location


def camera_at(name, atlas_center, direction, scale):
    center_b = Vector(to_blender([atlas_center])[0])
    direction_b = Vector(to_blender([direction])[0]).normalized()
    camera_data = bpy.data.cameras.new(name)
    camera_data.type, camera_data.ortho_scale = 'ORTHO', scale
    camera = bpy.data.objects.new(name, camera_data)
    scene.collection.objects.link(camera)
    camera.location = center_b + direction_b * .5
    camera.rotation_euler = (-direction_b).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = camera


camera_at('Right knee · anterior', [-.082, .43, .015], [0, .08, 1], .14)
scene.render.filepath = str(ROOT / 'modeling/knee-preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'modeling/atlas-additions.blend'))
bpy.ops.render.render(write_still=True)
camera_at('Disc · superior', center.tolist(), [0, 1, .15], .105)
for obj in context.objects:
    obj.hide_render = True
scene.render.filepath = str(ROOT / 'modeling/disc-preview.png')
bpy.ops.render.render(write_still=True)
for obj in context.objects:
    obj.hide_render = False
print('EXPORTED', len(parts), 'models', sum(p['indexCount'] // 3 for p in parts), 'triangles')
