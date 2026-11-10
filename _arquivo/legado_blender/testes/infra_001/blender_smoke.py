"""Run only in a dedicated background process, never in the artist session."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

out = Path(__file__).resolve().parent
if '--' in sys.argv:
    out = out / sys.argv[sys.argv.index('--')+1]
out.mkdir(parents=True, exist_ok=True)
for name in ('smoke.blend', 'smoke.png', 'blender_result.json'):
    if (out / name).exists():
        raise FileExistsError(out / name)
before = [o.name for o in bpy.context.scene.objects]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.object
cube.name = 'INFRA001_Cube'
mat = bpy.data.materials.new('INFRA001_Blue')
mat.diffuse_color = (0.05, 0.25, 0.65, 1)
mat.use_nodes = True
mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = mat.diffuse_color
cube.data.materials.append(mat)
bpy.ops.object.camera_add(location=(4, -6, 4))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 0)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type='AREA', location=(2, -3, 5))
bpy.context.object.data.energy = 800
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 4
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 8
scene.render.resolution_x = 144
scene.render.resolution_y = 256
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = str(out / 'smoke.png')
bpy.ops.wm.save_as_mainfile(filepath=str(out / 'smoke.blend'))
bpy.ops.render.render(write_still=True)
(out / 'blender_result.json').write_text(json.dumps(dict(version=bpy.app.version_string,
    before=before, after=[o.name for o in scene.objects], engine=scene.render.engine,
    size=[144,256], blend_exists=(out/'smoke.blend').is_file(),
    render_exists=(out/'smoke.png').is_file()), indent=2), encoding='utf-8')
print('INFRA001_BLENDER_PASS')
