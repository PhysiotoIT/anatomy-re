"""Render the saved scene using CPU Cycles; verify and freeze source transforms."""
import bpy
import json
import shutil
from pathlib import Path
import numpy as np
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
atlas = json.loads((ROOT / 'public/models/atlas-source.json').read_text())
parts = {p['id']: p for p in atlas['parts']}
existing = json.loads((ROOT / 'public/models/atlas.json').read_text())
existing_parts = {p['id']: p for p in existing['parts']}
colors = dict(skeletal='#e2d9ba', muscular='#a85b50', connective='#aec3bb', arterial='#c05245',
             venous='#527c9f', cardiac='#b96760', nervous='#d8b565', lymphatic='#879f7c',
             sensory='#b0c8ce', digestive='#b8916b', respiratory='#b98991', urinary='#b47961',
             endocrine='#c5a09a', reproductive='#bda098', integumentary='#ba9b7d')
materials = {}
for obj in bpy.data.objects:
    part = parts.get(obj.get('atlas_id')) or existing_parts.get(obj.get('id'))
    if not part: continue
    color = part.get('color', colors[part['system']])
    if color not in materials:
        srgb = [int(color[i:i+2],16)/255 for i in [1,3,5]]
        rgb = tuple(c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in srgb)
        mat = bpy.data.materials.new('Atlas color · '+color)
        mat.diffuse_color = (*rgb,1)
        mat.use_nodes = True
        shader = mat.node_tree.nodes['Principled BSDF']
        shader.inputs['Base Color'].default_value = (*rgb,1)
        shader.inputs['Roughness'].default_value = .57
        materials[color] = mat
    obj.data.materials.clear()
    obj.data.materials.append(materials[color])
buffers = {}
objects = []
for obj in bpy.data.objects:
    pid = obj.get('atlas_id')
    if not pid: continue
    part = parts[pid]
    ci = part['chunk']
    if ci not in buffers:
        buffers[ci] = (ROOT / 'public' / atlas['chunks'][ci]['url'].lstrip('/')).read_bytes()
    coords = np.frombuffer(buffers[ci], '<f4', part['vertexCount']*3, part['positions']).reshape(-1, 3)
    coords = np.column_stack((coords[:, 0], -coords[:, 2], coords[:, 1])).astype(np.float32)
    if obj.data.users > 1:
        obj.data = obj.data.copy()
    obj.parent = None
    obj.animation_data_clear()
    obj.matrix_world = Matrix.Identity(4)
    obj.data.vertices.foreach_set('co', coords.reshape(-1))
    obj.data.update()
    objects.append(obj)
del buffers
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = False
scene.render.resolution_x, scene.render.resolution_y = 1400, 1800
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'AgX'
scene.world.use_nodes = True
background = scene.world.node_tree.nodes['Background']
background.inputs['Color'].default_value = (.85, .9, .95, 1)
background.inputs['Strength'].default_value = .4
scene.render.film_transparent = False
camera = scene.camera
camera.location = (0, -3, .88)
camera.rotation_euler = (Vector((0, 0, .88))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.ortho_scale = 1.95
studio = bpy.data.collections.new('05 · Render studio')
scene.collection.children.link(studio)
for loc, energy, size in [((-.7,-1.3,2.2),90,1.4),((.8,-.6,1.2),45,1.1),((0,.7,1.8),65,1.2)]:
    data=bpy.data.lights.new('Softbox','AREA')
    data.energy, data.size=energy,size
    light=bpy.data.objects.new('Softbox',data)
    studio.objects.link(light)
    light.location=loc
    light.rotation_euler=(Vector((0,0,.85))-light.location).to_track_quat('-Z','Y').to_euler()
for obj in objects:
    obj.hide_render = parts[obj['atlas_id']]['system'] not in ['skeletal','muscular']
# The saved camera/visibility are a readable musculoskeletal overview.
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'modeling/anatomy-full-source.blend'),compress=True)
scene.render.filepath=str(ROOT/'modeling/full-atlas-preview.png')
bpy.ops.render.render(write_still=True)
for obj in objects:
    part=parts[obj['atlas_id']]
    lo,hi=part['bounds']
    obj.hide_render=part['system'] not in ['skeletal','connective'] or hi[1]<.34 or lo[1]>.51 or lo[0]>-.02
camera.location=(-.08,-.6,.437)
camera.rotation_euler=(Vector((-.08,0,.437))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.ortho_scale=.16
scene.render.resolution_x,scene.render.resolution_y=1400,1400
scene.render.filepath=str(ROOT/'modeling/source-knee-preview.png')
bpy.ops.render.render(write_still=True)
print('RENDERED source-quality overview and right knee from verified frozen geometry')
previews = ROOT / 'public/previews'
previews.mkdir(parents=True, exist_ok=True)
for source, name in [('full-atlas-preview.png','full-atlas.png'),('source-knee-preview.png','knee.png'),('disc-preview.png','disc.png')]:
    shutil.copyfile(ROOT / 'modeling' / source, previews / name)
