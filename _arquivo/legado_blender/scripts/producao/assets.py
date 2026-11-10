"""Parametric clay market assets built on the existing seller mesh/material pipeline."""
import math
from pathlib import Path
import bpy
from mathutils import Vector
from pipeline_v3 import primitives as p, materials_lighting as ml


def collection(name):
    c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);return c

def material(name,color):
    return ml.create_stylized_material('PROD2_'+name,(*color,1),roughness=.72)

def empty(name,c,loc=(0,0,0),parent=None):
    return p.create_empty(name,loc,c,parent=parent)

def box(name,c,mat,loc,size,parent=None,rot=(0,0,0)):
    return p.create_beveled_box(name,size,loc,mat,c,parent=parent,rot=rot,bevel_width=.018,bevel_segments=2,shade_smooth=True)

def ball(name,c,mat,loc,size,parent=None):
    return p.create_uv_sphere(name,1,20,12,loc,mat,c,parent=parent,scale_xyz=size,shade_smooth=True)

def cylinder(name,c,mat,loc,radius,depth,parent=None,rot=(0,0,0)):
    return p.create_cylinder(name,radius,radius,depth,20,loc,mat,c,parent=parent,rot=rot,bevel_width=.014,shade_smooth=True)

def rope(name,c,mat,points,parent=None,radius=.012):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=radius;data.bevel_resolution=2
    spline=data.splines.new('POLY');spline.points.add(len(points)-1)
    for pt,co in zip(spline.points,points):pt.co=(*co,1)
    ob=bpy.data.objects.new(name,data);c.objects.link(ob);ob.parent=parent;data.materials.append(mat);return ob

def goods(kind,c,name=None):
    root=empty(name or 'PROP_'+kind,c);root['kind']=kind
    wood=material('wood',(.42,.22,.095));light=material('cut_wood',(.77,.55,.28));cream=material('cream',(.93,.87,.70))
    if kind=='potatoes':
        box(root.name+'_tray',c,wood,(0,0,-.025),(.34,.23,.045),root)
        for i,(x,y,z) in enumerate([(-.09,-.035,.055),(.075,-.04,.05),(0,.065,.07)]):
            ball(root.name+str(i),c,material('potato',(.85,.62,.24)),(x,y,z),(.085,.065,.065),root)
    elif kind=='fish':
        blue=material('fish_silver_blue',(.15,.58,.70))
        ball(root.name+'_body',c,blue,(0,0,.045),(.235,.065,.095),root)
        mesh=bpy.data.meshes.new(root.name+'_tail');mesh.from_pydata([(.17,-.035,.045),(.36,-.035,.17),(.36,-.035,-.07),(.17,.035,.045),(.36,.035,.17),(.36,.035,-.07)],[],[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)]);mesh.update()
        ob=bpy.data.objects.new(root.name+'_tail',mesh);c.objects.link(ob);ob.parent=root;mesh.materials.append(blue)
        ball(root.name+'_eye',c,material('eye',(.02,.025,.03)),(-.15,-.060,.08),(.018,.012,.018),root)
        rope(root.name+'_gill',c,cream,[(-.08,-.062,.11),(-.05,-.069,.04),(-.08,-.06,-.02)],root,.008)
        box(root.name+'_fin',c,blue,(-.015,0,.14),(.12,.03,.10),root,rot=(0,-.35,0))
    elif kind=='wood':
        for i,(y,z) in enumerate([(-.075,.025),(.075,.025),(0,.15)]):
            cylinder(root.name+str(i),c,wood,(0,y,z),.075,.43,root,(0,math.pi/2,0))
            cylinder(root.name+'_cut'+str(i),c,light,(-.219,y,z),.058,.009,root,(0,math.pi/2,0))
        for x in (-.12,.12):rope(root.name+'_tie',c,cream,[(x,-.15,0),(x,-.10,.18),(x,0,.25),(x,.1,.18),(x,.15,0),(x,-.15,0)],root,.009)
    elif kind=='milk':
        white=material('milk_white',(.94,.93,.84))
        cylinder(root.name+'_body',c,white,(0,0,.14),.09,.26,root)
        ball(root.name+'_shoulder',c,white,(0,0,.26),(.09,.09,.07),root)
        cylinder(root.name+'_neck',c,white,(0,0,.32),.045,.10,root)
        cylinder(root.name+'_lid',c,material('milk_blue',(.20,.47,.67)),(0,0,.38),.05,.03,root)
    elif kind=='eggs':
        wicker=material('egg_wicker',(.64,.42,.18))
        egg_mat=material('egg_shell',(.96,.90,.78))
        straw=material('egg_straw',(.91,.74,.28))
        cylinder(root.name+'_basket',c,wicker,(0,0,.045),.155,.09,root)
        cylinder(root.name+'_rim',c,wood,(0,0,.095),.168,.022,root)
        ball(root.name+'_straw',c,straw,(0,0,.085),(.14,.14,.035),root)
        for i,(x,y,z) in enumerate([(-.055,-.03,.12),(.055,-.03,.12),(0,.05,.125),(0,-.005,.155)]):
            ball(root.name+f'_egg_{i}',c,egg_mat,(x,y,z),(.042,.042,.056),root)
    elif kind=='flour':
        sack_mat=material('flour_sack',(.93,.89,.79))
        band_mat=material('flour_band',(.76,.28,.18))
        ball(root.name+'_body',c,sack_mat,(0,0,.15),(.15,.12,.16),root)
        cylinder(root.name+'_neck',c,band_mat,(0,0,.29),.09,.03,root)
        cylinder(root.name+'_top',c,sack_mat,(0,0,.33),.11,.055,root)
        box(root.name+'_label',c,band_mat,(0,-.118,.15),(.15,.018,.075),root)
    elif kind=='token':
        token_wood=material('token_wood',(.62,.36,.15))
        token_rim=material('token_rim',(.38,.20,.08))
        token_mark=material('token_mark',(.94,.76,.26))
        cylinder(root.name+'_disc',c,token_wood,(0,0,.09),.115,.034,root,rot=(math.pi/2,0,0))
        cylinder(root.name+'_ring',c,token_rim,(0,-.004,.09),.124,.024,root,rot=(math.pi/2,0,0))
        box(root.name+'_star_h',c,token_mark,(0,-.018,.09),(.11,.014,.034),root)
        box(root.name+'_star_v',c,token_mark,(0,-.018,.09),(.034,.014,.11),root)
    elif kind=='shoes':
        red=material('shoe_red',(.86,.16,.15))
        gold=material('shoe_gold',(.96,.76,.18))
        sole=material('shoe_sole',(.95,.93,.88))
        box(root.name+'_pad',c,wood,(0,0,-.015),(.36,.25,.03),root)
        for side,sx in (('L',-.085),('R',.085)):
            box(f'{root.name}_{side}_sole',c,sole,(sx,0,.018),(.11,.23,.028),root)
            ball(f'{root.name}_{side}_upper',c,red,(sx,.01,.062),(.065,.11,.048),root)
            ball(f'{root.name}_{side}_toe',c,sole,(sx,-.082,.042),(.058,.045,.032),root)
            box(f'{root.name}_{side}_stripe',c,gold,(sx,-.005,.065),(.12,.042,.028),root)
    root.asset_mark();return root


