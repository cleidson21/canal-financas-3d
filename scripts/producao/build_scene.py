"""Build the two-trade proof from a scene spec, reusing original Nico and village.

Run in a dedicated Blender process. All disk writes are new versioned libraries
and the explicit scene output; the source .blend is never saved.
"""
import argparse
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from scripts.producao import assets as a, motions as m, cameras
from pipeline_v3 import scene_setup
from pipeline_v3.anim_character import _set_facial_expression


def nico_actor():
    get=lambda n:bpy.data.objects['Nico_'+n]
    actor=dict(root=get('Root'),torso=get('Torso'),head=get('Head'),pelvis=get('Pelvis'),
        arms={s:(get('Arm_'+s),get('Forearm_'+s)) for s in ('L','R')},
        palms={s:get('Mao_Palma_'+s) for s in ('L','R')},
        legs={s:(get('Leg_'+s),get('Knee_'+s),get('Foot_'+s)) for s in ('L','R')})
    actor['root'].rotation_euler=(0,0,0);actor['pelvis'].location=(0,0,.78);actor['pelvis'].rotation_euler=(0,0,0)
    actor['torso'].location=(0,0,.07);actor['torso'].rotation_euler=(0,0,0)
    actor['head'].location=(0,0,.55);actor['head'].rotation_euler=(0,0,0)
    for side,sign in (('L',-1),('R',1)):
        up,lo=actor['arms'][side];up.location=(sign*.28,0,.45);lo.location=(sign*.02,0,-.26)
        leg,knee,foot=actor['legs'][side];leg.location=(sign*.14,0,0);knee.location=(0,0,-.36);foot.location=(0,0,-.30)
        for ob in (up,lo,leg,knee,foot):ob.rotation_euler=(0,0,0)
    get('Tenis_SolaFrontal_R').rotation_euler=(math.radians(12),0,0)
    return actor

def face(actor,frame,t):
    objs={k:bpy.data.objects[v] for k,v in dict(eyebrow_l='Nico_Sobrancelha_L',eyebrow_r='Nico_Sobrancelha_R',mouth='Nico_Boca').items()}
    state='happy_idea' if t>.65 else 'neutral'
    if 11.6<t<12.3:state='surprised'
    _set_facial_expression(objs,frame,state)
    # Interpolated eyebrow asymmetry during the suspiciously easy success.
    if 12.3<t<15.7:
        ob=objs['eyebrow_l'];ob.rotation_euler.y+=.16*math.sin((t-12.3)/3.4*math.pi);m.key(ob,frame,'rotation_euler')
    blink=1.0
    for center in (.72,4.60,8.15,12.05,16.85):
        blink=min(blink,1-.92*max(0,1-abs(t-center)/.09))
    for side,sign in (('L',-1),('R',1)):
        for part in ('Olho_Branco','Pupila','Brilho_Olho','Brilho_Sec'):
            ob=bpy.data.objects['Nico_'+part+'_'+side]
            ob.scale.z=blink;m.key(ob,frame,'scale')
            if part in ('Brilho_Olho','Brilho_Sec'):
                z=.284 if part=='Brilho_Olho' else .254
                ob.location.z=.268+(z-.268)*blink;m.key(ob,frame,'location')

