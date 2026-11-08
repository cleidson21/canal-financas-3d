"""Build the complete EP001-V2 3D episode (Scenes 1-8, 3064 frames @ 30 FPS) in a unified master .blend.

Preserves:
- Approved Puck narration (`audio/narracoes/EP001/EP001_NARRACAO_COMPLETA_V1.wav`).
- Original Nico V3 rig, damaged right sneaker (`boca de jacaré`), village & Cobbler stall from `cena_01_V3_1.blend`.
- ANIM-004 torso-relative elbow pole (`pose_arm`), reach clamping, and thumb grip (`set_nico_grip`).
- Distinct stalls and differentiated merchants for Sapateiro, Pescador, Lenhador, Leiteiro, and Vendedor de Ovos.
- Continuous temporal animation across all 3,064 frames (zero static pose-strip slideshows).
"""
import argparse
import json
import math
from pathlib import Path
import sys
import time
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]

from scripts.producao import assets as a, motions as m
from pipeline_v3 import scene_setup, v3_1_narrated_scene as v31
from pipeline_v3.anim_character import _set_facial_expression

rad = math.radians


def k_loc(ob, frame, loc):
    ob.location = loc
    ob.keyframe_insert(data_path="location", frame=int(round(frame)))


def k_rot(ob, frame, rot):
    ob.rotation_mode = "XYZ"
    ob.rotation_euler = rot
    ob.keyframe_insert(data_path="rotation_euler", frame=int(round(frame)))


def k_scale(ob, frame, sc):
    ob.scale = sc
    ob.keyframe_insert(data_path="scale", frame=int(round(frame)))


def k_trs(ob, frame, loc=None, rot=None, scale=None):
    if ob is None:
        return
    f = int(round(frame))
    if loc is not None:
        ob.location = loc
        ob.keyframe_insert(data_path="location", frame=f)
    if rot is not None:
        ob.rotation_mode = "XYZ"
        ob.rotation_euler = rot
        ob.keyframe_insert(data_path="rotation_euler", frame=f)
    if scale is not None:
        ob.scale = scale
        ob.keyframe_insert(data_path="scale", frame=f)


def pop_scale(ob, start_f, end_f, max_s=1.0, total_f=3064):
    """Animate an object popping in with elastic overshoot between start_f and end_f, hidden outside."""
    HIDE = (0.001, 0.001, 0.001)
    S1 = tuple(max_s * 1.22 for _ in range(3))
    S2 = tuple(max_s * 0.93 for _ in range(3))
    S0 = (max_s, max_s, max_s)
    k_scale(ob, 1, HIDE)
    if start_f > 2:
        k_scale(ob, start_f - 1, HIDE)
    k_scale(ob, start_f + 6, S1)
    k_scale(ob, start_f + 11, S2)
    k_scale(ob, start_f + 16, S0)
    if end_f < total_f - 6:
        k_scale(ob, end_f - 4, S0)
        k_scale(ob, end_f + 2, HIDE)
        k_scale(ob, total_f, HIDE)
    else:
        k_scale(ob, total_f, S0)


def extend_village_fairground():
    """Extend the grass, dirt path, stepping stones, and background trees along X for the full fair."""
    grass = bpy.data.objects.get("Chao_Grama_Principal")
    if grass:
        grass.scale.x = 2.4
        grass.location.x = 6.0
    path = bpy.data.objects.get("Caminho_Terra_Feira")
    if path:
        path.scale.x = 3.2
        path.location.x = 5.5


def build_new_shoes_worn_on_nico(col):
    """Attach wearable red-and-gold new sneakers to Nico's feet (hidden until Scene 6C, shown in 6C-8)."""
    from pipeline_v3.primitives import create_beveled_box, create_tapered_box, create_uv_sphere

    red = a.material("worn_shoe_red", (0.86, 0.16, 0.15))
    gold = a.material("worn_shoe_gold", (0.96, 0.76, 0.18))
    sole = a.material("worn_shoe_sole", (0.95, 0.93, 0.88))
    worn = {}
    for side in ("L", "R"):
        foot = bpy.data.objects[f"Nico_Foot_{side}"]
        grp = a.empty(f"Nico_Sapato_Novo_Calcado_{side}", col, (0, 0, 0), parent=foot)
        create_beveled_box(
            f"Nico_Novo_{side}_Sola",
            size_xyz=(0.172, 0.345, 0.032),
            location=(0.0, -0.055, -0.097),
            mat=sole,
            col=col,
            parent=grp,
            bevel_width=0.012,
            subsurf_levels=1,
            shade_smooth=True,
        )
        create_tapered_box(
            f"Nico_Novo_{side}_Corpo",
            bottom_xy=(0.162, 0.315),
            top_xy=(0.132, 0.220),
            height_z=0.102,
            location=(0.0, -0.045, -0.032),
            mat=red,
            col=col,
            parent=grp,
            bevel_width=0.020,
            subsurf_levels=1,
            shade_smooth=True,
        )
        create_uv_sphere(
            f"Nico_Novo_{side}_Biqueira",
            radius=0.072,
            segments=14,
            rings=10,
            location=(0.0, -0.172, -0.062),
            mat=sole,
            col=col,
            parent=grp,
            scale_xyz=(1.04, 0.75, 0.45),
            shade_smooth=True,
        )
        create_beveled_box(
            f"Nico_Novo_{side}_FaixaOuro",
            size_xyz=(0.168, 0.065, 0.040),
            location=(0.0, -0.055, -0.034),
            mat=gold,
            col=col,
            parent=grp,
            bevel_width=0.008,
            shade_smooth=True,
        )
        for l_idx, (ly, lz) in enumerate(((-0.048, 0.016), (-0.082, 0.004), (-0.115, -0.008))):
            create_beveled_box(
                f"Nico_Novo_{side}_Cadarco_{l_idx+1}",
                size_xyz=(0.095, 0.020, 0.014),
                location=(0.0, ly, lz),
                mat=gold,
                col=col,
                parent=grp,
                rot=(rad(22), 0.0, 0.0),
                bevel_width=0.004,
                shade_smooth=True,
            )
        worn[side] = grp
    return worn


def build_transportadora_stack(col):
    """Build the comic teetering stack of crate, sack, wood, flour, and egg basket for Scene 4 ('abrir uma transportadora?')."""
    root = a.empty("Pilha_Transportadora_Root", col, (0, 0, 0))
    wood_m = a.material("stack_wood", (0.52, 0.32, 0.15))
    burlap_m = a.material("stack_burlap", (0.68, 0.48, 0.26))
    # Bottom crate held at stomach/waist level
    a.box("Pilha_Caixote_Base", col, wood_m, (0, 0, 0.08), (0.40, 0.28, 0.15), root)
    # Burlap sack on crate
    a.ball("Pilha_Saco_Meio", col, burlap_m, (0.04, 0, 0.23), (0.19, 0.15, 0.11), root)
    # Wood bundle tilted on left
    w = a.goods("wood", col, "Pilha_Lenha")
    w.parent = root
    w.location = (-0.06, 0, 0.33)
    w.scale = (0.78, 0.78, 0.78)
    # Flour sack tilted on right
    fl = a.goods("flour", col, "Pilha_Farinha")
    fl.parent = root
    fl.location = (0.07, 0, 0.44)
    fl.scale = (0.75, 0.75, 0.75)
    # Egg basket perched on top (reaches ~z=1.18 in world space so Nico's face at z=1.35..1.65 is 100% visible!)
    eg = a.goods("eggs", col, "Pilha_Ovos_Topo")
    eg.parent = root
    eg.location = (-0.03, 0, 0.58)
    eg.scale = (0.78, 0.78, 0.78)
    return root


def nico_actor():
    get = lambda n: bpy.data.objects["Nico_" + n]
    actor = dict(
        root=get("Root"),
        torso=get("Torso"),
        head=get("Head"),
        pelvis=get("Pelvis"),
        eyebrow_l=get("Sobrancelha_L"),
        eyebrow_r=get("Sobrancelha_R"),
        mouth=get("Boca"),
        damaged_sole=get("Sola_Descolada_Pivot_R"),
        arms={s: (get("Arm_" + s), get("Forearm_" + s)) for s in ("L", "R")},
        palms={s: get("Mao_Palma_" + s) for s in ("L", "R")},
        legs={s: (get("Leg_" + s), get("Knee_" + s), get("Foot_" + s)) for s in ("L", "R")},
    )
    for s in ("L", "R"):
        up, lo = actor["arms"][s]
        leg, knee, foot = actor["legs"][s]
        for ob in (up, lo, leg, knee, foot):
            ob.rotation_mode = "QUATERNION"
            ob.rotation_quaternion = (1, 0, 0, 0)
    return actor


def set_face_and_blink(nico, frame, t, state="neutral", asym_brow=0.0):
    _set_facial_expression(nico, frame, state)
    if abs(asym_brow) > 1e-4:
        ob = nico["eyebrow_l"]
        ob.rotation_euler.y += asym_brow
        m.key(ob, frame, "rotation_euler")

    # Natural blink every ~3.4 seconds
    blink = 1.0
    phase_b = (t + 0.6) % 3.4
    if phase_b < 0.16:
        blink = max(0.08, abs(phase_b - 0.08) / 0.08)
    for side in ("L", "R"):
        for part in ("Olho_Branco", "Pupila", "Brilho_Olho", "Brilho_Sec"):
            ob = bpy.data.objects[f"Nico_{part}_{side}"]
            ob.scale.z = blink
            m.key(ob, frame, "scale")
            if part in ("Brilho_Olho", "Brilho_Sec"):
                z = 0.284 if part == "Brilho_Olho" else 0.254
                ob.location.z = 0.268 + (z - 0.268) * blink
                m.key(ob, frame, "location")