THEMES={
 'pescador':dict(color=(.06,.34,.61),accent=(.91,.66,.18),wood=(.48,.32,.18),width=1.85),
 'lenhador':dict(color=(.18,.36,.16),accent=(.64,.32,.11),wood=(.33,.18,.07),width=1.95),
 'leiteiro':dict(color=(.88,.84,.65),accent=(.32,.61,.72),wood=(.68,.52,.32),width=1.8),
 'ovos':dict(color=(.90,.56,.14),accent=(.74,.24,.14),wood=(.56,.36,.18),width=1.82),
}

def stall(kind):
    c=collection('Barraca_'+kind+'_PROD002');root=empty('Barraca_'+kind,c)
    cfg=THEMES[kind];w=cfg['width'];wood=material(kind+'_wood',cfg['wood']);color=material(kind+'_awning',cfg['color']);accent=material(kind+'_accent',cfg['accent']);cream=material('canvas_cream',(.92,.87,.71))
    for x in (-w/2,w/2):
        for y in (.15,.90):box(kind+'_post',c,wood,(x,y,1.13),(.085,.085,2.26),root)
    for i in range(6):
        x=-w/2+(i+.5)*w/6
        box(kind+'_canvas',c,color if i%2==0 else cream,(x,.49,2.21),(w/6+.012,1.14,.065),root,rot=(.12,0,0))
        box(kind+'_valance',c,color if i%2==0 else cream,(x,-.07,2.12),(w/6,.055,.18),root)
    box(kind+'_counter',c,wood,(0,.25,.86),(w,.66,.13),root)
    for i in range(6):box(kind+'_front_board',c,color,(-w*.42+i*w*.168,-.065,.43),(w*.15,.075,.77),root)
    box(kind+'_shelf',c,wood,(0,.86,1.25),(w*.86,.24,.06),root)
    root['merchant_socket']=[.40,.64,0];root['counter_z']=.925;root['variant']=kind
    if kind=='pescador':
        for x in (-.55,.05):
            box('Fish_crate',c,accent,(x,.24,.98),(.48,.43,.15),root)
            for z in (1.00,1.07):box('Crate_slat',c,wood,(x,.015,z),(.51,.025,.025),root)
            f=goods('fish',c);f.parent=root;f.location=(x,.2,1.08);f.scale=(.64,)*3
        # Rope net beside stall, with crossing strands and a ring buoy.
        for i in range(6):
            x=-.89+i*.13;rope('Fishing_net_vertical',c,cream,[(x,.85,.35),(x,.91,1.65)],root,.008)
            z=.4+i*.23;rope('Fishing_net_horizontal',c,cream,[(-.90,.89,z),(-.21,.89,z+.06)],root,.008)
        cylinder('Blue_bucket',c,color,(-1.10,.35,.24),.23,.46,root)
        rope('Bucket_handle',c,cream,[(-1.32,.35,.4),(-1.28,.35,.68),(-.93,.35,.68),(-.88,.35,.4)],root)
    elif kind=='lenhador':
        # Solid rustic boards, storage logs and decorative axe; distinct silhouette.
        for i in range(5):box('Rustic_plank',c,wood,(-.76+i*.38,.25,.956),(.36,.7,.055),root)
        for x in (-.52,-.02):
            for z in (.15,.36,.57):
                cylinder('Stored_log',c,wood,(x,.65,z),.11,.75,root,(math.pi/2,0,0))
                cylinder('Log_end',c,accent,(x,.266,z),.085,.012,root,(math.pi/2,0,0))
        cylinder('Stump',c,wood,(-1.12,.3,.28),.27,.55,root)
        box('Axe_handle',c,accent,(-1.12,.3,.93),(.055,.055,.85),root,rot=(0,-.2,0))
        box('Axe_head',c,material('axe_metal',(.35,.40,.42)),(-1.18,.3,1.22),(.30,.09,.20),root)
        for x in (-.50,0):g=goods('wood',c);g.parent=root;g.location=(x,.28,1.03);g.scale=(.7,)*3
    elif kind=='ovos':
        for x in (-.55,-.05,.45):
            g=goods('eggs',c);g.parent=root;g.location=(x,.24,.94);g.scale=(.9,)*3
        for x in (-.50,.15):
            g=goods('eggs',c);g.parent=root;g.location=(x,.86,1.29);g.scale=(.72,)*3
        # Decorative straw bale & flour sack beside the egg stall
        box('Straw_bale',c,material('straw_gold',(.88,.70,.24)),(-1.10,.38,.22),(.48,.36,.34),root)
        fl=goods('flour',c,'Display_flour');fl.parent=root;fl.location=(.52,.86,1.28);fl.scale=(.78,)*3
    else:
        for x in (-.57,-.20,.17):g=goods('milk',c);g.parent=root;g.location=(x,.23,.94)
        for x in (-.6,-.15,.3):g=goods('milk',c);g.parent=root;g.location=(x,.86,1.30);g.scale=(.65,)*3
        for x in (-1.1,1.1):
            cylinder('Milk_storage_can',c,material('can_cream',(.83,.83,.73)),(x,.55,.4),.22,.70,root)
            cylinder('Milk_can_lid',c,accent,(x,.55,.78),.23,.065,root)
            for side in (-1,1):box('Can_handle',c,accent,(x+side*.25,.55,.64),(.055,.12,.12),root)
    c.asset_mark();root.asset_mark();return c,root


