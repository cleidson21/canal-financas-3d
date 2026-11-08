"""Build the controlled S03 rig experiment from the delivered scene. No render."""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts')]
sys.dont_write_bytecode = True
from scripts.producao import motions as m
from pipeline_v3.anim_character import _set_facial_expression
from pipeline_v3.config import EP001_DIR

TESTS = EP001_DIR / 'TESTES'
SOURCE = EP001_DIR / 'ENTREGAS/CENA03_EDITAVEL.blend'
FPS, FRAMES = 24, 84
CONTACT = 41


def object_named(name):
    return bpy.data.objects[name]


def mesh_data(obj, basis):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    matrix = basis @ evaluated.matrix_world
    return ([matrix @ v.co for v in evaluated.data.vertices],
            [tuple(p.vertices) for p in evaluated.data.polygons])


def camera(scene, name, basis, position, aim, scale):
    data = bpy.data.cameras.new(name)
    data.type, data.ortho_scale = 'ORTHO', scale
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = basis @ Vector(position)
    obj.rotation_euler = (basis @ Vector(aim) - obj.location).to_track_quat('-Z', 'Y').to_euler()
    return obj


def set_arm(side, goal, basis, variant, previous):
    upper, elbow, palm = (object_named(f'Nico_{name}_{side}') for name in ('Arm', 'Forearm', 'Mao_Palma'))
    if variant == 'antes':
        m.aim_chain(upper, elbow, palm, basis @ goal)
    else:
        sign = 1 if side == 'R' else -1
        return m.pose_arm(upper, elbow, palm, basis @ goal, (sign*.65, .72, -.18), previous)


def pose(frame, basis, variant, previous):
    t = (frame-1) / FPS
    target = m.track(t, [
        (0, (.345, -.052, .782)), (.50, (.345, -.052, .782)),
        (.83, (.365, -.10, .865)), (1.17, (.40, -.23, 1.07)),
        (1.67, (.40, -.405, 1.00)), (1.80, (.40, -.405, 1.00)),
        (2.06, (.40, -.40, 1.115)), (2.42, (.403, -.21, 1.125)),
        (3.18, (.365, -.075, .83)), (3.50, (.365, -.075, .83)),
    ])
    left = m.track(t, [(0, (-.34,-.05,.782)), (1.75, (-.355,-.055,.795)), (3.25, (-.34,-.05,.782))])
    for side, hand in (('R',target),('L',left)):
        previous[side] = set_arm(side, hand, basis, variant, previous.get(side))
    head = object_named('Nico_Head')
    head.rotation_mode = 'XYZ'
    head.rotation_euler = m.track(t, [(0,(.02,0,.02)),(.52,(.22,-.04,.21)),(1.55,(.31,-.04,.20)),
                                     (2.22,(.17,-.03,.14)),(2.8,(.065,0,.03)),(3.4,(.05,0,.015))])
    bpy.context.view_layer.update()
    return basis @ target


def make_stage():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False)
    scene = bpy.context.scene
    scene.frame_set(118)
    nico = object_named('Nico_Root')
    visible = {nico, *nico.children_recursive, object_named('Chao_Grama_Principal')}
    counter, potato = object_named('pescador_counter'), object_named('Troca_potatoes0')
    visible.update((counter, potato))
    for obj in scene.objects:
        if obj.type == 'LIGHT' and obj.name in {'Sol_Principal','Luz_Preenchimento','Luz_Recorte_Rim'}:
            visible.add(obj)
        if obj in visible and obj.animation_data:
            obj.animation_data_clear()
        obj.hide_render = obj not in visible
        obj.hide_set(obj not in visible)
    scene.sequence_editor_clear()
    for sound in list(bpy.data.sounds):
        bpy.data.sounds.remove(sound)
    scene.timeline_markers.clear()
    object_named('Nico_Sola_Descolada_Pivot_R').rotation_euler.x = 0
    object_named('Nico_Tenis_SolaFrontal_R').rotation_euler.x = 0
    bpy.context.view_layer.update()
    soles = [object_named('Nico_Tenis_Sola_L'), object_named('Nico_Tenis_SolaTraseira_R'),
             object_named('Nico_Tenis_SolaFrontal_R')]
    floor = max(v.z for v in mesh_data(object_named('Chao_Grama_Principal'), nico.matrix_world.inverted())[0])
    soles_min = min(v.z for obj in soles for v in mesh_data(obj,nico.matrix_world.inverted())[0])
    nico.location.z += floor - soles_min
    bpy.context.view_layer.update()
    basis = nico.matrix_world.copy()
    for obj, pos in ((counter, (.49,-.68,.835)), (potato, (.25,-.45,.965))):
        obj.parent = None
        obj.matrix_world = basis @ obj.matrix_basis
        obj.location = basis @ Vector(pos)
    counter.scale.x *= .46
    for side, x in (('L',.18),('R',.80)):
        leg = counter.copy()
        leg.name = 'ANIM003_Suporte_Balcao_' + side
        scene.collection.objects.link(leg)
        leg.location = basis @ Vector((x,-.80,.38))
        leg.scale.x *= .12
        leg.scale.y *= .17
        leg.scale.z *= .77/.13
    bpy.context.view_layer.update()
    # Place the prop on the measured surface of the reused counter.
    inverse = basis.inverted()
    top = max(v.z for v in mesh_data(counter, inverse)[0])
    bottom = min(v.z for v in mesh_data(potato, inverse)[0])
    potato.location += basis.to_3x3() @ Vector((0,0,top-bottom))
    bpy.context.view_layer.update()
    scene.camera = camera(scene,'ANIM003_Corpo',basis,(-1.55,-5.20,2.25),(.08,-.10,.91),2.19)
    camera(scene,'ANIM003_Lateral',basis,(4.8,-.92,1.74),(.09,-.14,.94),2.19)
    scene.frame_start, scene.frame_end = 1, FRAMES
    scene.render.fps, scene.render.fps_base = FPS, 1
    scene.render.resolution_x, scene.render.resolution_y = 216,384
    scene.render.resolution_percentage = 100
    scene.render.use_sequencer = False
    for frame, name in ((1,'Repouso'),(14,'Olhar'),(29,'Alcance'),(CONTACT,'Contato'),
                        (50,'Retirada'),(76,'Acomodacao')):
        scene.timeline_markers.new(name,frame=frame)
    return scene, basis, potato, soles, counter, top


