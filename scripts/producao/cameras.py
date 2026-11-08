"""Narrative 9:16 shot presets and marker cuts; camera travel uses clamped easing."""
import bpy
from .assets import empty
from .motions import key
from pipeline_v3.scene_setup import set_interpolation

PRESETS={
 'wide':((.05,-5.8,2.55),(.05,.20,1.12),42),
 'medium':((-.12,-3.5,1.95),(-.15,0,1.30),45),
 'goods_close':((.0,-2.95,1.68),(.02,-.10,1.22),48),
 'reaction_close':((-.30,-2.65,1.82),(-.42,-.03,1.45),52),
 'negotiation':((.05,-5.2,2.20),(.05,.10,1.13),45),
 'comparative':((0,-3.7,1.85),(0,0,1.10),48),
 'shoe_close':((-.20,-1.85,.42),(-.05,-.05,.20),48),
 'fair_panorama':((.0,-7.8,2.65),(.0,.25,1.22),38),
}

def shot(scene,col,name,start,end,preset,offset=0,travel=(0,0,0),target_travel=(0,0,0)):
    location,target,lens=PRESETS[preset]
    data=bpy.data.cameras.new(name);data.lens=lens;data.clip_start=.05;data.clip_end=100
    ob=bpy.data.objects.new(name,data);col.objects.link(ob)
    tgt=empty(name+'_target',col)
    con=ob.constraints.new('TRACK_TO');con.target=tgt;con.track_axis='TRACK_NEGATIVE_Z';con.up_axis='UP_Y'
    for t,u in ((start,0),(end,1)):
        frame=round(t*30)+1
        ob.location=(location[0]+offset+travel[0]*u,location[1]+travel[1]*u,location[2]+travel[2]*u)
        tgt.location=(target[0]+offset+target_travel[0]*u,target[1]+target_travel[1]*u,target[2]+target_travel[2]*u)
        key(ob,frame,'location');key(tgt,frame,'location')
    set_interpolation(ob);set_interpolation(tgt)
    marker=scene.timeline_markers.new(name,frame=round(start*30)+1);marker.camera=ob
    if start==0:scene.camera=ob
    return ob