def merchant(kind,head_source):
    """Same pivot schema and head mesh source, with clothes/accessories/proportions per role."""
    c=collection('Comerciante_'+kind+'_PROD002');root=empty('Comerciante_'+kind,c)
    cfg=THEMES[kind];shirt=material(kind+'_shirt',cfg['color']);cloth=material(kind+'_apron',cfg['accent']);skin=bpy.data.materials['Mat_nico_skin'];dark=material('hair_dark',(.12,.065,.035));white=material('canvas_cream',(.92,.87,.71))
    torso=empty(kind+'_Torso',c,(0,0,.84),root)
    p.create_segmented_organic_tube(kind+'_shirt',[(.52,.16,.11,0,0),(.46,.27,.15,0,0),(.18,.25,.16,0,0),(0,.23,.14,0,0)],18,(0,0,0),shirt,c,parent=torso,subsurf_levels=1,shade_smooth=True)
    # Contoured organic apron hugging the torso (no flat rigid board on chest)
    p.create_segmented_organic_tube(kind+'_apron',[(.38,.18,.115,0,-.045),(.22,.22,.135,0,-.042),(.02,.215,.13,0,-.038),(-.06,.20,.12,0,-.032)],16,(0,0,0),cloth,c,parent=torso,subsurf_levels=1,shade_smooth=True)
    for sx in (-.11,.11):
        box(f'{kind}_apron_strap_{sx:+.2f}',c,cloth,(sx,-.142,.44),(.038,.032,.14),torso,rot=(.18,0,0))
    if kind=='pescador':
        for z in (.28,.36,.43):
            p.create_segmented_organic_tube(f'Sailor_stripe_{z:.2f}',[(z+.016,.262,.158,0,-.004),(z-.016,.262,.158,0,-.004)],18,(0,0,0),white,c,parent=torso,cap_top=False,cap_bottom=False,subsurf_levels=1,shade_smooth=True)
    if kind=='lenhador':
        for z in (.28,.40):
            p.create_segmented_organic_tube(f'Plaid_band_{z:.2f}',[(z+.015,.264,.160,0,-.003),(z-.015,.264,.160,0,-.003)],18,(0,0,0),cloth,c,parent=torso,cap_top=False,cap_bottom=False,subsurf_levels=1,shade_smooth=True)
    head=empty(kind+'_Head',c,(0,0,.57),torso)
    cylinder(kind+'_neck',c,skin,(0,0,-.015),.083,.20,head)
    eyebrows=[]
    for original in head_source:
        if 'Boina' in original.name or ('Bigode' in original.name and kind!='leiteiro'):continue
        copy=original.copy();copy.data=original.data;c.objects.link(copy);copy.parent=head;copy.name=kind+'_'+original.name
        copy.animation_data_clear();copy.hide_render=False
        if 'Sobrancelha' in original.name:eyebrows.append(copy)
    # Add whites and mouth to the existing head, keeping the approved clay shape.
    for x in (-.095,.095):ball(kind+'_eye_white',c,white,(x,-.192,.255),(.045,.018,.046),head)
    mouth=ball(kind+'_smile',c,dark,(0,-.216,.115),(.06,.018,.018),head)
    if kind=='pescador':
        cylinder('Fisher_cap',c,shirt,(0,0,.46),.26,.11,head)
        cylinder('Fisher_cap_band',c,cloth,(0,0,.405),.263,.035,head)
        box('Fisher_cap_brim',c,shirt,(0,-.18,.395),(.45,.28,.035),head)
    elif kind=='lenhador':
        ball('Lumber_beanie',c,cloth,(0,0,.45),(.25,.24,.16),head)
        box('Lumber_beanie_rim',c,cloth,(0,0,.40),(.46,.41,.065),head)
        ball('Lumber_beard',c,dark,(0,-.175,.09),(.18,.12,.15),head)
        ball('Lumber_nose',c,skin,(0,-.24,.24),(.055,.055,.055),head)
    elif kind=='ovos':
        straw=material('straw_hat',(.92,.76,.32))
        cylinder('Egg_straw_crown',c,straw,(0,0,.45),.23,.12,head)
        cylinder('Egg_straw_brim',c,straw,(0,-.02,.40),.36,.028,head)
        cylinder('Egg_straw_band',c,cloth,(0,0,.415),.238,.032,head)
    else:
        ball('Milk_cap',c,white,(0,0,.44),(.26,.24,.11),head)
        box('Milk_cap_peak',c,shirt,(0,-.18,.40),(.35,.25,.035),head)
        box('Milk_bowtie',c,cloth,(0,-.155,.46),(.14,.035,.065),torso)
    arms={};palms={}
    for side,sign in (('L',-1),('R',1)):
        upper=empty(kind+'_Arm_'+side,c,(sign*.28,0,.44),torso)
        cylinder(kind+'_upper_'+side,c,shirt,(0,0,-.12),.066,.25,upper)
        lower=empty(kind+'_Forearm_'+side,c,(0,0,-.25),upper)
        cylinder(kind+'_lower_'+side,c,skin,(0,0,-.11),.05,.23,lower)
        palm=ball(kind+'_Palm_'+side,c,skin,(0,-.008,-.235),(.057,.045,.065),lower)
        ball(kind+'_Thumb_'+side,c,skin,(-sign*.045,-.035,-.22),(.025,.03,.04),lower)
        arms[side]=(upper,lower);palms[side]=palm
        cylinder(kind+'_trouser_'+side,c,material(kind+'_pants',(.13,.18,.22)),(sign*.135,0,.47),.095,.7,root)
        ball(kind+'_boot_'+side,c,dark,(sign*.135,-.065,.09),(.11,.20,.09),root)
    if kind=='lenhador':root.scale=(1.12,1.02,1.06)
    elif kind=='pescador':root.scale=(.94,.94,1.01)
    else:root.scale=(.95,.95,.97)
    c.asset_mark();root.asset_mark();root['role']=kind;root['animation_schema']='negotiator_two_link_v1'
    return dict(root=root,torso=torso,head=head,arms=arms,palms=palms,eyebrows=eyebrows,mouth=mouth,col=c)