def foot_pose(nico,frame,t,prior_rotations):
    root=nico['root'];start=6.7;end=7.48
    max_error=0
    for side,sign in (('L',-1),('R',1)):
        # Planted feet keep world-space support points while the body turns.
        stance_x=-.4 if t<7.5 else 2.17
        angle=math.radians(50)
        initial=Vector((stance_x+sign*.14*math.cos(angle),-.10+sign*.14*math.sin(angle),.12))
        ankle=initial.copy()
        if start<=t<end:
            dt=(end-start)/4;step=min(3,int((t-start)/dt));u=(t-start-step*dt)/dt
            latest=step if (step%2==0)==(side=='L') else step-1
            if latest>=0:
                previous=-.4+(latest-1)*.18+sign*.14*math.cos(angle) if latest>=2 else initial.x
                target=-.4+(latest+1)*.18+sign*.14*math.cos(angle)
                previous_y=-.10-(latest-1)*.1375+sign*.14*math.sin(angle) if latest>=2 else initial.y
                target_y=-.10-(latest+1)*.1375+sign*.14*math.sin(angle)
                progress=m.smooth(u) if latest==step else 1
                ankle.x=previous+(target-previous)*progress
                ankle.y=previous_y+(target_y-previous_y)*progress
                ankle.z=.12+(.09*math.sin(u*math.pi) if latest==step else 0)
            else:ankle=initial.copy()
        leg,knee,foot=nico['legs'][side]
        error=m.aim_chain(leg,knee,foot,ankle,bend=(.35,-.7,0),previous=prior_rotations.get(leg.name),evaluate=False)
        leg_rotation,knee_rotation=leg.rotation_quaternion.copy(),knee.rotation_quaternion.copy()
        prior_rotations[leg.name]=(leg_rotation,knee_rotation)
        max_error=max(max_error,error)
        m.key(leg,frame,'rotation_quaternion');m.key(knee,frame,'rotation_quaternion')
        parent_rotation=leg.parent.matrix_world.to_quaternion() @ leg_rotation @ knee_rotation
        rotation=parent_rotation.inverted() @ root.matrix_world.to_quaternion()
        if foot.name in prior_rotations:rotation.make_compatible(prior_rotations[foot.name])
        prior_rotations[foot.name]=rotation.copy()
        foot.rotation_mode='QUATERNION';foot.rotation_quaternion=rotation
        m.key(foot,frame,'rotation_quaternion')
        if side=='R':
            sole=bpy.data.objects['Nico_Tenis_SolaFrontal_R']
            sole.rotation_euler.x=.06+max(0,ankle.z-.12)*3
            m.key(sole,frame,'rotation_euler')
    return max_error

