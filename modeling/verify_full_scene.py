"""Verify the saved Blender assembly matches both exported catalogues exactly."""
import bpy
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
atlases = [json.loads((ROOT / 'public/models' / name).read_text())
           for name in ['atlas-source.json', 'atlas.json']]
lookup = {p['id']: (p, atlas) for atlas in atlases for p in atlas['parts']}
seen = set()
failures=[]
bpy.context.view_layer.update()
for obj in bpy.data.objects:
    pid = obj.get('atlas_id') or obj.get('id')
    if not pid or pid not in lookup: continue
    part, atlas = lookup[pid]
    assert obj.type == 'MESH'
    mesh = obj.data
    mesh.calc_loop_triangles()
    assert len(mesh.vertices) == part['vertexCount'], pid
    assert len(mesh.loop_triangles) * 3 == part['indexCount'], pid
    raw = (ROOT / 'public' / atlas['chunks'][part['chunk']]['url'].lstrip('/')).read_bytes()
    expected = np.frombuffer(raw, '<f4', part['vertexCount']*3, part['positions']).reshape(-1, 3)
    coords = np.empty(part['vertexCount']*3, dtype=float)
    mesh.vertices.foreach_get('co', coords)
    m = np.array(obj.matrix_world)
    actual = coords.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]
    actual = np.column_stack((actual[:, 0], actual[:, 2], -actual[:, 1]))
    error = float(np.abs(actual - expected).max())
    if error >= 5e-7: failures.append((pid, error))
    assert pid not in seen
    seen.add(pid)
assert not failures, f'Saved-coordinate differences: {sorted(failures,key=lambda p:-p[1])[:20]} ({len(failures)} objects)'
assert len(seen) == 5249, len(seen)
assert set(lookup) == seen
assert len(bpy.context.scene.view_layers) == 2
assert len([i for i in bpy.data.images if i.packed_file]) >= 3
print('VERIFIED SAVED SCENE',len(seen),'editable objects; every source and existing vertex position preserved')