def desire_plaque(name,c,kind='check',loc=(0,0,0),parent=None):
    """Build a compact 3D stall badge ('check', 'refuse', 'eggs', 'flour', 'token_accept')."""
    root=empty(name,c,loc,parent=parent)
    board=material('plaque_board',(.96,.94,.86))
    green=material('plaque_green',(.14,.74,.30))
    red=material('plaque_red',(.90,.14,.14))
    wood=material('plaque_wood',(.56,.34,.15))
    gold=material('plaque_gold',(.94,.76,.22))
    box(name+'_bg',c,board,(0,0,0),(.52,.055,.52),root)
    border_mat=green if kind in ('check','token_accept') else (red if kind=='refuse' else wood)
    box(name+'_border',c,border_mat,(0,.012,0),(.58,.04,.58),root)
    if kind=='refuse':
        for ang in (45,-45):
            box(f'{name}_x_{ang}',c,red,(0,-.038,0),(.42,.045,.10),root,rot=(0,math.radians(ang),0))
    elif kind=='check':
        box(name+'_chk_s',c,green,(-.07,-.038,-.04),(.14,.045,.065),root,rot=(0,math.radians(40),0))
        box(name+'_chk_l',c,green,(.07,-.038,.02),(.28,.045,.065),root,rot=(0,math.radians(-45),0))
    elif kind=='token_accept':
        cylinder(name+'_tok',c,wood,(-.06,-.042,-.02),.13,.036,root,rot=(math.pi/2,0,0))
        box(name+'_tok_h',c,gold,(-.06,-.062,-.02),(.11,.015,.034),root)
        box(name+'_tok_v',c,gold,(-.06,-.062,-.02),(.034,.015,.11),root)
        box(name+'_chk_s',c,green,(.11,-.045,.11),(.10,.04,.042),root,rot=(0,math.radians(40),0))
        box(name+'_chk_l',c,green,(.19,-.045,.15),(.19,.04,.042),root,rot=(0,math.radians(-45),0))
    elif kind=='eggs':
        egg_mat=material('plaque_egg',(.97,.91,.80))
        wicker=material('plaque_wicker',(.64,.42,.18))
        cylinder(name+'_bsk',c,wicker,(0,-.045,-.08),.15,.08,root)
        for idx,(ex,ez) in enumerate([(-.06,.02),(.06,.02),(0,.07)]):
            ball(f'{name}_egg_{idx}',c,egg_mat,(ex,-.05,ez),(.055,.04,.072),root)
        box(name+'_chk_s',c,green,(.12,-.045,.14),(.09,.04,.038),root,rot=(0,math.radians(40),0))
        box(name+'_chk_l',c,green,(.19,-.045,.18),(.17,.04,.038),root,rot=(0,math.radians(-45),0))
    elif kind=='flour':
        sack_m=material('plaque_flour',(.94,.90,.82))
        ball(name+'_sck',c,sack_m,(0,-.045,-.04),(.14,.06,.16),root)
        box(name+'_lbl',c,red,(0,-.095,-.04),(.14,.02,.06),root)
        box(name+'_chk_s',c,green,(.12,-.045,.14),(.09,.04,.038),root,rot=(0,math.radians(40),0))
        box(name+'_chk_l',c,green,(.19,-.045,.18),(.17,.04,.038),root,rot=(0,math.radians(-45),0))
    root.asset_mark();return root


def trade_arrow(name,c,color=(.94,.76,.20),length=.65,loc=(0,0,0),rot=(0,0,0),parent=None):
    """Build a 3D directional arrow used to visualize trade links and mismatches."""
    root=empty(name,c,loc,parent=parent);root.rotation_euler=rot
    mat=material(name+'_mat',color)
    box(name+'_shaft',c,mat,(-length*.18,0,0),(length*.64,.045,.075),root)
    box(name+'_wing_u',c,mat,(length*.18,0,.065),(.22,.048,.065),root,rot=(0,math.radians(35),0))
    box(name+'_wing_d',c,mat,(length*.18,0,-.065),(.22,.048,.065),root,rot=(0,math.radians(-35),0))
    root.asset_mark();return root


def write_library(path,collections):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():return
    bpy.data.libraries.write(str(path),set(collections),fake_user=True)