def contact_distance(obj, hands, basis):
    verts, polygons = mesh_data(obj, basis)
    surface = BVHTree.FromPolygons(verts,polygons)
    best = float('inf')
    overlap = False
    for hand in hands:
        hverts, hfaces = mesh_data(hand,basis)
        overlap |= bool(surface.overlap(BVHTree.FromPolygons(hverts,hfaces)))
        best = min(best, min(surface.find_nearest(v)[3] for v in hverts))
    return best, overlap


def run(output, variant):
    scene, basis, potato, soles, counter, top = make_stage()
    palm = object_named('Nico_Mao_Palma_R')
    thumb = object_named('Nico_Mao_Polegar_R')
    # Set the initial potato against the contact surface of the corrected hand.
    # Both versions use the same bench, prop placement, hand target and cameras.
    pose(CONTACT,basis,'depois',{})
    start = potato.location.copy()
    for i in range(101):
        potato.location = start + basis.to_3x3() @ Vector((i*.001,0,0))
        bpy.context.view_layer.update()
        gap, overlap = contact_distance(potato,(palm,thumb),basis.inverted())
        if gap < .004 and not overlap:
            break
    else:
        raise RuntimeError('Could not seat potato against the hand')
    potato.rotation_mode = 'QUATERNION'
    grounded = potato.matrix_world.copy()
    grip = None
    previous = {}
    rows = []
    for frame in range(1,FRAMES+1):
        scene.frame_set(frame)
        requested = pose(frame,basis,variant,previous)
        if frame == CONTACT:
            grip = palm.matrix_world.inverted() @ grounded
        potato.matrix_world = grounded if frame < CONTACT else palm.matrix_world @ grip
        for side in ('L','R'):
            for control in ('Arm','Forearm'):
                m.key(object_named(f'Nico_{control}_{side}'),frame,'rotation_quaternion')
        for prop in ('location','rotation_quaternion'):
            m.key(potato,frame,prop)
        m.key(object_named('Nico_Head'),frame,'rotation_euler')
        bpy.context.view_layer.update()
        rows.append(dict(frame=frame,target_error=(palm.matrix_world.translation-requested).length))
    m.finalize_curves(scene.objects)
    face = {key: object_named(name) for key,name in (
        ('eyebrow_l','Nico_Sobrancelha_L'), ('eyebrow_r','Nico_Sobrancelha_R'), ('mouth','Nico_Boca'))}
    for frame,state in ((1,'neutral'),(14,'neutral'),(32,'effort'),(44,'effort'),
                        (65,'happy_idea'),(84,'neutral')):
        _set_facial_expression(face,frame,state)
    if variant=='depois':
        scene['ANIM003'] = 'Polo em espaco do tronco, controles Empty e skin V3 preservados'
    scene['ANIM003_variant'] = variant
    scene['ANIM003_source'] = SOURCE.relative_to(ROOT).as_posix()
    scene['ANIM003_contact_frame'] = CONTACT
    scene['ANIM003_counter_height'] = top
    scene['ANIM003_target_max_error'] = max(r['target_error'] for r in rows)
    scene.frame_set(1)
    bpy.context.preferences.filepaths.file_preview_type = 'NONE'
    bpy.ops.wm.save_as_mainfile(filepath=str(output), relative_remap=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('variant',choices=('antes','depois'))
    parser.add_argument('output',type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    path = args.output.resolve()
    if not path.is_relative_to(TESTS) or path.suffix != '.blend' or path.exists():
        raise ValueError('Choose a new .blend inside TESTES')
    run(path,args.variant)
