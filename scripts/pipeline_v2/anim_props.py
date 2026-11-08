"""Procedural construction and animation of interactive props: Potato Sack, Impact Dust, Red X Sign, and Milk Sign."""

import math
from . import config
from .primitives import (
    create_beveled_box,
    create_cylinder,
    create_empty,
    create_gabled_roof,
    create_icosphere,
    create_tapered_box,
)
from .scene_setup import set_interpolation


def build_and_animate_potato_sack(col, mats):
    """Build the burlap potato sack (origin at bottom Z=0) and animate drop, squash-stretch, carry, and counter placement."""
    sx, sy = config.POSITIONS["sack_drop_xy"]
    sz_start = config.POSITIONS["sack_start_z"]

    sack_root = create_empty("Saco_Batatas_Root", (sx, sy, sz_start), col, empty_size=0.15)

    # Plump Burlap Body (bottom at local Z = 0.0, height = 0.44)
    create_icosphere(
        "Saco_Corpo_Base",
        radius=0.25,
        subdivisions=2,
        location=(0.0, 0.0, 0.22),
        mat=mats["burlap_sack"],
        col=col,
        parent=sack_root,
        scale_xyz=(1.08, 0.96, 0.92),
    )
    # Tied Rope Collar at Z = 0.41
    create_cylinder(
        "Saco_Corda_Amarracao",
        radius1=0.155,
        radius2=0.155,
        depth=0.045,
        vertices=12,
        location=(0.0, 0.0, 0.41),
        mat=mats["burlap_rope"],
        col=col,
        parent=sack_root,
        bevel_width=0.008,
    )
    # Flared Burlap Top Rim
    create_cylinder(
        "Saco_Borda_Superior",
        radius1=0.14,
        radius2=0.21,
        depth=0.11,
        vertices=10,
        location=(0.0, 0.0, 0.46),
        mat=mats["burlap_sack"],
        col=col,
        parent=sack_root,
        bevel_width=0.008,
    )
    # Visible Golden Potatoes overflowing at the top of the sack
    potato_offsets = [
        (0.0, 0.0, 0.49, (1.1, 0.9, 0.85)),
        (-0.08, -0.04, 0.47, (1.0, 0.85, 0.8)),
        (0.08, -0.03, 0.48, (0.95, 1.1, 0.8)),
        (-0.04, 0.06, 0.47, (1.05, 0.9, 0.85)),
        (0.05, 0.06, 0.47, (0.9, 1.0, 0.8)),
    ]
    for idx, (px, py, pz, psc) in enumerate(potato_offsets):
        create_icosphere(
            f"Saco_Batata_Visivel_{idx+1}",
            radius=0.068,
            subdivisions=2,
            location=(px, py, pz),
            mat=mats["potato_gold"],
            col=col,
            parent=sack_root,
            scale_xyz=psc,
        )

    # Impact Dust Puffs at landing site
    dust_puffs = []
    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0)
        p_obj = create_icosphere(
            f"Poeira_Impacto_{i+1}",
            radius=0.085,
            subdivisions=1,
            location=(sx, sy, 0.04),
            mat=mats["dust_puff"],
            col=col,
        )
        dust_puffs.append((p_obj, ang))

    # Animate Dust Puffs (frames 73 to 90)
    for p_obj, ang in dust_puffs:
        dx = math.cos(ang) * 0.42
        dy = math.sin(ang) * 0.42
        keyframes_dust = [
            (1, (sx, sy, 0.03), (0.001, 0.001, 0.001)),
            (73, (sx, sy, 0.03), (0.001, 0.001, 0.001)),
            (76, (sx + dx * 0.45, sy + dy * 0.45, 0.09), (1.15, 1.15, 0.85)),
            (83, (sx + dx * 0.88, sy + dy * 0.88, 0.14), (0.75, 0.75, 0.60)),
            (90, (sx + dx, sy + dy, 0.18), (0.001, 0.001, 0.001)),
        ]
        for fr, loc, sc in keyframes_dust:
            p_obj.location = loc
            p_obj.scale = sc
            p_obj.keyframe_insert(data_path="location", frame=fr)
            p_obj.keyframe_insert(data_path="scale", frame=fr)

    # Keyframe the Potato Sack across the 15-second storyboard
    # 1) Hidden above ground (frames 1-60), then accelerating fall (frames 61-74), squash & stretch (74-92)
    drop_keyframes = [
        (1, (sx, sy, sz_start), (0.001, 0.001, 0.001), (0.0, 0.0, 0.0)),
        (60, (sx, sy, sz_start), (0.001, 0.001, 0.001), (0.0, 0.0, 0.0)),
        (61, (sx, sy, sz_start), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)),
        (65, (sx, sy, 4.85), (0.96, 0.96, 1.06), (0.0, 0.04, 0.0)),
        (69, (sx, sy, 3.20), (0.92, 0.92, 1.14), (0.0, -0.05, 0.0)),
        (72, (sx, sy, 1.35), (0.86, 0.86, 1.24), (0.0, 0.03, 0.0)),
        (74, (sx, sy, 0.015), (0.88, 0.88, 1.20), (0.0, 0.0, 0.0)),
        # Impact Squash ("PLOC!")
        (76, (sx, sy, 0.015), (1.36, 1.36, 0.56), (0.0, 0.06, 0.0)),
        # Rebound Stretch & Hop
        (80, (sx, sy, 0.20), (0.86, 0.86, 1.20), (0.0, -0.08, 0.0)),
        # Second Squash
        (84, (sx, sy, 0.015), (1.16, 1.16, 0.82), (0.0, 0.03, 0.0)),
        # Small Settle
        (88, (sx, sy, 0.015), (0.96, 0.96, 1.05), (0.0, -0.01, 0.0)),
        (92, (sx, sy, 0.015), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)),
        (135, (sx, sy, 0.015), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)),
    ]

    # 2) Picked up by Nico (frames 135-148) and carried during the 6-step walk (frames 148-236)
    pickup_and_carry = [
        (140, (-1.45, -0.58, 0.28), (1.04, 1.04, 0.94), (math.radians(-10), 0.0, 0.0)),
        (148, (-1.42, -0.56, 0.66), (1.0, 1.0, 1.0), (math.radians(-14), 0.0, 0.0)),
    ]

    # Sync with Nico's 6 walk steps from X = -1.78 to X = +0.02 (sack held +0.34m ahead in X)
    walk_start_f = config.BEATS["walk_start"]
    walk_end_f = config.BEATS["walk_end"]
    cx_end_nico, cy_end_nico, _ = config.POSITIONS["nico_at_counter"]
    num_half_steps = 12
    for step_i in range(1, num_half_steps + 1):
        t = step_i / num_half_steps
        fr = round(walk_start_f + t * (walk_end_f - walk_start_f))
        nx = -1.78 + t * (cx_end_nico - (-1.78))
        ny = -0.62 + t * (cy_end_nico - (-0.62))
        # Sack is held in front of Nico (+0.34 in X, +0.05 in Y)
        bob_z = 0.66 + (0.045 if step_i % 2 == 1 else -0.015)
        sway_rot = math.radians(5 if step_i % 2 == 1 else -5)
        pickup_and_carry.append(
            (fr, (nx + 0.34, ny + 0.05, bob_z), (1.0, 1.0, 1.0), (math.radians(-12), sway_rot, 0.0))
        )

    # 3) Placed onto the Shop Counter (frames 236-266) and resting on Counter (Z = 0.96)
    cx, cy, cz = config.POSITIONS["sack_on_counter"]
    counter_keyframes = [
        (248, (0.68, -0.34, 1.12), (0.96, 0.96, 1.05), (math.radians(-6), 0.0, 0.0)),
        (257, (cx, cy, cz), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)),
        (260, (cx, cy, cz), (1.18, 1.18, 0.80), (0.0, 0.03, 0.0)),
        (265, (cx, cy, cz), (0.97, 0.97, 1.04), (0.0, 0.0, 0.0)),
        (270, (cx, cy, cz), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)),
        (450, (cx, cy, cz), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)),
    ]

    for fr, loc, sc, rot in drop_keyframes + pickup_and_carry + counter_keyframes:
        sack_root.location = loc
        sack_root.scale = sc
        sack_root.rotation_euler = rot
        sack_root.keyframe_insert(data_path="location", frame=fr)
        sack_root.keyframe_insert(data_path="scale", frame=fr)
        sack_root.keyframe_insert(data_path="rotation_euler", frame=fr)

    set_interpolation(sack_root, interpolation="BEZIER")
    return sack_root