def pose_scene(scene,nico,fisher,lumber,props,spec):
    errors=[];frames=scene.frame_end
    arm_solver = spec.get('nico_arm_solver', 'legacy')
    if arm_solver not in ('legacy', 'anatomical'):
        raise ValueError('Unknown Nico arm solver')
    previous = {}
    # Fixed world-space contact points shared by giver and receiver.
    potato_contact=(-.02,-.10,1.08);fish_contact=(.21,-.10,1.18)
    lumber_contact=(2.58,-.07,1.10);wood_contact=(2.71,-.10,1.09)
    left=lambda v:tuple(Vector(v)+Vector((-.075,0,0)))
    right=lambda v:tuple(Vector(v)+Vector((.075,0,0)))
    for frame in range(1,frames+1):
        scene.frame_set(frame);t=(frame-1)/30
        if t<6.7:x=-.4
        elif t<7.5:x=-.4+.60*m.smooth((t-6.7)/.78)
        else:x=2.17
        yaw=math.radians(50)
        if t>10.8:yaw=math.radians(50)*(1-m.smooth((t-10.8)/.8))
        y=-.10-.55*m.smooth((t-6.7)/.78) if 6.7<=t<7.5 else -.10
        nico['root'].location=(x,y,0);nico['root'].rotation_euler=(0,0,yaw)
        m.key(nico['root'],frame,'location');m.key(nico['root'],frame,'rotation_euler')
        walk_weight=m.smooth((t-6.55)/.15)*(1-m.smooth((t-7.35)/.15))
        nico['pelvis'].location.z=.755+.003*math.sin(t*2.8)-.045*walk_weight+.01*math.sin((t-6.7)/.195*math.pi)*walk_weight
        m.key(nico['pelvis'],frame,'location')
        nico['torso'].rotation_euler=(m.track(t,[(0,(.08,0,0)),(.45,(.16,0,0)),(.95,(-.06,0,0)),(1.6,(0,0,0)),(10.7,(0,0,0)),(11.4,(-.10,0,-.04)),(12.0,(-.04,0,.06)),(12.6,(-.10,0,0)),(15.5,(-.10,0,0)),(16.1,(-.02,0,.04)),(16.8,(-.10,0,-.03)),(17.5,(-.06,0,0))]))
        m.key(nico['torso'],frame,'rotation_euler')
        nico['head'].rotation_euler=m.track(t,[(0,(.06,0,0)),(.4,(.32,0,-.1)),(.9,(-.10,0,.18)),(1.5,(0,0,.25)),(2.4,(0,0,.12)),(6.5,(0,0,.12)),(7.5,(0,0,.12)),(10.5,(0,0,.12)),(11.1,(-.12,0,0)),(11.9,(.05,0,-.25)),(12.5,(-.16,0,0)),(15.2,(-.16,0,.10)),(16.1,(.06,0,0)),(16.6,(-.13,0,0)),(17.5,(-.08,0,0))])
        m.key(nico['head'],frame,'rotation_euler');face(nico,frame,t)
        # Merchants inspect, nod acceptance, then recover. No icon substitutes.
        for actor,begin in ((fisher,2.8),(lumber,8.0)):
            phase=(t-begin)
            nod=.15*math.sin(max(0,min(1,phase/1.2))*math.tau) if 0<phase<1.2 else 0
            actor['head'].rotation_euler=(nod,0,.12 if actor==fisher else -.10)
            actor['torso'].rotation_euler.x=.07*math.sin(max(0,min(1,phase/1.1))*math.pi) if 0<phase<1.1 else .015*math.sin(t*2)
            m.key(actor['head'],frame,'rotation_euler');m.key(actor['torso'],frame,'rotation_euler')
            for brow in actor['eyebrows']:
                brow.location.z=.32+.015*max(0,math.sin(phase*3)) if 0<phase<1.3 else .32
                m.key(brow,frame,'location')
        bpy.context.view_layer.update()
        base=nico['root'].matrix_world
        nr=base@Vector((.26,-.30,1.04));nl=base@Vector((-.26,-.20,1.03))
        if t<6.7:
            nr=m.track(t,[(0,(-.32,-.35,1.03)),(2.4,(-.32,-.35,1.03)),(3.9,left(potato_contact)),(4.15,left(potato_contact)),(4.6,(-.22,-.30,1.08)),(5.9,left(fish_contact)),(6.12,left(fish_contact)),(6.55,(-.27,-.32,1.07))])
            nl=m.track(t,[(0,tuple(nl)),(.9,tuple(nl)),(1.45,(-.13,-.35,1.47)),(1.8,(-.13,-.35,1.47)),(2.3,tuple(nl))])
        elif t<7.5:
            nr=Vector((x+.13,y-.22,1.07))
            nl=Vector((x-.014,y-.328+.04*math.sin((t-6.7)*math.tau/.39),1.03))
        else:
            nr=m.track(t,[(7.5,(2.30,-.34,1.08)),(8.9,left(lumber_contact)),(9.10,left(lumber_contact)),(9.45,(2.32,-.32,1.08)),(10.4,left(wood_contact)),(10.60,left(wood_contact)),(11.15,(2.40,-.34,1.07)),(12.0,(2.40,-.34,1.07)),(17.52,(2.40,-.34,1.07))])
            if t>11:
                nl=m.track(t,[(11,tuple(nl)),(11.6,(1.87,-.25,1.30)),(12.2,(1.87,-.25,1.30)),(13.0,(1.83,-.12,1.12)),(15.4,(1.83,-.12,1.12)),(16.1,(1.88,-.28,1.40)),(16.8,(1.91,-.3,1.20)),(17.52,(1.9,-.25,1.10))])
        # Hands occupy opposite sides of each item, never the same palm volume.
        fl=m.track(t,[(0,(.23,-.13,1.06)),(2.8,(.23,-.13,1.06)),(3.9,tuple(Vector(potato_contact)+Vector((.075,0,0)))),(4.15,tuple(Vector(potato_contact)+Vector((.075,0,0)))),(4.65,(.12,.24,1.02))])
        fr=m.track(t,[(0,(.62,-.14,1.07)),(4.55,(.62,-.14,1.07)),(5.9,right(fish_contact)),(6.12,right(fish_contact)),(6.55,(.62,-.14,1.07))])
        ll=m.track(t,[(0,(2.80,-.10,1.08)),(8.15,(2.80,-.10,1.08)),(8.9,right(lumber_contact)),(9.1,right(lumber_contact)),(9.65,(2.63,.30,1.02))])
        lr=m.track(t,[(0,(3.25,-.15,1.10)),(9.45,(3.25,-.15,1.10)),(10.4,right(wood_contact)),(10.6,right(wood_contact)),(11.1,(3.25,-.15,1.10))])
        local_errors=[]
        for actor,side,target in ((nico,'R',nr),(nico,'L',nl),(fisher,'L',fl),(fisher,'R',fr),(lumber,'L',ll),(lumber,'R',lr)):
            pole = m.nico_elbow_pole(side) if actor is nico and arm_solver == 'anatomical' else None
            error=m.hand(actor,side,target,frame,pole=pole,previous=previous,evaluate=False)
            local_errors.append(error)
        feet_error=foot_pose(nico,frame,t,previous)
        bpy.context.view_layer.update()
        m.bind_transfer(props['potatoes'],frame,nico['palms']['R'],fisher['palms']['L'],round(3.9*30)+1,giver_offset=(.075,0,.11),receiver_offset=(-.075,0,.11))
        if t<8.9:m.bind_transfer(props['fish'],frame,fisher['palms']['R'],nico['palms']['R'],round(5.9*30)+1,giver_offset=(-.075,0,.115),receiver_offset=(.075,0,.115))
        else:m.bind_transfer(props['fish'],frame,nico['palms']['R'],lumber['palms']['L'],round(8.9*30)+1,giver_offset=(.075,0,.115),receiver_offset=(-.075,0,.115))
        m.bind_transfer(props['wood'],frame,lumber['palms']['R'],nico['palms']['R'],round(10.4*30)+1,giver_offset=(-.075,0,.115),receiver_offset=(.075,0,.115))
        errors.append(dict(frame=frame,hand_target_error_max=max(local_errors),
                           nico_hand_target_error_max=max(local_errors[:2]),foot_target_error_max=feet_error))
    m.finalize_curves(bpy.context.scene.objects)
    return errors