def pose_legs_walk_or_stand(
    nico,
    frame,
    walk_u=None,
    num_steps=4,
    start_xy=(0.0, 0.0),
    end_xy=(0.0, 0.0),
    yaw=0.0,
    squat=0.0,
    stumble=0.0,
    sole_open_override=None,
    intact_shoe=False,
    prior_rotations=None,
):
    """Solve Nico's legs in world space with alternating grounded steps, or planted stance with knee bend."""
    root = nico["root"]
    rx, ry, rz = root.location
    c_yaw, s_yaw = math.cos(yaw), math.sin(yaw)

    for side, sign in (("L", -1.0), ("R", 1.0)):
        # Lateral hip offset in world space (local +X is right side of character)
        off_x = sign * 0.14 * c_yaw
        off_y = sign * 0.14 * s_yaw
        fwd_x = s_yaw
        fwd_y = -c_yaw
        ankle = Vector((rx + off_x, ry + off_y, 0.12))
        sole_ang = 0.04

        if walk_u is not None and 0.0 <= walk_u <= 1.0:
            step_f = walk_u * num_steps
            step_idx = min(num_steps - 1, int(step_f))
            u = step_f - step_idx
            is_swing = (step_idx % 2 == 0) == (side == "L")
            # Stride offset along Nico's forward direction relative to his current root (rx, ry),
            # preventing leg overstretching regardless of total walk distance
            stride = (-0.15 + 0.30 * m.smooth(u)) if is_swing else (0.15 - 0.30 * u)
            ankle.x = rx + off_x + fwd_x * stride
            ankle.y = ry + off_y + fwd_y * stride
            if is_swing:
                ankle.z = 0.12 + 0.105 * math.sin(u * math.pi)
                if side == "R":
                    sole_ang = 0.52 * math.sin(u * math.pi)
            else:
                ankle.z = 0.12
                sole_ang = 0.02

        if stumble > 0.0:
            if side == "R":
                # Lift right foot forward/up so the detached sole visibly peels open ("boca de jacaré")
                ankle.x += fwd_x * 0.14 * stumble
                ankle.y += fwd_y * 0.14 * stumble
                ankle.z = 0.12 + 0.12 * stumble
            else:
                ankle.x -= fwd_x * 0.08 * stumble
                ankle.y -= fwd_y * 0.08 * stumble

        leg, knee, foot = nico["legs"][side]
        # Forward knee bend direction in world space (local -Y is forward)
        fwd_x = s_yaw
        fwd_y = -c_yaw
        bend_dir = (fwd_x * 0.8 + sign * 0.15, fwd_y * 0.8, 0.0)
        m.aim_chain(
            leg,
            knee,
            foot,
            ankle,
            bend=bend_dir,
            previous=prior_rotations.get(leg.name) if prior_rotations is not None else None,
            evaluate=False,
        )
        leg_rot, knee_rot = leg.rotation_quaternion.copy(), knee.rotation_quaternion.copy()
        if prior_rotations is not None:
            prior_rotations[leg.name] = (leg_rot, knee_rot)
        m.key(leg, frame, "rotation_quaternion")
        m.key(knee, frame, "rotation_quaternion")

        parent_rot = leg.parent.matrix_world.to_quaternion() @ leg_rot @ knee_rot
        foot_rot = parent_rot.inverted() @ root.matrix_world.to_quaternion()
        if prior_rotations is not None and foot.name in prior_rotations:
            foot_rot.make_compatible(prior_rotations[foot.name])
            prior_rotations[foot.name] = foot_rot.copy()
        foot.rotation_mode = "QUATERNION"
        foot.rotation_quaternion = foot_rot
        m.key(foot, frame, "rotation_quaternion")

        if side == "R":
            sole_piv = nico["damaged_sole"]
            sole_mesh = bpy.data.objects.get("Nico_Tenis_SolaFrontal_R")
            ang = 0.0 if intact_shoe else (sole_open_override if sole_open_override is not None else sole_ang)
            if sole_piv:
                sole_piv.rotation_mode = "XYZ"
                sole_piv.rotation_euler = (ang, 0.0, 0.0)
                m.key(sole_piv, frame, "rotation_euler")
            if sole_mesh:
                sole_mesh.rotation_mode = "XYZ"
                sole_mesh.rotation_euler = (0.0, 0.0, 0.0)
                m.key(sole_mesh, frame, "rotation_euler")


def setup_shot_cameras(scene, cam_col, plans):
    """Create all 22 shot cameras from decupagem and bind timeline markers."""
    scene.timeline_markers.clear()
    # Camera definitions: id -> (start_loc, end_loc, start_tgt, end_tgt, lens)
    CAM_SPECS = {
        # S01: Cold Open Shoe Stumble + Village Reveal
        "Cam_S01_P01": ((-1.64, -2.35, 0.52), (-1.82, -4.25, 1.32), (-2.12, -0.62, 0.28), (-1.88, -0.56, 0.94), 45),
        "Cam_S01_P02": ((-0.58, -7.80, 1.85), (-0.48, -7.25, 1.76), (-0.38, 0.12, 1.20), (-0.32, 0.08, 1.16), 40),
        # S02: 40kg Potato Pickup, Walk & Offer, Cobbler Refusal, Reaction
        "Cam_S02_P01": ((-1.62, -4.15, 1.28), (-1.48, -4.05, 1.24), (-1.60, -0.24, 0.86), (-1.44, -0.36, 0.84), 45),
        "Cam_S02_P02": ((-1.05, -4.45, 1.32), (0.48, -4.85, 1.52), (-1.00, -0.35, 0.90), (0.66, -0.18, 1.12), 44),
        "Cam_S02_P03": ((0.54, -5.35, 1.62), (0.66, -5.50, 1.66), (0.62, -0.20, 1.30), (0.76, -0.20, 1.36), 44),
        "Cam_S02_P04": ((0.06, -3.75, 1.34), (0.04, -3.60, 1.32), (0.10, -0.38, 1.18), (0.08, -0.38, 1.16), 50),
        # S03: Fisherman & Lumberjack (offset +3.50 along X so stalls sit at X=3.93 and X=6.50)
        "Cam_S03_P01": ((3.25, -4.10, 1.92), (3.45, -5.10, 2.20), (3.35, 0.05, 1.24), (3.55, 0.15, 1.18), 44),
        "Cam_S03_P02": ((3.52, -3.45, 1.72), (3.56, -3.20, 1.68), (3.52, -0.05, 1.24), (3.54, -0.05, 1.22), 46),
        "Cam_S03_P03": ((3.60, -4.20, 1.85), (5.95, -3.55, 1.74), (3.65, -0.35, 1.18), (6.02, -0.05, 1.24), 45),
        "Cam_S03_P04": ((5.38, -3.15, 1.76), (5.42, -2.75, 1.74), (5.52, -0.05, 1.32), (5.55, -0.05, 1.36), 50),
        # S04: Milkman (X=9.50), Egg Seller (X=12.40), Transportadora Stack
        "Cam_S04_P01": ((9.05, -4.65, 1.92), (9.12, -4.45, 1.88), (9.10, 0.05, 1.28), (9.15, 0.05, 1.32), 45),
        "Cam_S04_P02": ((11.15, -5.10, 1.96), (11.95, -4.75, 1.92), (11.35, 0.05, 1.30), (11.98, 0.08, 1.32), 43),
        "Cam_S04_P03": ((11.45, -3.85, 1.58), (11.50, -3.65, 1.55), (11.55, -0.20, 1.18), (11.55, -0.20, 1.22), 46),
        # S05: Exhausted Nico & Double Coincidence of Wants
        "Cam_S05_P01": ((10.65, -3.35, 1.28), (10.70, -3.55, 1.34), (10.75, -0.55, 0.85), (10.75, -0.55, 0.92), 46),
        "Cam_S05_P02": ((10.75, -6.50, 2.25), (10.85, -6.20, 2.15), (10.80, 0.15, 1.30), (10.85, 0.15, 1.28), 40),
        # S06: Wooden Token Idea & 3 Distinct Transactions (Potatoes->Tokens, Tokens->Shoes, Tokens->Milk)
        "Cam_S06_P01": ((4.80, -7.20, 2.40), (3.60, -4.80, 1.90), (4.80, 0.20, 1.35), (3.55, 0.10, 1.28), 40),
        "Cam_S06_P02": ((3.48, -3.35, 1.70), (3.54, -3.15, 1.66), (3.50, -0.05, 1.22), (3.52, -0.05, 1.22), 46),
        "Cam_S06_P03": ((0.72, -4.15, 1.65), (0.68, -3.85, 1.60), (0.80, -0.10, 1.18), (0.75, -0.15, 1.18), 46),
        "Cam_S06_P04": ((8.85, -4.55, 1.85), (8.75, -4.25, 1.80), (8.90, 0.0, 1.22), (8.80, -0.05, 1.24), 44),
        # S07: Token Detail, Collective Trust, Without Trust = Just Wood
        "Cam_S07_P01": ((5.45, -2.55, 1.66), (5.50, -2.42, 1.64), (5.62, -0.12, 1.28), (5.64, -0.12, 1.28), 52),
        "Cam_S07_P02": ((5.10, -5.30, 2.05), (5.20, -5.05, 1.98), (5.15, 0.05, 1.28), (5.22, 0.05, 1.28), 42),
        "Cam_S07_P03": ((5.95, -3.55, 1.74), (6.00, -3.35, 1.70), (6.02, -0.05, 1.20), (6.04, -0.05, 1.18), 46),
        # S08: New Sneakers Callback & Final Question with Story Goods
        "Cam_S08_P01": ((0.18, -3.65, 1.18), (0.15, -3.95, 1.28), (0.10, -0.45, 0.72), (0.10, -0.45, 0.85), 45),
        "Cam_S08_P02": ((0.55, -3.95, 1.52), (0.35, -3.45, 1.48), (0.58, -0.25, 1.12), (0.32, -0.32, 1.18), 46),
    }

    for idx, plan in enumerate(plans):
        cid = plan["camera"]
        f0, f1 = plan["frames"]
        c_start, c_end, t_start, t_end, lens = CAM_SPECS[cid]
        cam_data = bpy.data.cameras.new(cid)
        cam_data.lens = lens
        cam_data.clip_start = 0.05
        cam_data.clip_end = 100.0
        cam_ob = bpy.data.objects.new(cid, cam_data)
        cam_col.objects.link(cam_ob)
        tgt_ob = a.empty(cid + "_target", cam_col)
        con = cam_ob.constraints.new("TRACK_TO")
        con.target = tgt_ob
        con.track_axis = "TRACK_NEGATIVE_Z"
        con.up_axis = "UP_Y"

        k_loc(cam_ob, f0, c_start)
        k_loc(cam_ob, f1, c_end)
        k_loc(tgt_ob, f0, t_start)
        k_loc(tgt_ob, f1, t_end)
        if cid == "Cam_S01_P01":
            # Pull back smoothly before frame 55 so Nico's full body and cap stay in frame during the stumble
            k_loc(cam_ob, 45, (-1.78, -4.05, 1.24))
            k_loc(tgt_ob, 45, (-1.92, -0.58, 0.88))
        elif cid == "Cam_S03_P03":
            # Track walk during 793..816, then frame Lumberjack stall cleanly from frame 818 onward
            k_loc(cam_ob, 815, (3.85, -4.35, 1.88))
            k_loc(tgt_ob, 815, (3.90, -0.45, 1.18))
            k_loc(cam_ob, 818, (5.88, -3.65, 1.76))
            k_loc(tgt_ob, 818, (6.00, -0.05, 1.24))
        scene_setup.set_interpolation(cam_ob, interpolation="BEZIER")
        scene_setup.set_interpolation(tgt_ob, interpolation="BEZIER")

        marker = scene.timeline_markers.new(cid, frame=f0)
        marker.camera = cam_ob
        if idx == 0:
            scene.camera = cam_ob