def build_and_animate_refusal_and_milk_signs(col, mats):
    """Build and animate the Red X refusal sign and the Milk symbol desired by the seller."""
    # 1. Red X Refusal Sign ("Placa X Vermelho")
    x_pos = config.POSITIONS["sign_x_pos"]
    x_root = create_empty(
        "Placa_Recusa_X_Root",
        location=x_pos,
        col=col,
        rot=(0.0, 0.0, math.radians(-12)),
        empty_size=0.15,
    )
    # Outer Red Border Frame
    create_beveled_box(
        "Placa_X_Moldura",
        size_xyz=(0.68, 0.08, 0.68),
        location=(0.0, 0.0, 0.0),
        mat=mats["sign_border_red"],
        col=col,
        parent=x_root,
        bevel_width=0.025,
    )
    # Inner White/Cream Board
    create_beveled_box(
        "Placa_X_Fundo",
        size_xyz=(0.58, 0.10, 0.58),
        location=(0.0, -0.01, 0.0),
        mat=mats["sign_board"],
        col=col,
        parent=x_root,
        bevel_width=0.015,
    )
    # Volumetric 3D Red X Bars on front
    for idx, ang in enumerate((math.pi / 4.0, -math.pi / 4.0)):
        create_beveled_box(
            f"Placa_X_Barra_{idx+1}",
            size_xyz=(0.52, 0.09, 0.12),
            location=(0.0, -0.045, 0.0),
            mat=mats["sign_x_red"],
            col=col,
            parent=x_root,
            rot=(0.0, ang, 0.0),
            bevel_width=0.015,
        )

    # Elastic Pop Animation for Red X Sign (Frames 332-348)
    x_keyframes = [
        (1, (0.001, 0.001, 0.001), (0.0, 0.0, math.radians(-12))),
        (331, (0.001, 0.001, 0.001), (0.0, 0.0, math.radians(-12))),
        (338, (1.28, 1.28, 1.28), (0.0, math.radians(8), math.radians(-12))),
        (343, (0.90, 0.90, 0.90), (0.0, math.radians(-5), math.radians(-12))),
        (348, (1.04, 1.04, 1.04), (0.0, math.radians(2), math.radians(-12))),
        (353, (1.0, 1.0, 1.0), (0.0, 0.0, math.radians(-12))),
        (450, (1.0, 1.0, 1.0), (0.0, 0.0, math.radians(-12))),
    ]
    for fr, sc, rot in x_keyframes:
        x_root.scale = sc
        x_root.rotation_euler = rot
        x_root.keyframe_insert(data_path="scale", frame=fr)
        x_root.keyframe_insert(data_path="rotation_euler", frame=fr)

    # 2. Milk Symbol Sign ("Símbolo de Leite")
    m_pos = config.POSITIONS["sign_milk_pos"]
    m_root = create_empty(
        "Placa_Desejo_Leite_Root",
        location=m_pos,
        col=col,
        rot=(0.0, 0.0, math.radians(-12)),
        empty_size=0.15,
    )
    # Outer Blue Border Frame
    create_beveled_box(
        "Placa_Leite_Moldura",
        size_xyz=(0.72, 0.08, 0.72),
        location=(0.0, 0.0, 0.0),
        mat=mats["sign_border_blue"],
        col=col,
        parent=m_root,
        bevel_width=0.025,
    )
    # Inner Dark Navy Board (so the bright white Milk Carton & Glass pop with high contrast!)
    create_beveled_box(
        "Placa_Leite_Fundo",
        size_xyz=(0.62, 0.10, 0.62),
        location=(0.0, -0.01, 0.0),
        mat=mats["sign_milk_bg"],
        col=col,
        parent=m_root,
        bevel_width=0.015,
    )
    # Green Checkmark Badge in top-right corner of Milk Sign (indicates "WANTED / ACCEPTED")
    create_beveled_box(
        "Placa_Leite_Check_Curto",
        size_xyz=(0.09, 0.06, 0.042),
        location=(0.137, -0.055, 0.160),
        mat=mats["sign_check_green"],
        col=col,
        parent=m_root,
        rot=(0.0, math.radians(42), 0.0),
        bevel_width=0.008,
    )
    create_beveled_box(
        "Placa_Leite_Check_Longo",
        size_xyz=(0.18, 0.06, 0.042),
        location=(0.234, -0.055, 0.194),
        mat=mats["sign_check_green"],
        col=col,
        parent=m_root,
        rot=(0.0, math.radians(-45), 0.0),
        bevel_width=0.008,
    )
    # 3D Stylized Milk Carton + Milk Bottle mounted in relief on the front of the board
    carton_root = create_empty(
        "Icone_Caixa_Leite",
        location=(-0.08, -0.09, -0.04),
        col=col,
        parent=m_root,
        rot=(0.0, 0.0, math.radians(8)),
        empty_size=0.08,
    )
    # White Carton Body
    create_beveled_box(
        "Leite_Caixa_Corpo",
        size_xyz=(0.24, 0.14, 0.30),
        location=(0.0, 0.0, 0.0),
        mat=mats["milk_white"],
        col=col,
        parent=carton_root,
        bevel_width=0.015,
    )
    # Blue Label Band across the middle of the milk carton
    create_beveled_box(
        "Leite_Caixa_FaixaAzul",
        size_xyz=(0.25, 0.15, 0.11),
        location=(0.0, -0.005, 0.0),
        mat=mats["milk_blue"],
        col=col,
        parent=carton_root,
        bevel_width=0.01,
    )
    # White Milk Drop Emblem on the Blue Band
    create_icosphere(
        "Leite_Gota_Branca",
        radius=0.038,
        subdivisions=2,
        location=(0.0, -0.08, -0.005),
        mat=mats["milk_white"],
        col=col,
        parent=carton_root,
        scale_xyz=(0.85, 0.4, 1.25),
    )
    # Blue Gabled Carton Roof Top + Spout Cap
    create_gabled_roof(
        "Leite_Caixa_Topo",
        width_x=0.24,
        depth_y=0.14,
        height_z=0.11,
        location=(0.0, 0.0, 0.15),
        mat=mats["milk_blue"],
        col=col,
        parent=carton_root,
        bevel_width=0.01,
    )
    create_beveled_box(
        "Leite_Caixa_AbaSuperior",
        size_xyz=(0.24, 0.03, 0.04),
        location=(0.0, 0.0, 0.27),
        mat=mats["milk_white"],
        col=col,
        parent=carton_root,
        bevel_width=0.006,
    )
    create_cylinder(
        "Leite_Tampa_Rosca",
        radius1=0.028,
        radius2=0.028,
        depth=0.03,
        vertices=10,
        location=(0.05, -0.04, 0.21),
        mat=mats["milk_white"],
        col=col,
        parent=carton_root,
        rot=(math.radians(38), 0.0, 0.0),
        bevel_width=0.005,
    )

    # Classic Milk Glass / Bottle right beside the Carton inside the Sign
    create_cylinder(
        "Leite_Copo_Cheio",
        radius1=0.065,
        radius2=0.082,
        depth=0.20,
        vertices=12,
        location=(0.14, -0.09, -0.09),
        mat=mats["milk_white"],
        col=col,
        parent=m_root,
        bevel_width=0.01,
    )
    create_cylinder(
        "Leite_Copo_DetalheAzul",
        radius1=0.072,
        radius2=0.076,
        depth=0.04,
        vertices=12,
        location=(0.14, -0.09, -0.08),
        mat=mats["milk_blue"],
        col=col,
        parent=m_root,
        bevel_width=0.005,
    )

    # Elastic Pop Animation for Milk Sign (Frames 360-377)
    m_keyframes = [
        (1, (0.001, 0.001, 0.001), (0.0, 0.0, math.radians(-12))),
        (359, (0.001, 0.001, 0.001), (0.0, 0.0, math.radians(-12))),
        (366, (1.26, 1.26, 1.26), (0.0, math.radians(-8), math.radians(-12))),
        (371, (0.91, 0.91, 0.91), (0.0, math.radians(5), math.radians(-12))),
        (376, (1.03, 1.03, 1.03), (0.0, math.radians(-2), math.radians(-12))),
        (381, (1.0, 1.0, 1.0), (0.0, 0.0, math.radians(-12))),
        (450, (1.0, 1.0, 1.0), (0.0, 0.0, math.radians(-12))),
    ]
    for fr, sc, rot in m_keyframes:
        m_root.scale = sc
        m_root.rotation_euler = rot
        m_root.keyframe_insert(data_path="scale", frame=fr)
        m_root.keyframe_insert(data_path="rotation_euler", frame=fr)

    set_interpolation(x_root, interpolation="BEZIER")
    set_interpolation(m_root, interpolation="BEZIER")

    return {"x_sign": x_root, "milk_sign": m_root}