def build(spec_path):
    spec=json.loads(spec_path.read_text(encoding='utf-8'));out=ROOT/spec['output'];out.mkdir(parents=True, exist_ok=True)
    if spec['story']!='two_trades' or spec['episode']!='EP001_dinheiro' or spec['segment']!='S03':
        raise ValueError('This proof builder supports EP001/S03 only. Compose another scene with the shared API after human approval.')
    if spec['handoffs_seconds']!={'potatoes':3.9,'fish':5.9,'fish_to_lumberjack':8.9,'wood':10.4}:
        raise ValueError('Changing handoff cues requires reviewing the acting curves; metadata alone cannot retime this proof.')
    dest=out/spec['scene_file']
    if dest.exists():raise FileExistsError(dest)
    timing=json.loads((ROOT/spec['timing']).read_text(encoding='utf-8'));segment=next(s for s in timing['segmentos'] if s['id']==spec['segment'])
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/spec['nico_source']),load_ui=False)
    # Work around the observed save-thumbnail path failure in this process only.
    # Never save user preferences or change the global Blender configuration.
    bpy.context.preferences.filepaths.file_preview_type='NONE'
    scene=bpy.context.scene
    for ob in list(bpy.data.objects):
        ob.animation_data_clear()
        if ob.data and hasattr(ob.data,'animation_data_clear'):ob.data.animation_data_clear()
    head_source=[ob for ob in bpy.data.objects if ob.parent and ob.parent.name=='Vendedor_Head']
    actors={kind:a.merchant(kind,head_source) for kind in spec['stalls']}
    stalls={kind:a.stall(kind) for kind in spec['stalls']}
    propcol=a.collection('Mercadorias_PROD002');props={kind:a.goods(kind,propcol,'Troca_'+kind) for kind in spec['goods']}
    # Export neutral library datablocks before adding episode poses.
    a.write_library(ROOT/'personagens/comerciantes_PROD002_V2.blend',[x['col'] for x in actors.values()])
    a.write_library(ROOT/'cenarios/barracas_PROD002_V2.blend',[x[0] for x in stalls.values()])
    a.write_library(ROOT/'objetos/mercadorias_PROD002_V2.blend',[propcol])
    # Remove obsolete foreground from this in-memory copy only. Keep Nico/village/lights.
    obsolete=[ob for ob in list(bpy.data.objects) if ob.name.startswith(('Vendedor_','Saco_','Carrinho_','Placa_','Par_Sapatos_','Selo_','Carimbo_')) or any(c.name=='Col_Feira_Barraca' for c in ob.users_collection)]
    # New merchant names are prefixed by their role, so they are not selected above.
    obsolete=set(obsolete).union(*(set(ob.children_recursive) for ob in obsolete))
    for ob in obsolete:bpy.data.objects.remove(ob,do_unlink=True)
    for ob in bpy.data.objects:
        if ob.name.startswith('Nico_'):ob.hide_render=False
    nico=nico_actor()
    for kind,x in (('pescador',.43),('lenhador',3.0),('leiteiro',6.0)):
        stalls[kind][1].location=(x,.75,0)
        actors[kind]['root'].location=(x-(.10 if kind=='lenhador' else 0),-.02,0);actors[kind]['root'].rotation_euler.z=math.radians(-40)
    scene_setup.configure_scene_and_render(scene)
    scene.render.resolution_x,scene.render.resolution_y=spec['resolution'];scene.render.resolution_percentage=100
    scene.render.fps=spec['fps'];scene.frame_start=1;scene.frame_end=math.ceil(segment['duracao_s']*30)
    scene.render.film_transparent=False;scene.render.use_sequencer=False
    if hasattr(scene.eevee,'taa_render_samples'):scene.eevee.taa_render_samples=spec['eevee_samples']
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    scene.render.use_file_extension=True;scene.timeline_markers.clear();scene.render.fps_base=1
    scene.render.use_persistent_data=True
    camcol=a.collection('Cameras_PROD002')
    cameras.shot(scene,camcol,'A_ideia',0,1.55,'medium',offset=-.22,travel=(.06,.10,.02))
    cameras.shot(scene,camcol,'A2_revela_destino',1.55,2.46,'wide',travel=(.12,.08,0))
    cameras.shot(scene,camcol,'B_oferta_pescador',2.46,4.65,'negotiation',travel=(.08,.22,0))
    cameras.shot(scene,camcol,'C_entrega_peixe',4.65,6.65,'goods_close',travel=(.04,.12,-.03))
    cameras.shot(scene,camcol,'C2_caminhada',6.65,7.5,'medium',travel=(.60,-.55,0),target_travel=(.60,-.55,0))
    cameras.shot(scene,camcol,'D_lenhador',7.5,9.2,'negotiation',offset=2.57,travel=(.04,.15,0))
    cameras.shot(scene,camcol,'D2_entrega_lenha',9.2,10.8,'goods_close',offset=2.57,travel=(.04,.12,0))
    cameras.shot(scene,camcol,'E_confianca',10.8,13,'medium',offset=2.57,travel=(0,.15,0))
    cameras.shot(scene,camcol,'E2_sorte_suspeita',13,17.52,'reaction_close',offset=2.57,travel=(.05,.22,.02))
    errors=pose_scene(scene,nico,actors['pescador'],actors['lenhador'],props,spec)
    if spec.get('nico_arm_solver') == 'anatomical':
        worst = max(errors, key=lambda row: row['nico_hand_target_error_max'])
        if worst['nico_hand_target_error_max'] > .005:
            raise ValueError(f"Nico target outside validated reach at frame {worst['frame']}; review the trajectory before saving")
    # Original S03 is loaded as a sound strip for editable playback; no synthesis.
    ed=scene.sequence_editor_create();sound=ed.strips.new_sound('Puck_S03_original',str(ROOT/segment['wav']),channel=1,frame_start=1);sound.volume=1
    scene['production_spec']=str(spec_path.relative_to(ROOT));scene['approved_audio']=segment['wav'];scene['canonical_global_start']=segment['inicio_global_s']
    scene['handoffs']=json.dumps(spec['handoffs_seconds']);scene['human_approval']=False
    scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=True)
    (out/'bake_metrics.json').write_text(json.dumps(errors,indent=2),encoding='utf-8')
    (out/'scene_build.json').write_text(json.dumps(dict(blender=bpy.app.version_string,file=dest.name,frames=scene.frame_end,duration_audio=segment['duracao_s'],global_start=segment['inicio_global_s'],segment=segment['id'],objects=len(scene.objects),camera_shots=len(scene.timeline_markers),hand_target_error_max=max(e['hand_target_error_max'] for e in errors)),indent=2),encoding='utf-8')
    status = out / 'STATUS.json'
    state = json.loads(status.read_text()) if status.exists() else {'completed': []}
    state['stage'] = 'scene_built_pending_audit'
    state['completed'] += ['shared asset libraries', 'S03 keyframes and cameras']
    status.write_text(json.dumps(state, indent=2), encoding='utf-8')
    print('BUILD_OK',dest,flush=True)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:];build(ROOT/args[0])