def build_episode(decupagem_path: Path):
    t0 = time.perf_counter()
    spec = json.loads(decupagem_path.read_text(encoding="utf-8"))
    timing = json.loads((ROOT / spec["timing"]).read_text(encoding="utf-8"))
    total_frames = int(spec["total_quadros"])  # 3064

    # 1. Open canonical V3.1 scene (contains Nico V3 + Armature, Cobbler stall, Seller, Cart, 40kg Sack, Signs)
    source_blend = ROOT / "arquivo/EP001/piloto/cenas/cena_01_V3_1.blend"
    bpy.ops.wm.open_mainfile(filepath=str(source_blend), load_ui=False)
    bpy.context.preferences.filepaths.file_preview_type = "NONE"
    scene = bpy.context.scene

    # Clear old animation data
    for ob in list(bpy.data.objects):
        ob.animation_data_clear()
        if ob.data and hasattr(ob.data, "animation_data_clear"):
            ob.data.animation_data_clear()

    # Ensure all Nico objects render
    for ob in bpy.data.objects:
        if ob.name.startswith("Nico_"):
            ob.hide_render = False

    # Extend village ground & path to cover the entire fairground
    extend_village_fairground()

    # 2. Build differentiated stalls and merchants along the fairground path:
    # Cobbler is already at X ~ 1.18 (Seller at X=1.38)
    # Pescador at X = 3.93, Lenhador at X = 6.50, Leiteiro at X = 9.50, Ovos at X = 12.40
    head_source = [ob for ob in bpy.data.objects if ob.parent and ob.parent.name == "Vendedor_Head"]
    roles = ("pescador", "lenhador", "leiteiro", "ovos")
    actors = {kind: a.merchant(kind, head_source) for kind in roles}
    stalls = {kind: a.stall(kind) for kind in roles}

    prop_col = a.collection("Mercadorias_EP001_V2")
    props = {
        kind: a.goods(kind, prop_col, "Troca_" + kind)
        for kind in ("potatoes", "fish", "wood", "milk", "eggs", "flour", "token")
    }

    # Save versioned shared libraries without overwriting protected files
    a.write_library(ROOT / "personagens/comerciantes_EP001_V2.blend", [x["col"] for x in actors.values()])
    a.write_library(ROOT / "cenarios/barracas_EP001_V2.blend", [x[0] for x in stalls.values()])
    a.write_library(ROOT / "objetos/mercadorias_EP001_V2.blend", [prop_col])
    a.write_library(ROOT / "objetos/ficha_pagamento.blend", [prop_col])

    stall_positions = {
        "pescador": 3.93,
        "lenhador": 6.50,
        "leiteiro": 9.50,
        "ovos": 12.40,
    }
    for kind, sx in stall_positions.items():
        stalls[kind][1].location = (sx, 0.75, 0.0)
        mx = sx - (0.10 if kind == "lenhador" else 0.0)
        actors[kind]["root"].location = (mx, -0.02, 0.0)
        actors[kind]["root"].rotation_euler.z = rad(-40)

    # Upgrade the Cobbler seller's apron to hug his torso cleanly and add legs/boots so he can stand in front of counters
    cob_apron = bpy.data.objects.get("Vendedor_Avental")
    if cob_apron:
        cob_apron.scale.y = 0.28
        cob_apron.location.y = -0.115
    cob_root = bpy.data.objects["Vendedor_Root"]
    cob_col = cob_root.users_collection[0] if cob_root.users_collection else scene.collection
    pants_m = a.material("cobbler_pants", (0.22, 0.25, 0.32))
    boot_m = a.material("cobbler_boots", (0.20, 0.13, 0.08))
    for side_s, sx in (("L", -0.12), ("R", 0.12)):
        a.cylinder(f"Vendedor_Perna_{side_s}", cob_col, pants_m, (sx, 0.0, 0.45), 0.085, 0.72, cob_root)
        a.ball(f"Vendedor_Bota_{side_s}", cob_col, boot_m, (sx, -0.04, 0.09), (0.095, 0.16, 0.09), cob_root)

    cobbler = {
        "root": cob_root,
        "torso": bpy.data.objects["Vendedor_Torso"],
        "head": bpy.data.objects["Vendedor_Head"],
        "arm_l": bpy.data.objects["Vendedor_Arm_L"],
        "arm_r": bpy.data.objects["Vendedor_Arm_R"],
    }

    # 3. Build Episode Story Props & Visual Metaphors (Plaques, Arrows, Transportadora Stack, Wearable New Shoes)
    fx_col = a.collection("Props_Narrativos_EP001_V2")
    mats = {m_ob.name: m_ob for m_ob in bpy.data.materials}
    no_money_badge = v31.build_no_money_context_badge(fx_col, mats)
    carimbo_badge = v31.build_carimbo_da_duvida_asset(fx_col, mats)
    worn_new_shoes = build_new_shoes_worn_on_nico(fx_col)
    transport_stack = build_transportadora_stack(fx_col)

    # Plaques for S04 & S05 (positioned cleanly above counters, clear of all characters' faces)
    plaque_s04_refuse_wood = a.desire_plaque("Placa_S04_Recusa_Lenha", fx_col, "refuse", (9.08, -0.22, 1.82))
    plaque_s04_want_eggs = a.desire_plaque("Placa_S04_Desejo_Ovos", fx_col, "eggs", (9.82, -0.18, 1.90))
    plaque_s04_refuse_eggs = a.desire_plaque("Placa_S04_Recusa_Ovos", fx_col, "refuse", (11.98, 0.12, 1.88))
    plaque_s04_want_flour = a.desire_plaque("Placa_S04_Desejo_Farinha", fx_col, "flour", (12.72, 0.12, 1.92))

    # 3D Trade Chain Arrows for S04 & S05
    arrow_1 = a.trade_arrow("Seta_Cadeia_1", fx_col, (0.94, 0.74, 0.18), 0.75, (9.85, -0.25, 1.55), (0, 0, 0))
    arrow_2 = a.trade_arrow("Seta_Cadeia_2", fx_col, (0.94, 0.52, 0.16), 0.75, (11.00, -0.25, 1.62), (0, 0, 0))
    arrow_3 = a.trade_arrow("Seta_Cadeia_3", fx_col, (0.90, 0.22, 0.16), 0.75, (12.15, -0.25, 1.68), (0, 0, 0))
    plaque_s05_mismatch_1 = a.desire_plaque("Placa_S05_Mismatch_1", fx_col, "refuse", (10.20, -0.28, 1.92))
    plaque_s05_mismatch_2 = a.desire_plaque("Placa_S05_Mismatch_2", fx_col, "refuse", (11.45, -0.28, 1.92))

    # Plaques for S06 & S07 (Token Acceptance ✓ and S07 Refusal X positioned prominently above Lumberjack counter)
    plaque_tok_cobbler = a.desire_plaque("Placa_Aceita_Sapateiro", fx_col, "token_accept", (1.65, -0.22, 1.82))
    plaque_tok_fisher = a.desire_plaque("Placa_Aceita_Pescador", fx_col, "token_accept", (4.35, -0.12, 1.82))
    plaque_tok_lumber = a.desire_plaque("Placa_Aceita_Lenhador", fx_col, "token_accept", (6.95, -0.12, 1.82))
    plaque_tok_milk = a.desire_plaque("Placa_Aceita_Leiteiro", fx_col, "token_accept", (9.90, -0.12, 1.82))
    plaque_s07_refuse_lumber = a.desire_plaque("Placa_Recusa_Lenhador", fx_col, "refuse", (5.98, -0.22, 1.80))

    # Hero Token Display for S06A & Summary Goods on Cobbler Counter for S08B
    ficha_hero = a.goods("token", fx_col, "Ficha_Destaque_Root")
    ficha_hero.location = (3.45, -0.55, 1.48)

    resumo_fish = a.goods("fish", fx_col, "Resumo_Peixe")
    resumo_wood = a.goods("wood", fx_col, "Resumo_Lenha")
    resumo_milk = a.goods("milk", fx_col, "Resumo_Leite")
    resumo_token = a.goods("token", fx_col, "Resumo_Ficha")

    # Configure scene render settings
    scene_setup.configure_scene_and_render(scene)
    scene.render.fps = 30
    scene.render.fps_base = 1.0
    scene.frame_start = 1
    scene.frame_end = total_frames
    scene.render.film_transparent = False
    scene.render.use_sequencer = False
    scene.render.use_persistent_data = True

    # Setup all 22 shot cameras
    cam_col = a.collection("Cameras_EP001_V2")
    setup_shot_cameras(scene, cam_col, spec["plans"])

    # 4. Animate Static/Pop-In Story Signs & Props across the 3064 frames
    # S01 No-Money Badge (frames 134..184)
    no_money_badge.location = (-0.38, -0.62, 1.92)
    pop_scale(no_money_badge, 134, 184, 1.0, total_frames)

    # S02 Cobbler Refusal X & Milk Sign & Carimbo
    x_sign = bpy.data.objects["Placa_Recusa_X_Root"]
    x_sign.location = (0.58, -0.26, 1.76)
    pop_scale(x_sign, 404, 590, 0.92, total_frames)

    milk_sign = bpy.data.objects["Placa_Desejo_Leite_Root"]
    milk_sign.location = (1.30, -0.24, 1.94)
    pop_scale(milk_sign, 456, 590, 0.95, total_frames)

    carimbo_badge.location = (-0.44, -0.52, 1.62)
    pop_scale(carimbo_badge, 540, 590, 1.0, total_frames)

    # S02 Potato Sack (40kg) & Dust Puffs
    sack = bpy.data.objects["Saco_Batatas_Root"]
    cx, cy, cz = (-1.62, 0.26, 0.34)
    cnt_x, cnt_y, cnt_z = (0.64, -0.20, 0.96)
    sack_keys = [
        (1, (cx, cy, cz), (1.0, 1.0, 1.0), (0, 0, rad(-8))),
        (235, (cx, cy, cz), (1.0, 1.0, 1.0), (0, 0, rad(-8))),
        (238, (cx - 0.02, cy - 0.06, cz - 0.02), (1.06, 1.04, 0.92), (rad(8), 0, rad(-4))),
        (256, (-1.28, -0.50, 0.78), (0.96, 0.96, 1.05), (rad(14), rad(-6), 0)),
        (270, (-0.98, -0.50, 0.83), (1.0, 1.0, 1.0), (rad(12), rad(4), 0)),
        (284, (-0.62, -0.49, 0.76), (1.03, 1.02, 0.96), (rad(15), rad(-4), 0)),
        (298, (-0.26, -0.48, 0.83), (1.0, 1.0, 1.0), (rad(12), rad(4), 0)),
        (310, (0.16, -0.42, 0.80), (1.0, 1.0, 1.0), (rad(10), 0, 0)),
        (314, (0.44, -0.32, 1.18), (0.94, 0.94, 1.08), (rad(-8), rad(6), rad(-6))),
        (318, (cnt_x, cnt_y, cnt_z), (1.24, 1.20, 0.74), (rad(4), rad(-4), rad(-10))),
        (323, (cnt_x, cnt_y, cnt_z), (0.93, 0.94, 1.10), (rad(-2), rad(2), rad(-10))),
        (330, (cnt_x, cnt_y, cnt_z), (1.0, 1.0, 1.0), (0, 0, rad(-10))),
        (592, (cnt_x, cnt_y, cnt_z), (1.0, 1.0, 1.0), (0, 0, rad(-10))),
        (2935, (cnt_x, cnt_y, cnt_z), (0.001, 0.001, 0.001), (0, 0, rad(-10))),
        (2936, (0.48, -0.22, 0.96), (0.72, 0.72, 0.72), (0, 0, rad(-6))),
        (total_frames, (0.48, -0.22, 0.96), (0.72, 0.72, 0.72), (0, 0, rad(-6))),
    ]
    for fr, loc, sc, rot in sack_keys:
        k_trs(sack, fr, loc=loc, rot=rot, scale=sc)
    scene_setup.set_interpolation(sack, interpolation="BEZIER")

    for i in range(6):
        puff = bpy.data.objects.get(f"Poeira_Impacto_{i+1}")
        if not puff:
            continue
        ang = i * (math.tau / 6.0)
        dx, dy = math.cos(ang) * 0.34, math.sin(ang) * 0.26
        k_trs(puff, 1, loc=(cnt_x, cnt_y, cnt_z + 0.02), scale=(0.001, 0.001, 0.001))
        k_trs(puff, 316, loc=(cnt_x, cnt_y, cnt_z + 0.02), scale=(0.001, 0.001, 0.001))
        k_trs(puff, 321, loc=(cnt_x + dx * 0.55, cnt_y + dy * 0.55, cnt_z + 0.08), scale=(1.15, 1.15, 0.85))
        k_trs(puff, 332, loc=(cnt_x + dx, cnt_y + dy, cnt_z + 0.14), scale=(0.001, 0.001, 0.001))
        k_trs(puff, total_frames, loc=(cnt_x + dx, cnt_y + dy, cnt_z + 0.14), scale=(0.001, 0.001, 0.001))

    # S04 & S05 Plaques and Arrows (hidden during S04_P03 transportadora close-up 1416..1557, shown again in S05_P02 1665..1835)
    for pl_ob, f_in, sc_in in (
        (plaque_s04_refuse_wood, 1180, 0.88),
        (plaque_s04_want_eggs, 1212, 0.92),
        (plaque_s04_refuse_eggs, 1295, 0.88),
        (plaque_s04_want_flour, 1315, 0.92),
        (arrow_1, 1330, 0.90),
        (arrow_2, 1350, 0.90),
        (arrow_3, 1370, 0.90),
    ):
        pop_scale(pl_ob, f_in, 1414, sc_in, total_frames)
        k_scale(pl_ob, 1664, (0.001, 0.001, 0.001))
        k_scale(pl_ob, 1672, (sc_in, sc_in, sc_in))
        k_scale(pl_ob, 1832, (sc_in, sc_in, sc_in))
        k_scale(pl_ob, 1836, (0.001, 0.001, 0.001))
        k_scale(pl_ob, total_frames, (0.001, 0.001, 0.001))
    pop_scale(plaque_s05_mismatch_1, 1675, 1835, 0.72, total_frames)
    pop_scale(plaque_s05_mismatch_2, 1705, 1835, 0.72, total_frames)

    # S06 & S07 Acceptance Plaques
    pop_scale(ficha_hero, 1860, 2080, 1.85, total_frames)
    for f_spin in range(1860, 2081, 10):
        k_rot(ficha_hero, f_spin, (0, 0, (f_spin - 1860) * 0.06))
    pop_scale(plaque_tok_fisher, 1965, 2730, 0.88, total_frames)
    pop_scale(plaque_tok_lumber, 1980, 2730, 0.88, total_frames)
    pop_scale(plaque_tok_cobbler, 1995, 2730, 0.88, total_frames)
    pop_scale(plaque_tok_milk, 2010, 2730, 0.88, total_frames)
    pop_scale(plaque_s07_refuse_lumber, 2732, 2855, 0.92, total_frames)

    # S08 Summary Goods on Cobbler Counter (frames 2936..3064)
    for ob, loc, sc in (
        (resumo_fish, (0.82, -0.18, 0.98), 0.72),
        (resumo_wood, (1.12, -0.18, 1.00), 0.68),
        (resumo_milk, (1.42, -0.18, 0.95), 0.78),
        (resumo_token, (1.68, -0.22, 0.98), 1.35),
    ):
        ob.location = loc
        pop_scale(ob, 2936, total_frames, sc, total_frames)

    # Wearable new shoes on Nico: hidden until frame 2242 (when he buys them in S06C!), visible in S06C-S08,
    # while hiding the old gray/broken sneaker meshes from frame 2242 onward so there is zero clipping!
    for side, grp in worn_new_shoes.items():
        k_scale(grp, 1, (0.001, 0.001, 0.001))
        k_scale(grp, 2241, (0.001, 0.001, 0.001))
        k_scale(grp, 2242, (1.0, 1.0, 1.0))
        k_scale(grp, total_frames, (1.0, 1.0, 1.0))

    old_shoe_names = [
        "Nico_Tenis_Corpo_L",
        "Nico_Tenis_Corpo_R",
        "Nico_Tenis_Sola_L",
        "Nico_Tenis_SolaTraseira_R",
        "Nico_Tenis_InteriorEscuro_R",
        "Nico_Tenis_MeiaInterna_R",
        "Nico_Tenis_SolaFrontal_R",
        "Nico_Tenis_SolaFrontal_CamadaInterna_R",
        "Nico_Tenis_Cadarco_L_1",
        "Nico_Tenis_Cadarco_L_2",
        "Nico_Tenis_Cadarco_L_3",
        "Nico_Tenis_Cadarco_R_1",
        "Nico_Tenis_Cadarco_R_2",
        "Nico_Tenis_Cadarco_R_3",
    ]
    for sh_name in old_shoe_names:
        sh_ob = bpy.data.objects.get(sh_name)
        if sh_ob:
            sh_ob.hide_render = False
            sh_ob.keyframe_insert(data_path="hide_render", frame=1)
            sh_ob.keyframe_insert(data_path="hide_render", frame=2241)
            sh_ob.hide_render = True
            sh_ob.keyframe_insert(data_path="hide_render", frame=2242)
            sh_ob.keyframe_insert(data_path="hide_render", frame=total_frames)

    # Display shoes on Cobbler counter: transferred to Nico at frame 2242
    shoes_disp = bpy.data.objects["Par_Sapatos_Novos_Root"]
    k_trs(shoes_disp, 1, loc=(1.30, -0.12, 1.02), rot=(0, 0, rad(-18)), scale=(1, 1, 1))
    k_trs(shoes_disp, 2235, loc=(1.30, -0.12, 1.02), rot=(0, 0, rad(-18)), scale=(1, 1, 1))
    k_trs(shoes_disp, 2242, loc=(0.62, -0.24, 1.12), rot=(0, 0, rad(15)), scale=(0.95, 0.95, 0.95))
    k_trs(shoes_disp, 2265, loc=(0.45, -0.30, 1.08), rot=(0, 0, rad(25)), scale=(0.001, 0.001, 0.001))
    k_trs(shoes_disp, total_frames, loc=(0.45, -0.30, 1.08), rot=(0, 0, rad(25)), scale=(0.001, 0.001, 0.001))

    # 5. Frame-by-frame continuous bake for Nico, all 5 Merchants, and Trade Goods (frames 1..3064)
    nico = nico_actor()
    fisher = actors["pescador"]
    lumber = actors["lenhador"]
    milkman = actors["leiteiro"]
    eggseller = actors["ovos"]
    previous = {}

    # World-space handoff coordinates (shifted by +3.50 for S03 stalls at 3.93 and 6.50)
    potato_contact = (3.48, -0.10, 1.08)
    fish_contact = (3.71, -0.10, 1.18)
    lumber_contact = (6.08, -0.07, 1.10)
    wood_contact = (6.21, -0.10, 1.09)
    milk_token_contact = (8.98, -0.08, 1.12)
    left_of = lambda v: tuple(Vector(v) + Vector((-0.075, 0, 0)))
    right_of = lambda v: tuple(Vector(v) + Vector((0.075, 0, 0)))

    for frame in range(1, total_frames + 1):
        scene.frame_set(frame)
        t = (frame - 1) / 30.0

        # Default hide/park for dynamic props unless active in current scene
        transport_stack.scale = (0.001, 0.001, 0.001)
        props["eggs"].location = (12.40, 0.24, 0.94)
        props["flour"].location = (12.92, 0.86, 1.28)
        props["milk"].location = (9.30, 0.23, 0.94)
        props["token"].location = (3.93, 0.20, 0.50)

        # Default Cobbler pose
        cob_loc = (1.38, 0.50, 0.08)
        cob_yaw = rad(-16)
        cob_head = (0.0, 0.0, rad(-20))
        cob_torso = (0.015 * math.sin(t * 2.2), 0.0, 0.0)
        cob_al = (rad(-12), rad(8), 0.0)
        cob_ar = (rad(-12), rad(-8), 0.0)

        # Default Nico state
        nx, ny, nz = 0.0, -0.48, 0.0
        nyaw = rad(25)
        pelvis_z = 0.77 + 0.004 * math.sin(t * 2.8)
        torso_rot = (0.02 * math.sin(t * 2.5), 0.0, 0.0)
        head_rot = (0.0, 0.0, 0.0)
        face_state = "neutral"
        asym_brow = 0.0
        walk_u = None
        walk_steps = 4
        walk_start = (0.0, 0.0)
        walk_end = (0.0, 0.0)
        stumble_w = 0.0
        sole_override = None
        intact_shoe = frame >= 2242
        grip_l, grip_r = 0.15, 0.15

        # ======================================================================
        # SCENE 1 (Frames 1..185 | 0.00s..6.13s): O SAPATO PEDIU DEMISSÃO
        # ======================================================================
        if frame <= 185:
            if frame <= 90:
                u = (frame - 1) / 89.0
                nx = -2.28 + 0.46 * m.smooth(u)
                ny = -0.62 + 0.06 * m.smooth(u)
                nyaw = rad(34)
                if frame < 38:
                    # Step lift: right foot lifts high and sole peels wide open ("boca de jacaré")
                    su = (frame - 1) / 37.0
                    sole_override = rad(14 + 26 * math.sin(su * math.pi))
                    stumble_w = 0.85 * math.sin(su * math.pi)
                    pelvis_z = 0.77 + 0.015 * math.sin(su * math.pi)
                    torso_rot = (rad(8), 0.0, rad(-4))
                    head_rot = (rad(16), 0.0, rad(-8))
                    face_state = "worried_shoe"
                elif frame < 68:
                    # Snag & stumble peak at frame 55
                    su = (frame - 38) / 30.0
                    stumble_bell = math.sin(su * math.pi)
                    stumble_w = stumble_bell
                    pelvis_z = 0.77 - 0.07 * stumble_bell
                    torso_rot = (rad(8 + 20 * stumble_bell), rad(-5 * stumble_bell), rad(8 * stumble_bell))
                    head_rot = (rad(14), rad(5 * stumble_bell), rad(-10))
                    sole_override = rad(6 + 26 * stumble_bell)
                    face_state = "surprised"
                else:
                    # Recover balance & inspect broken sole
                    sole_override = rad(24)
                    stumble_w = 0.35
                    torso_rot = (rad(12), 0.0, rad(-4))
                    head_rot = (rad(18), 0.0, rad(-8))
                    face_state = "worried_shoe"
            else:
                # Shot 2: Village reveal & No-Money badge
                u = (frame - 91) / 94.0
                nx, ny = -1.78 + 0.04 * m.smooth(u), -0.55
                nyaw = rad(26)
                sole_override = rad(20)
                head_rot = (rad(-2), 0.0, rad(-24 + 14 * math.sin(u * math.pi)))
                face_state = "worried_shoe" if frame > 135 else "neutral"

        # ======================================================================
        # SCENE 2 (Frames 186..592 | 6.17s..19.70s): A PRIMEIRA TENTATIVA
        # ======================================================================
        elif frame <= 592:
            if frame <= 258:
                # Idea + Squat + Lift 40kg potato sack
                if frame < 224:
                    nx, ny = -1.72, -0.54
                    nyaw = rad(32)
                    torso_rot = (rad(-4), 0.0, rad(-6))
                    head_rot = (rad(-6), rad(4), rad(-14))
                    face_state = "happy_idea"
                    sole_override = rad(16)
                elif frame < 244:
                    # Squat to grab sack
                    su = m.smooth((frame - 224) / 20.0)
                    nx = -1.72 + 0.16 * su
                    ny = -0.54 + 0.20 * su
                    nyaw = rad(32 - 14 * su)
                    pelvis_z = 0.77 - 0.10 * math.sin(su * math.pi)
                    torso_rot = (rad(22 * math.sin(su * math.pi)), 0.0, 0.0)
                    head_rot = (rad(-6), 0.0, 0.0)
                    face_state = "effort"
                    grip_l = grip_r = 0.85
                else:
                    # Heave sack against chest
                    su = m.smooth((frame - 244) / 14.0)
                    nx = -1.56 + 0.14 * su
                    ny = -0.34 - 0.16 * su
                    nyaw = rad(18 + 56 * su)
                    pelvis_z = 0.75
                    torso_rot = (rad(-8), 0.0, 0.0)
                    head_rot = (rad(6), 0.0, rad(-12))
                    face_state = "effort"
                    grip_l = grip_r = 0.95
            elif frame <= 312:
                # 4 grounded heavy steps from (-1.42, -0.50) to (0.02, -0.48)
                walk_u = (frame - 259) / 53.0
                walk_steps = 4
                walk_start = (-1.42, -0.50)
                walk_end = (0.02, -0.48)
                nx = walk_start[0] + (walk_end[0] - walk_start[0]) * walk_u
                ny = walk_start[1] + (walk_end[1] - walk_start[1]) * walk_u
                nyaw = rad(72 if walk_u < 0.88 else 44)
                pelvis_z = 0.755 - 0.025 * abs(math.sin(walk_u * 4 * math.pi))
                torso_rot = (rad(-7), 0.0, rad(4 * math.sin(walk_u * 2 * math.pi)))
                head_rot = (rad(6), 0.0, rad(-16))
                face_state = "effort"
                grip_l = grip_r = 0.95
            elif frame <= 342:
                # Drop sack on counter ("PLOC!" at 318) & point to new shoes
                nx, ny = 0.02, -0.48
                nyaw = rad(38)
                if frame < 322:
                    torso_rot = (rad(-10 if frame < 318 else 8), 0.0, rad(-6))
                    face_state = "effort"
                else:
                    torso_rot = (rad(4), 0.0, rad(-10))
                    head_rot = (rad(-4), 0.0, rad(-16))
                    face_state = "happy_idea"
                    sole_override = rad(15)
                cob_head = (rad(18), 0.0, rad(-18))
            elif frame <= 512:
                # Cobbler refuses (head shake + left arm up at 404) & points to Milk (right arm up at 456)
                nx, ny = -0.05, -0.48
                nyaw = rad(26)
                sole_override = rad(14)
                if frame < 404:
                    # Cobbler shakes head NO
                    shake = math.sin((frame - 343) * 0.35) * rad(22)
                    cob_head = (rad(10), 0.0, rad(-16) + shake)
                    face_state = "happy_idea"
                elif frame < 456:
                    # Red X pops! Nico recoils in surprise
                    cob_al = (rad(-68), rad(16), 0.0)
                    torso_rot = (rad(-8), 0.0, rad(6))
                    head_rot = (rad(-10), 0.0, rad(-18))
                    face_state = "surprised"
                else:
                    # Milk Sign pops!
                    cob_al = (rad(-24), rad(10), 0.0)
                    cob_ar = (rad(-76), rad(-20), 0.0)
                    cob_head = (rad(-6), 0.0, rad(-8))
                    torso_rot = (rad(-6), 0.0, rad(4))
                    head_rot = (rad(-12), rad(4), rad(-22))
                    face_state = "surprised"
            else:
                # Shot 4 (513..592): "Nico... aí complicou."
                nx, ny = -0.05, -0.48
                nyaw = rad(18)
                sole_override = rad(18)
                if frame < 538:
                    head_rot = (rad(-12), rad(4), rad(-20))
                    face_state = "surprised"
                elif frame < 556:
                    head_rot = (rad(14), rad(-4), rad(-24))
                    face_state = "worried_shoe"
                else:
                    pelvis_z = 0.735
                    torso_rot = (rad(8), rad(-3), 0.0)
                    head_rot = (rad(4), rad(8), rad(-8))
                    face_state = "frustrated"

        # ======================================================================
        # SCENE 3 (Frames 593..1121 | 19.76s..37.33s): UMA SORTE INACREDITÁVEL
        # ======================================================================
        elif frame <= 1121:
            t_s03 = (frame - 593) / 30.0  # 0.00s .. 17.60s local to S03
            if t_s03 < 6.7:
                nx, ny = 3.10, -0.10
                nyaw = rad(50)
            elif t_s03 < 7.5:
                walk_u = (t_s03 - 6.7) / 0.80
                walk_steps = 4
                walk_start = (3.10, -0.10)
                walk_end = (3.70, -0.65)
                nx = 3.10 + 0.60 * m.smooth(walk_u)
                ny = -0.10 - 0.55 * m.smooth(walk_u)
                nyaw = rad(50)
                pelvis_z = 0.755 - 0.035 * math.sin(walk_u * math.pi)
            else:
                nx, ny = 5.67, -0.10
                nyaw = rad(50) if t_s03 <= 10.8 else rad(50) * (1.0 - m.smooth((t_s03 - 10.8) / 0.8))
                # Physical weight dip when receiving the heavy wood bundle at t_s03 = 10.4s
                if 10.35 <= t_s03 <= 11.2:
                    dip = math.sin(max(0.0, min(1.0, (t_s03 - 10.35) / 0.85)) * math.pi)
                    pelvis_z -= 0.045 * dip

            torso_Vec = m.track(
                t_s03,
                [
                    (0, (0.08, 0, 0)),
                    (0.45, (0.16, 0, 0)),
                    (0.95, (-0.06, 0, 0)),
                    (1.6, (0, 0, 0)),
                    (10.3, (0, 0, 0)),
                    (10.55, (0.12, 0, 0.05)),
                    (11.4, (-0.10, 0, -0.04)),
                    (12.0, (-0.04, 0, 0.06)),
                    (12.6, (-0.10, 0, 0)),
                    (15.5, (-0.10, 0, 0)),
                    (16.1, (-0.02, 0, 0.04)),
                    (16.8, (-0.10, 0, -0.03)),
                    (17.5, (-0.06, 0, 0)),
                ],
            )
            torso_rot = tuple(torso_Vec)
            head_Vec = m.track(
                t_s03,
                [
                    (0, (0.06, 0, 0)),
                    (0.4, (0.32, 0, -0.1)),
                    (0.9, (-0.10, 0, 0.18)),
                    (1.5, (0, 0, 0.25)),
                    (2.4, (0, 0, 0.12)),
                    (6.5, (0, 0, 0.12)),
                    (7.5, (0, 0, 0.12)),
                    (10.5, (0, 0, 0.12)),
                    (11.1, (-0.12, 0, 0)),
                    (11.9, (0.05, 0, -0.25)),
                    (12.5, (-0.16, 0, 0)),
                    (15.2, (-0.16, 0, 0.14)),
                    (16.1, (0.06, 0, -0.12)),
                    (16.6, (-0.13, 0, 0.08)),
                    (17.5, (-0.08, 0, 0)),
                ],
            )
            head_rot = tuple(head_Vec)
            face_state = "happy_idea" if t_s03 > 0.65 else "neutral"
            if 11.6 < t_s03 < 12.4:
                face_state = "surprised"
            if 12.3 < t_s03 < 16.8:
                asym_brow = 0.18 * math.sin((t_s03 - 12.3) / 4.5 * math.pi)
            grip_r = 0.85 if t_s03 > 2.5 else 0.35

            # Fisherman & Lumberjack inspection & nod
            for actor, begin in ((fisher, 2.8), (lumber, 8.0)):
                ph = t_s03 - begin
                nod = 0.16 * math.sin(max(0.0, min(1.0, ph / 1.2)) * math.tau) if 0.0 < ph < 1.2 else 0.0
                actor["head"].rotation_euler = (nod, 0.0, 0.12 if actor is fisher else -0.10)
                actor["torso"].rotation_euler.x = (
                    0.07 * math.sin(max(0.0, min(1.0, ph / 1.1)) * math.pi) if 0.0 < ph < 1.1 else 0.015 * math.sin(t * 2)
                )
                m.key(actor["head"], frame, "rotation_euler")
                m.key(actor["torso"], frame, "rotation_euler")
                for brow in actor["eyebrows"]:
                    brow.location.z = 0.32 + 0.015 * max(0.0, math.sin(ph * 3)) if 0.0 < ph < 1.3 else 0.32
                    m.key(brow, frame, "location")

        # ======================================================================
        # SCENE 4 (Frames 1122..1557 | 37.38s..51.86s): A COINCIDÊNCIA ACABOU
        # ======================================================================
        elif frame <= 1557:
            if frame <= 1255:
                # At Milkman stall (X=9.50): Nico offers wood, Milkman refuses & points to Eggs
                nx, ny = 8.65, -0.15
                nyaw = rad(42)
                grip_r = 0.85
                if frame < 1180:
                    torso_rot = (rad(6), 0.0, rad(-6))
                    head_rot = (rad(-4), 0.0, rad(-12))
                    face_state = "happy_idea"
                else:
                    torso_rot = (rad(-6), 0.0, rad(5))
                    head_rot = (rad(-10), 0.0, rad(-18))
                    face_state = "surprised"
                # Milkman shakes head & points to Egg plaque
                shake = math.sin((frame - 1165) * 0.35) * rad(18) if 1165 <= frame <= 1210 else 0.0
                milkman["head"].rotation_euler = (0.0, 0.0, -0.15 + shake)
                m.key(milkman["head"], frame, "rotation_euler")
            elif frame <= 1415:
                # Walk to Egg Seller stall (1256..1290) and Egg Seller demands Flour + trade chain arrows
                if frame < 1290:
                    walk_u = (frame - 1256) / 34.0
                    walk_steps = 4
                    walk_start = (10.75, -0.18)
                    walk_end = (11.55, -0.15)
                    nx = walk_start[0] + (walk_end[0] - walk_start[0]) * m.smooth(walk_u)
                    ny = walk_start[1] + (walk_end[1] - walk_start[1]) * m.smooth(walk_u)
                    nyaw = rad(55)
                else:
                    nx, ny = 11.55, -0.15
                    nyaw = rad(35)
                    look_osc = math.sin((frame - 1290) * 0.14) * rad(22)
                    head_rot = (rad(-8), 0.0, look_osc)
                    torso_rot = (rad(4), 0.0, look_osc * 0.3)
                    face_state = "frustrated" if frame > 1340 else "surprised"
                shake = math.sin((frame - 1290) * 0.35) * rad(18) if 1290 <= frame <= 1335 else 0.0
                eggseller["head"].rotation_euler = (0.0, 0.0, -0.15 + shake)
                m.key(eggseller["head"], frame, "rotation_euler")
            else:
                # Shot 3 (1416..1557): "abrir uma transportadora?" — Nico staggering under chest-high stack (face 100% visible!)
                wobble = math.sin((frame - 1416) * 0.18)
                nx = 11.55 + 0.06 * wobble
                ny = -0.25
                nyaw = rad(18)
                pelvis_z = 0.725 + 0.015 * math.cos((frame - 1416) * 0.36)
                torso_rot = (rad(-10), rad(7 * wobble), rad(-5 * wobble))
                head_rot = (rad(-6), rad(-5 * wobble), rad(-8))
                face_state = "effort"
                sole_override = rad(22)
                grip_l = grip_r = 0.95
                transport_stack.location = (nx + 0.04, ny - 0.30, 0.56)
                transport_stack.rotation_euler = (rad(5), rad(9 * wobble), rad(6))
                transport_stack.scale = (1.0, 1.0, 1.0)

        # ======================================================================
        # SCENE 5 (Frames 1558..1837 | 51.92s..61.20s): DUPLA COINCIDÊNCIA DE DESEJOS
        # ======================================================================
        elif frame <= 1837:
            nx, ny = 10.75, -0.60
            nyaw = rad(10)
            breath = math.sin((frame - 1558) * 0.16)
            pelvis_z = 0.725 + 0.008 * breath
            sole_override = rad(26)  # Torn right shoe sole clearly open as reminder of goal
            if frame <= 1660:
                # Exhausted posture, heavy breathing, wiping brow / gesturing to goods on ground
                torso_rot = (rad(16 + 3 * breath), 0.0, 0.0)
                head_rot = (rad(14 + 2 * breath), 0.0, rad(-8))
                face_state = "frustrated"
            else:
                # Looking between mismatched merchants (Milkman on left, Egg Seller on right)
                pan_look = math.sin((frame - 1661) * 0.08) * rad(26)
                torso_rot = (rad(10), 0.0, pan_look * 0.25)
                head_rot = (rad(4), 0.0, pan_look)
                face_state = "worried_shoe"

        # ======================================================================
        # SCENE 6 (Frames 1838..2444 | 61.26s..81.43s): A IDEIA DA FICHA
        # ======================================================================
        elif frame <= 2444:
            if frame <= 2085:
                # 6A: Fair tests the wooden token; green plaques pop up; Nico perks up!
                nx, ny = 3.10, -0.25
                nyaw = rad(32)
                torso_rot = (rad(-4), 0.0, rad(-6))
                head_rot = (rad(-8), 0.0, rad(-12 + 16 * math.sin((frame - 1838) * 0.05)))
                face_state = "happy_idea" if frame > 1900 else "surprised"
            elif frame <= 2180:
                # 6B: Beat 1 — Nico sells potatoes at Fisherman stall (q2112) and receives wooden tokens (q2152)
                nx, ny = 3.10, -0.10
                nyaw = rad(48)
                torso_rot = (rad(4), 0.0, 0.0)
                head_rot = (rad(4), 0.0, rad(10))
                face_state = "happy_idea"
                grip_r = 0.85
            elif frame <= 2265:
                # 6C: Beat 2 — Nico hands tokens to Cobbler (q2208) and receives the new sneakers (q2242)!
                nx, ny = 0.25, -0.35
                nyaw = rad(42)
                torso_rot = (rad(-4), 0.0, rad(-8))
                head_rot = (rad(-6), 0.0, rad(-12))
                face_state = "happy_idea"
                cob_head = (rad(8), 0.0, rad(-18))
                cob_al = (rad(-52), rad(14), 0.0) if frame > 2200 else (rad(-15), rad(8), 0.0)
                cob_ar = (rad(-58), rad(-12), 0.0) if frame > 2230 else (rad(-15), rad(-8), 0.0)
            else:
                # 6D: Beat 3 — Cobbler uses the same tokens at Milkman stall (X=8.55..9.50) to buy milk!
                nx, ny = 7.80, -0.35
                nyaw = rad(28)
                cob_loc = (8.55, -0.12, 0.0)
                cob_yaw = rad(45)
                cob_head = (rad(4), 0.0, rad(-10))
                if frame < 2350:
                    # Cobbler extends right arm handing token to Milkman
                    cob_ar = (rad(-64), rad(-14), 0.0)
                elif frame < 2395:
                    # Cobbler receives milk bottle
                    cob_al = (rad(-58), rad(14), 0.0)
                    cob_ar = (rad(-48), rad(-10), 0.0)
                else:
                    # "Agora sim!" celebration
                    cob_al = (rad(-75), rad(20), 0.0)
                    cob_ar = (rad(-75), rad(-20), 0.0)
                    pelvis_z = 0.78 + 0.03 * abs(math.sin((frame - 2395) * 0.25))
                face_state = "happy_idea"

        # ======================================================================
        # SCENE 7 (Frames 2445..2861 | 81.48s..95.33s): CONFIANÇA
        # ======================================================================
        elif frame <= 2861:
            if frame <= 2602:
                # 7A: Nico inspects the wooden token in his hand ("pedaço de madeira como pagamento?")
                nx, ny = 5.67, -0.10
                nyaw = rad(18)
                torso_rot = (rad(-4), 0.0, 0.0)
                head_rot = (rad(6), rad(6 * math.sin((frame - 2445) * 0.06)), rad(-8))
                face_state = "surprised" if frame < 2520 else "happy_idea"
                asym_brow = 0.14
                grip_r = 0.80
            elif frame <= 2725:
                # 7B: Positive circulation & mutual trust ("Porque confiava que outras pessoas também aceitariam")
                nx, ny = 4.50, -0.25
                nyaw = rad(15)
                nod = 0.12 * math.sin((frame - 2603) * 0.18)
                head_rot = (nod, 0.0, rad(14 * math.sin((frame - 2603) * 0.07)))
                face_state = "happy_idea"
                for actor in (fisher, lumber):
                    actor["head"].rotation_euler = (nod, 0.0, 0.0)
                    m.key(actor["head"], frame, "rotation_euler")
            else:
                # 7C: Contrast — Without trust, plaques turn to X and token sits on counter as ordinary wood
                nx, ny = 5.67, -0.10
                nyaw = rad(32)
                head_rot = (rad(12), 0.0, rad(-10))
                face_state = "worried_shoe" if frame < 2830 else "neutral"
                shake = math.sin((frame - 2730) * 0.32) * rad(18) if frame < 2810 else 0.0
                lumber["head"].rotation_euler = (0.0, 0.0, -0.12 + shake)
                m.key(lumber["head"], frame, "rotation_euler")

        # ======================================================================
        # SCENE 8 (Frames 2862..3064 | 95.38s..102.12s): FECHAMENTO E PERGUNTA FINAL
        # ======================================================================
        else:
            nx, ny = 0.10, -0.45
            nyaw = rad(16)
            intact_shoe = True
            sole_override = 0.0
            if frame <= 2935:
                # 8A: Joyful step & intact right foot tap callback to Scene 1!
                u = (frame - 2862) / 73.0
                hop = abs(math.sin(u * 2 * math.pi))
                stumble_w = 0.75 * hop
                pelvis_z = 0.775 + 0.035 * hop
                torso_rot = (rad(6 - 10 * hop), 0.0, rad(-6))
                head_rot = (rad(12 * (1.0 - u)), 0.0, rad(-8))
                face_state = "happy_idea"
            else:
                # 8B: Final inviting question to the viewer alongside the story goods
                u = (frame - 2936) / 128.0
                torso_rot = (rad(-4), 0.0, rad(-6 + 6 * m.smooth(u)))
                head_rot = (rad(-4), rad(4 * math.sin(u * math.pi)), rad(-6))
                face_state = "happy_idea"
                asym_brow = 0.10 * math.sin(u * math.pi)

        # Apply Nico root, pelvis, torso, head, face, and legs
        k_trs(nico["root"], frame, loc=(nx, ny, nz), rot=(0.0, 0.0, nyaw))
        k_trs(nico["pelvis"], frame, loc=(0.0, 0.0, pelvis_z), rot=(0.0, 0.0, 0.0))
        k_trs(nico["torso"], frame, rot=torso_rot)
        k_trs(nico["head"], frame, rot=head_rot)
        set_face_and_blink(nico, frame, t, state=face_state, asym_brow=asym_brow)

        pose_legs_walk_or_stand(
            nico,
            frame,
            walk_u=walk_u,
            num_steps=walk_steps,
            start_xy=walk_start,
            end_xy=walk_end,
            yaw=nyaw,
            stumble=stumble_w,
            sole_open_override=sole_override,
            intact_shoe=intact_shoe,
            prior_rotations=previous,
        )

        # Apply Cobbler pose
        k_trs(cobbler["root"], frame, loc=cob_loc, rot=(0.0, 0.0, cob_yaw))
        k_trs(cobbler["torso"], frame, rot=cob_torso)
        k_trs(cobbler["head"], frame, rot=cob_head)
        k_trs(cobbler["arm_l"], frame, rot=cob_al)
        k_trs(cobbler["arm_r"], frame, rot=cob_ar)

        # Update matrices once before solving two-link hands & prop transfers
        bpy.context.view_layer.update()
        base_mat = nico["root"].matrix_world

        # Default relaxed hand targets in Nico's root frame
        nr = base_mat @ Vector((0.25, -0.24, 0.98))
        nl = base_mat @ Vector((-0.25, -0.22, 0.98))

        # Scene-specific hand targets for Nico
        if frame <= 90:
            if 38 <= frame <= 68:
                # Stumble balance arms out
                sb = math.sin((frame - 38) / 30.0 * math.pi)
                nr = base_mat @ Vector((0.36, -0.30, 1.12 + 0.16 * sb))
                nl = base_mat @ Vector((-0.36, -0.30, 1.12 + 0.18 * sb))
        elif 186 <= frame <= 592:
            if 192 <= frame <= 222:
                # Idea gesture pointing with right hand
                nr = base_mat @ Vector((0.24, -0.36, 1.32))
            elif 224 <= frame <= 316:
                # Carrying the 40kg sack against chest with both hands
                nr = base_mat @ Vector((0.18, -0.34, 1.02))
                nl = base_mat @ Vector((-0.18, -0.34, 1.02))
            elif 322 <= frame <= 398:
                # Pointing proudly to the new shoes on counter
                nr = base_mat @ Vector((0.28, -0.38, 1.24))
            elif 404 <= frame <= 510:
                # Startled recoil hands up
                nr = base_mat @ Vector((0.24, -0.28, 1.18))
                nl = base_mat @ Vector((-0.24, -0.28, 1.18))
            elif frame >= 556:
                # Comic shrug palms out
                nr = base_mat @ Vector((0.34, -0.26, 1.08))
                nl = base_mat @ Vector((-0.34, -0.26, 1.08))
        elif 593 <= frame <= 1121:
            t_s03 = (frame - 593) / 30.0
            if t_s03 < 6.7:
                nr = m.track(
                    t_s03,
                    [
                        (0, (3.18, -0.35, 1.03)),
                        (2.4, (3.18, -0.35, 1.03)),
                        (3.9, left_of(potato_contact)),
                        (4.15, left_of(potato_contact)),
                        (4.6, (3.28, -0.30, 1.08)),
                        (5.9, left_of(fish_contact)),
                        (6.12, left_of(fish_contact)),
                        (6.55, (3.23, -0.32, 1.07)),
                    ],
                )
                nl = m.track(
                    t_s03,
                    [
                        (0, tuple(nl)),
                        (0.9, tuple(nl)),
                        (1.45, (3.30, -0.34, 1.38)),
                        (1.8, (3.30, -0.34, 1.38)),
                        (2.3, tuple(nl)),
                    ],
                )
            elif t_s03 < 7.5:
                nr = Vector((nx + 0.13, ny - 0.22, 1.07))
                nl = Vector((nx - 0.04, ny - 0.30 + 0.04 * math.sin((t_s03 - 6.7) * math.tau / 0.39), 1.03))
            else:
                nr = m.track(
                    t_s03,
                    [
                        (7.5, (5.80, -0.34, 1.08)),
                        (8.9, left_of(lumber_contact)),
                        (9.10, left_of(lumber_contact)),
                        (9.45, (5.82, -0.32, 1.08)),
                        (10.4, left_of(wood_contact)),
                        (10.60, left_of(wood_contact)),
                        (11.15, (5.90, -0.34, 1.07)),
                        (17.52, (5.90, -0.34, 1.07)),
                    ],
                )
                if t_s03 > 11.0:
                    nl = m.track(
                        t_s03,
                        [
                            (11.0, tuple(nl)),
                            (11.6, (5.42, -0.28, 1.28)),
                            (12.2, (5.42, -0.28, 1.28)),
                            (13.0, (5.42, -0.22, 1.10)),
                            (15.4, (5.42, -0.22, 1.10)),
                            (16.1, (5.44, -0.30, 1.32)),
                            (16.8, (5.45, -0.28, 1.16)),
                            (17.52, (5.44, -0.25, 1.08)),
                        ],
                    )
        elif 1122 <= frame <= 1557:
            if frame <= 1255:
                # Offering wood bundle to Milkman
                nr = base_mat @ Vector((0.22, -0.34, 1.08))
                nl = base_mat @ Vector((-0.18, -0.30, 1.04))
            elif frame <= 1415:
                nr = base_mat @ Vector((0.22, -0.32, 1.06))
                nl = base_mat @ Vector((-0.26, -0.28, 1.14))
            else:
                # Holding the teetering Transportadora stack with both hands
                nr = base_mat @ Vector((0.20, -0.34, 1.06))
                nl = base_mat @ Vector((-0.20, -0.34, 1.06))
        elif 1558 <= frame <= 1837:
            # Exhausted slump, then gesturing toward surrounding stalls
            if frame > 1670:
                nr = base_mat @ Vector((0.30, -0.28, 1.10))
                nl = base_mat @ Vector((-0.30, -0.28, 1.10))
        elif 1838 <= frame <= 2444:
            if 2086 <= frame <= 2180:
                # Selling potatoes for token at Fisherman stall
                t_b = (frame - 2086) / 30.0
                nr = m.track(
                    t_b,
                    [
                        (0.0, (3.22, -0.32, 1.06)),
                        (0.85, left_of(potato_contact)),
                        (1.10, left_of(potato_contact)),
                        (2.20, left_of(fish_contact)),
                        (2.45, left_of(fish_contact)),
                        (3.10, (3.24, -0.32, 1.12)),
                    ],
                )
            elif 2181 <= frame <= 2265:
                # Handing token to Cobbler & receiving shoes
                u = (frame - 2181) / 84.0
                nr = base_mat @ Vector((0.24, -0.36, 1.14 + 0.08 * math.sin(u * math.pi)))
                nl = base_mat @ Vector((-0.20, -0.32, 1.10))
            elif frame >= 2395:
                # Celebrating "Agora sim!"
                nr = base_mat @ Vector((0.30, -0.28, 1.32))
                nl = base_mat @ Vector((-0.30, -0.28, 1.32))
        elif 2445 <= frame <= 2861:
            if frame <= 2602:
                # Holding wooden token up for close inspection
                nr = base_mat @ Vector((0.16, -0.34, 1.24))
                nl = base_mat @ Vector((-0.22, -0.26, 1.06))
            elif frame <= 2725:
                nr = base_mat @ Vector((0.24, -0.32, 1.14))
            else:
                # Placing token on Lumberjack counter at frame 2765
                t_c = (frame - 2726) / 30.0
                nr = m.track(
                    t_c,
                    [
                        (0.0, (5.82, -0.32, 1.12)),
                        (1.3, left_of(lumber_contact)),
                        (1.6, left_of(lumber_contact)),
                        (2.4, (5.78, -0.28, 1.04)),
                        (4.5, (5.78, -0.28, 1.04)),
                    ],
                )
        else:
            # Scene 8: Inviting gesture toward the viewer and the story objects
            if frame > 2945:
                u = (frame - 2945) / 119.0
                nr = base_mat @ Vector((0.28, -0.34, 1.16 + 0.06 * math.sin(u * math.pi)))
                nl = base_mat @ Vector((-0.28, -0.30, 1.10))

        # Clamp targets to Nico's validated anatomical reach shell and solve with torso-relative elbow pole
        nr_clamped = m.clamp_nico_reach(nico, "R", nr)
        nl_clamped = m.clamp_nico_reach(nico, "L", nl)
        m.hand(nico, "R", nr_clamped, frame, pole=m.nico_elbow_pole("R"), previous=previous, evaluate=False)
        m.hand(nico, "L", nl_clamped, frame, pole=m.nico_elbow_pole("L"), previous=previous, evaluate=False)
        m.set_nico_grip("R", grip_r, frame)
        m.set_nico_grip("L", grip_l, frame)

        # Solve Merchant arms for Fisherman, Lumberjack, Milkman, Egg Seller
        fl = (3.73, -0.13, 1.06)
        fr = (4.12, -0.14, 1.07)
        ll = (6.30, -0.10, 1.08)
        lr = (6.75, -0.15, 1.10)
        ml_l = (9.30, -0.12, 1.08)
        ml_r = (9.70, -0.14, 1.08)
        eg_l = (12.20, -0.12, 1.08)
        eg_r = (12.60, -0.14, 1.08)

        if 593 <= frame <= 1121:
            t_s03 = (frame - 593) / 30.0
            fl = m.track(
                t_s03,
                [
                    (0, (3.73, -0.13, 1.06)),
                    (2.8, (3.73, -0.13, 1.06)),
                    (3.9, right_of(potato_contact)),
                    (4.15, right_of(potato_contact)),
                    (4.65, (3.62, 0.24, 1.02)),
                ],
            )
            fr = m.track(
                t_s03,
                [
                    (0, (4.12, -0.14, 1.07)),
                    (4.55, (4.12, -0.14, 1.07)),
                    (5.9, right_of(fish_contact)),
                    (6.12, right_of(fish_contact)),
                    (6.55, (4.12, -0.14, 1.07)),
                ],
            )
            ll = m.track(
                t_s03,
                [
                    (0, (6.30, -0.10, 1.08)),
                    (8.15, (6.30, -0.10, 1.08)),
                    (8.9, right_of(lumber_contact)),
                    (9.1, right_of(lumber_contact)),
                    (9.65, (6.13, 0.30, 1.02)),
                ],
            )
            lr = m.track(
                t_s03,
                [
                    (0, (6.75, -0.15, 1.10)),
                    (9.45, (6.75, -0.15, 1.10)),
                    (10.4, right_of(wood_contact)),
                    (10.6, right_of(wood_contact)),
                    (11.1, (6.75, -0.15, 1.10)),
                ],
            )
        elif 1122 <= frame <= 1415:
            if frame <= 1255 and frame >= 1180:
                # Milkman points to Egg desire plaque
                ml_r = (9.75, -0.18, 1.36)
            elif frame > 1295:
                # Egg Seller points to Flour desire plaque
                eg_r = (12.65, -0.18, 1.36)
        elif 2086 <= frame <= 2180:
            t_b = (frame - 2086) / 30.0
            fl = m.track(
                t_b,
                [
                    (0.0, (3.73, -0.13, 1.06)),
                    (0.85, right_of(potato_contact)),
                    (1.10, right_of(potato_contact)),
                    (1.60, (3.62, 0.24, 1.02)),
                ],
            )
            fr = m.track(
                t_b,
                [
                    (0.0, (4.12, -0.14, 1.07)),
                    (1.60, (4.12, -0.14, 1.07)),
                    (2.20, right_of(fish_contact)),
                    (2.45, right_of(fish_contact)),
                    (3.00, (4.12, -0.14, 1.07)),
                ],
            )
        elif 2266 <= frame <= 2444:
            # Milkman receives token and hands milk to Cobbler
            t_m = (frame - 2266) / 30.0
            ml_l = m.track(
                t_m,
                [
                    (0.0, (9.30, -0.12, 1.08)),
                    (2.1, right_of(milk_token_contact)),
                    (2.4, right_of(milk_token_contact)),
                    (3.0, (9.30, 0.15, 1.04)),
                ],
            )
            ml_r = m.track(
                t_m,
                [
                    (0.0, (9.70, -0.14, 1.08)),
                    (3.0, (9.70, -0.14, 1.08)),
                    (3.6, (9.08, -0.10, 1.14)),
                    (4.2, (9.70, -0.14, 1.08)),
                ],
            )

        for actor, side, target in (
            (fisher, "L", fl),
            (fisher, "R", fr),
            (lumber, "L", ll),
            (lumber, "R", lr),
            (milkman, "L", ml_l),
            (milkman, "R", ml_r),
            (eggseller, "L", eg_l),
            (eggseller, "R", eg_r),
        ):
            m.hand(actor, side, target, frame, pole=None, previous=previous, evaluate=False)

        bpy.context.view_layer.update()

        # Bind Trade Goods Transfers with continuous ownership
        if 593 <= frame <= 1121:
            t_s03 = (frame - 593) / 30.0
            m.bind_transfer(
                props["potatoes"],
                frame,
                nico["palms"]["R"],
                fisher["palms"]["L"],
                593 + round(3.9 * 30),
                giver_offset=(0.075, 0, 0.11),
                receiver_offset=(-0.075, 0, 0.11),
            )
            if t_s03 < 8.9:
                m.bind_transfer(
                    props["fish"],
                    frame,
                    fisher["palms"]["R"],
                    nico["palms"]["R"],
                    593 + round(5.9 * 30),
                    giver_offset=(-0.075, 0, 0.115),
                    receiver_offset=(0.075, 0, 0.115),
                )
            else:
                m.bind_transfer(
                    props["fish"],
                    frame,
                    nico["palms"]["R"],
                    lumber["palms"]["L"],
                    593 + round(8.9 * 30),
                    giver_offset=(0.075, 0, 0.115),
                    receiver_offset=(-0.075, 0, 0.115),
                )
            m.bind_transfer(
                props["wood"],
                frame,
                lumber["palms"]["R"],
                nico["palms"]["R"],
                593 + round(10.4 * 30),
                giver_offset=(-0.075, 0, 0.115),
                receiver_offset=(0.075, 0, 0.115),
            )
        elif 1122 <= frame <= 1415:
            # Nico carries the wood bundle during S04P01 and S04P02
            props["wood"].location = nico["palms"]["R"].matrix_world.translation + Vector((0.06, -0.04, 0.10))
            props["potatoes"].location = (3.62, 0.24, 1.02)
            props["fish"].location = (6.13, 0.30, 1.02)
        elif 1558 <= frame <= 1837:
            # S05: Goods resting on the ground around exhausted Nico
            props["wood"].location = (10.30, -0.52, 0.08)
            props["potatoes"].location = (11.20, -0.52, 0.06)
            props["fish"].location = (6.13, 0.30, 1.02)
        elif 2086 <= frame <= 2180:
            # S06B: Nico sells potatoes for wooden token
            m.bind_transfer(
                props["potatoes"],
                frame,
                nico["palms"]["R"],
                fisher["palms"]["L"],
                2112,
                giver_offset=(0.075, 0, 0.11),
                receiver_offset=(-0.075, 0, 0.11),
            )
            m.bind_transfer(
                props["token"],
                frame,
                fisher["palms"]["R"],
                nico["palms"]["R"],
                2152,
                giver_offset=(-0.06, 0, 0.08),
                receiver_offset=(0.06, 0, 0.08),
            )
        elif 2181 <= frame <= 2265:
            # S06C: Nico gives token to Cobbler
            if frame < 2208:
                props["token"].location = nico["palms"]["R"].matrix_world.translation + Vector((0.05, -0.04, 0.08))
            else:
                props["token"].location = (0.95, -0.18, 1.02)
        elif 2266 <= frame <= 2444:
            # S06D: Cobbler gives token to Milkman (2330) and receives Milk bottle (2375)
            if frame < 2330:
                props["token"].location = (8.88, -0.12, 1.12)
            else:
                props["token"].location = milkman["palms"]["L"].matrix_world.translation + Vector((-0.05, 0, 0.08))
            if frame >= 2375:
                props["milk"].location = (8.78, -0.12, 1.08)
        elif 2445 <= frame <= 2861:
            # S07: Token inspected in Nico's hand (7A & 7B), then placed on counter next to wood (7C)
            if frame < 2765:
                props["token"].location = nico["palms"]["R"].matrix_world.translation + Vector((0.04, -0.05, 0.08))
                props["wood"].location = (6.35, 0.18, 1.02)
            else:
                props["token"].location = (6.05, -0.08, 0.96)
                props["wood"].location = (6.35, -0.06, 1.00)
        else:
            props["potatoes"].location = (3.62, 0.24, 1.02)
            props["fish"].location = (6.13, 0.30, 1.02)
            props["wood"].location = (6.50, 0.28, 1.03)

        for p_ob in props.values():
            m.key(p_ob, frame, "location")
        k_trs(
            transport_stack,
            frame,
            loc=transport_stack.location,
            rot=transport_stack.rotation_euler,
            scale=transport_stack.scale,
        )

    m.finalize_curves(bpy.context.scene.objects)

    # 6. Attach canonical full narration WAV strip at frame 1
    wav_full = ROOT / timing["narracao_completa"]
    v31.setup_vse_narration_audio(scene, wav_full)
    scene.render.use_sequencer = False  # Keep 3D camera rendering active!

    # 7. Save master editable 3D project
    dest_blend = ROOT / spec["blend"]
    dest_blend.parent.mkdir(parents=True, exist_ok=True)
    scene.frame_set(1)
    bpy.context.preferences.filepaths.file_preview_type = "NONE"
    bpy.ops.wm.save_as_mainfile(filepath=str(dest_blend), relative_remap=True)
    elapsed = time.perf_counter() - t0
    print(f"BUILD_EP001_V2_OK {dest_blend} ({elapsed:.2f}s)", flush=True)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else ["episodios/EP001_dinheiro/TESTES/EP001_V2_DECUPAGEM.json"]
    build_episode(ROOT / argv[0])
