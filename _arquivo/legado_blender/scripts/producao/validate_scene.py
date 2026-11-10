"""Read-only structural/contact/foot-support regression for a saved proof scene."""
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from pipeline_v3.scene_setup import iter_object_fcurves

def main(spec, scene_path=None):
    out = ROOT / spec['output']
    bpy.ops.wm.open_mainfile(filepath=str(scene_path or out / spec['scene_file']), load_ui=False)
    scene=bpy.context.scene;errors=[];contacts=[]
    expected=[('potatoes',3.9,'Nico_Mao_Palma_R','pescador_Palm_L',(.075,0,.11),(-.075,0,.11)),('fish',5.9,'pescador_Palm_R','Nico_Mao_Palma_R',(-.075,0,.115),(.075,0,.115)),('fish_to_lumberjack',8.9,'Nico_Mao_Palma_R','lenhador_Palm_L',(.075,0,.115),(-.075,0,.115)),('wood',10.4,'lenhador_Palm_R','Nico_Mao_Palma_R',(-.075,0,.115),(.075,0,.115))]
    for name,t,giver,receiver,go,ro in expected:
        scene.frame_set(round(t*30)+1);bpy.context.view_layer.update()
        g=bpy.data.objects[giver].matrix_world.translation;r=bpy.data.objects[receiver].matrix_world.translation
        prop=bpy.data.objects['Troca_'+('fish' if name=='fish_to_lumberjack' else name)]
        agreement=(g+Vector(go)-r-Vector(ro)).length
        offset_error=(prop.location-r-Vector(ro)).length
        row=dict(event=name,time=t,support_center_agreement_m=agreement,receiver_offset_error_m=offset_error,palm_separation_m=(g-r).length)
        contacts.append(row)
        if agreement>.005 or offset_error>.005 or (g-r).length<.11:errors.append('handoff '+name)
    previous={};prop_steps=[];planted={s:[] for s in ('L','R')};cuts={x.frame for x in scene.timeline_markers};bbox_collisions=[];body_distances=[]
    for frame in range(1,scene.frame_end+1):
        scene.frame_set(frame);bpy.context.view_layer.update();t=(frame-1)/30
        nr=bpy.data.objects['Nico_Root'].matrix_world.translation
        for role in ('pescador','lenhador'):
            mr=bpy.data.objects['Comerciante_'+role].matrix_world.translation
            body_distances.append(((nr.x-mr.x)**2+(nr.y-mr.y)**2)**.5)
        for name in ('potatoes','fish','wood'):
            ob=bpy.data.objects['Troca_'+name];position=ob.matrix_world.translation.copy()
            if ob.hide_render:errors.append('hidden trade object '+name)
            if name in previous and frame not in cuts:prop_steps.append((position-previous[name]).length)
            previous[name]=position
        bounds={}
        for name in ('potatoes','fish','wood'):
            ob=bpy.data.objects['Troca_'+name]
            points=[part.matrix_world@Vector(v) for part in ob.children_recursive if part.type=='MESH' for v in part.bound_box]
            bounds[name]=([min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)])
        for left,right in (('potatoes','fish'),('fish','wood'),('potatoes','wood')):
            a,b=bounds[left];c,d=bounds[right]
            if all(min(b[i],d[i])-max(a[i],c[i])>.005 for i in range(3)):bbox_collisions.append(dict(frame=frame,pair=[left,right]))
        if t>=7.5:
            for side in planted:planted[side].append(bpy.data.objects['Nico_Foot_'+side].matrix_world.translation.copy())
    drift={s:max((p-planted[s][0]).length for p in planted[s]) for s in planted}
    if max(drift.values())>.003:errors.append('planted feet drift')
    max_step=max(prop_steps)
    if max_step>.085:errors.append('unexplained prop jump')
    for side in ('L','R'):
        ob=bpy.data.objects['Nico_Arm_'+side]
        if not any(len(fc.keyframe_points)>=scene.frame_end for fc in iter_object_fcurves(ob)):errors.append('missing dense temporal arm animation')
    rig=bpy.data.objects.get('Nico_Armature_V3')
    if not rig or not rig.pose.bones:errors.append('original Nico armature missing')
    if len(scene.timeline_markers)!=9:errors.append('camera shot count')
    for category,stem in [('personagens','comerciantes'),('cenarios','barracas'),('objetos','mercadorias')]:
        path=ROOT/category/(stem+'_PROD002_V2.blend')
        with bpy.data.libraries.load(str(path),link=False) as (source,dest):
            if len(source.collections)<1:errors.append('empty shared library '+stem)
    if bbox_collisions:errors.append('trade-goods bounding boxes overlap; inspect physical separation')
    if min(body_distances)<.55:errors.append('characters too close along travel path')
    result=dict(errors=errors,contacts=contacts,max_prop_step_m_except_cuts=max_step,trade_goods_bbox_overlaps=bbox_collisions,planted_foot_drift_m=drift,frames=scene.frame_end,fps=scene.render.fps,resolution=[scene.render.resolution_x,scene.render.resolution_y],camera_shots=len(scene.timeline_markers),nico_rig_preserved=bool(rig),human_approval=False)
    result['minimum_character_root_distance_xy_m'] = min(body_distances)
    evidence = out / 'testes'
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / 'validacao_3d.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print('VALIDATION',json.dumps(result))
    if errors:raise AssertionError(errors)

if __name__=='__main__':
    args = sys.argv[sys.argv.index('--') + 1:]
    spec = json.loads((ROOT / args[0]).read_text(encoding='utf-8'))
    main(spec, ROOT / args[1] if len(args) > 1 else None)
