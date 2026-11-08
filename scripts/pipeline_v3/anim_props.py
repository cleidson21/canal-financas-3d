"""Procedural construction and animation of interactive props V3:
- 40kg Burlap Potato Sack (starts on the wooden handcart, carried by Nico, lands with 'PLOC!' on counter)
- Counter Impact Dust Puffs
- Large Refusal Red X over the Potatoes
- Large Milk Desire Icon (Milk Carton + Glass + Green Checkmark)
"""

import math
from . import config
from .primitives import (
    create_beveled_box,
    create_cylinder,
    create_empty,
    create_gabled_roof,
    create_icosphere,
    create_tapered_box,
    create_uv_sphere,
)
from .scene_setup import set_interpolation


def build_potato_sack_geometry(col, mats, start_pos=None):
    """Build the 40kg burlap potato sack mesh hierarchy (origin at bottom Z=0)."""
    if start_pos is None:
        start_pos = config.POSITIONS["sack_on_cart"]

    sack_root = create_empty("Saco_Batatas_Root", start_pos, col, empty_size=0.15)

    # Plump Burlap Body (bottom at local Z = 0.0, height = 0.46)
    create_uv_sphere(
        "Saco_Corpo_Base",
        radius=0.255,
        segments=20,
        rings=14,
        location=(0.0, 0.0, 0.225),
        mat=mats["burlap_sack"],
        col=col,
        parent=sack_root,
        scale_xyz=(1.10, 0.96, 0.92),
        subsurf_levels=1,
        shade_smooth=True,
    )
    # Tied Rope Collar at Z = 0.41
    create_cylinder(
        "Saco_Corda_Amarracao",
        radius1=0.16,
        radius2=0.16,
        depth=0.048,
        vertices=16,
        location=(0.0, 0.0, 0.415),
        mat=mats["burlap_rope"],
        col=col,
        parent=sack_root,
        bevel_width=0.01,
        shade_smooth=True,
    )
    # Flared Burlap Top Rim
    create_cylinder(
        "Saco_Borda_Superior",
        radius1=0.145,
        radius2=0.22,
        depth=0.115,
        vertices=14,
        location=(0.0, 0.0, 0.465),
        mat=mats["burlap_sack"],
        col=col,
        parent=sack_root,
        bevel_width=0.008,
        shade_smooth=True,
    )
    # Front cream burlap patch / weight badge on the sack
    create_beveled_box(
        "Saco_Etiqueta_Frente",
        size_xyz=(0.18, 0.025, 0.11),
        location=(0.0, -0.245, 0.23),
        mat=mats["awning_cream"],
        col=col,
        parent=sack_root,
        rot=(math.radians(6), 0.0, 0.0),
        bevel_width=0.006,
        shade_smooth=True,
    )
    # Visible Golden Potatoes overflowing at the top of the sack
    potato_offsets = [
        (0.0, 0.0, 0.505, 0.082, (1.22, 0.92, 0.78)),
        (-0.085, -0.04, 0.495, 0.072, (1.12, 0.95, 0.82)),
        (0.085, -0.03, 0.495, 0.074, (1.05, 1.15, 0.80)),
        (-0.045, 0.065, 0.50, 0.068, (1.15, 0.90, 0.85)),
        (0.055, 0.065, 0.495, 0.070, (1.10, 1.00, 0.82)),
        (0.0, -0.085, 0.488, 0.065, (1.18, 0.88, 0.78)),
    ]
    for idx, (px, py, pz, prad, psc) in enumerate(potato_offsets):
        create_uv_sphere(
            f"Batata_Visivel_{idx+1:02d}",
            radius=prad,
            segments=12,
            rings=10,
            location=(px, py, pz),
            mat=mats["potato_gold"],
            col=col,
            parent=sack_root,
            scale_xyz=psc,
            shade_smooth=True,
        )

    return sack_root


def build_and_animate_potato_sack(col, mats):
    """Build the 40kg potato sack on the wooden cart and animate pickup, heavy carry, and 'PLOC!' counter landing."""
    cx, cy, cz = config.POSITIONS["sack_on_cart"]
    sack_root = build_potato_sack_geometry(col, mats, start_pos=(cx, cy, cz))

    # Keyframes: (frame, location, scale, rotation_euler)
    keyframes = [
        # 0.0-4.0s (Frames 1-120): Sitting coherently on the wooden handcart bed
        (1, (cx, cy, cz), (1.0, 1.0, 1.0), (0.0, 0.0, math.radians(-8))),
        (118, (cx, cy, cz), (1.0, 1.0, 1.0), (0.0, 0.0, math.radians(-8))),

        # 4.0-4.5s (Frames 120-135): Nico squats, grabs the heavy 40kg sack from the cart, and heaves it up
        (124, (cx - 0.02, cy - 0.06, cz - 0.02), (1.06, 1.04, 0.92), (math.radians(8), 0.0, math.radians(-4))),
        (135, (-1.28, -0.50, 0.78), (0.96, 0.96, 1.05), (math.radians(14), math.radians(-6), 0.0)),

        # 4.5-8.25s (Frames 136-248): Carried in Nico's arms with heavy up-and-down step bounce
        (146, (-1.12, -0.50, 0.83), (1.0, 1.0, 1.0), (math.radians(12), math.radians(4), 0.0)),
        (158, (-0.94, -0.50, 0.76), (1.03, 1.02, 0.96), (math.radians(15), math.radians(-4), 0.0)),
        (170, (-0.75, -0.49, 0.83), (1.0, 1.0, 1.0), (math.radians(12), math.radians(4), 0.0)),
        (182, (-0.56, -0.49, 0.76), (1.03, 1.02, 0.96), (math.radians(15), math.radians(-4), 0.0)),
        (194, (-0.37, -0.48, 0.83), (1.0, 1.0, 1.0), (math.radians(12), math.radians(4), 0.0)),
        (206, (-0.20, -0.48, 0.76), (1.03, 1.02, 0.96), (math.radians(15), math.radians(-4), 0.0)),
        (218, (-0.04, -0.48, 0.83), (1.0, 1.0, 1.0), (math.radians(12), math.radians(3), 0.0)),
        (232, (0.10, -0.46, 0.77), (1.02, 1.02, 0.97), (math.radians(14), math.radians(-3), 0.0)),
        (248, (0.22, -0.42, 0.80), (1.0, 1.0, 1.0), (math.radians(10), 0.0, 0.0)),

        # 8.5-9.3s (Frames 256-280): Nico heaves the 40kg sack high and drops it onto the counter ("PLOC!")
        (260, (0.44, -0.32, 1.18), (0.94, 0.94, 1.08), (math.radians(-8), math.radians(6), math.radians(-6))),
        # Frame 268: Heavy "PLOC!" impact on the wooden counter (Z = 0.96) with squash & stretch
        (268, (0.64, -0.20, 0.96), (1.24, 1.20, 0.74), (math.radians(4), math.radians(-4), math.radians(-10))),
        # Frame 274: Elastic rebound
        (274, (0.64, -0.20, 0.96), (0.93, 0.94, 1.10), (math.radians(-2), math.radians(2), math.radians(-10))),
        # Frame 280: Settle on the counter
        (280, (0.64, -0.20, 0.96), (1.0, 1.0, 1.0), (0.0, 0.0, math.radians(-10))),
        (450, (0.64, -0.20, 0.96), (1.0, 1.0, 1.0), (0.0, 0.0, math.radians(-10))),
    ]

    for fr, loc, sc, rot in keyframes:
        sack_root.location = loc
        sack_root.scale = sc
        sack_root.rotation_euler = rot
        sack_root.keyframe_insert(data_path="location", frame=fr)
        sack_root.keyframe_insert(data_path="scale", frame=fr)
        sack_root.keyframe_insert(data_path="rotation_euler", frame=fr)

    set_interpolation(sack_root, interpolation="BEZIER")

    # Counter Impact Dust Puffs at Frame 268 ("PLOC!" on counter)
    cx_cnt, cy_cnt, cz_cnt = config.POSITIONS["sack_on_counter"]
    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0)
        puff = create_icosphere(
            f"Poeira_Impacto_{i+1}",
            radius=0.06,
            subdivisions=1,
            location=(cx_cnt, cy_cnt, cz_cnt + 0.03),
            mat=mats["dust_puff"],
            col=col,
        )
        dx = math.cos(ang) * 0.34
        dy = math.sin(ang) * 0.26
        puff_keys = [
            (1, (cx_cnt, cy_cnt, cz_cnt + 0.02), (0.001, 0.001, 0.001)),
            (266, (cx_cnt, cy_cnt, cz_cnt + 0.02), (0.001, 0.001, 0.001)),
            (271, (cx_cnt + dx * 0.55, cy_cnt + dy * 0.55, cz_cnt + 0.08), (1.15, 1.15, 0.85)),
            (282, (cx_cnt + dx, cy_cnt + dy, cz_cnt + 0.14), (0.001, 0.001, 0.001)),
            (450, (cx_cnt + dx, cy_cnt + dy, cz_cnt + 0.14), (0.001, 0.001, 0.001)),
        ]
        for fr, loc, sc in puff_keys:
            puff.location = loc
            puff.scale = sc
            puff.keyframe_insert(data_path="location", frame=fr)
            puff.keyframe_insert(data_path="scale", frame=fr)
        set_interpolation(puff, interpolation="BEZIER")

    return sack_root


def build_story_signs_geometry(col, mats):
    """Build the 3D Refusal Red X sign and the Large 3D Milk Desire Sign."""
    # 1. BOLD RED "X" SIGN OVER THE POTATOES
    x_pos = config.POSITIONS["sign_x_pos"]
    x_root = create_empty(
        "Placa_Recusa_X_Root",
        x_pos,
        col,
        rot=(0.0, 0.0, math.radians(8)),
        empty_size=0.15,
    )
    create_beveled_box(
        "Placa_X_Fundo",
        size_xyz=(0.68, 0.07, 0.68),
        location=(0.0, 0.0, 0.0),
        mat=mats["sign_board"],
        col=col,
        parent=x_root,
        bevel_width=0.025,
    )
    create_beveled_box(
        "Placa_X_Moldura",
        size_xyz=(0.74, 0.05, 0.74),
        location=(0.0, 0.015, 0.0),
        mat=mats["sign_border_red"],
        col=col,
        parent=x_root,
        bevel_width=0.025,
    )
    for idx, angle_deg in enumerate((45, -45)):
        create_beveled_box(
            f"Placa_X_Barra_{idx+1}",
            size_xyz=(0.56, 0.06, 0.13),
            location=(0.0, -0.045, 0.0),
            mat=mats["sign_x_red"],
            col=col,
            parent=x_root,
            rot=(0.0, math.radians(angle_deg), 0.0),
            bevel_width=0.015,
        )

    # 2. LARGE 3D MILK DESIRE SIGN (Carton + Full Milk Glass + Green Check ✓)
    m_pos = config.POSITIONS["sign_milk_pos"]
    m_root = create_empty(
        "Placa_Desejo_Leite_Root",
        m_pos,
        col,
        rot=(0.0, 0.0, math.radians(-10)),
        empty_size=0.15,
    )
    create_beveled_box(
        "Placa_Leite_Fundo",
        size_xyz=(0.86, 0.07, 0.82),
        location=(0.0, 0.0, 0.0),
        mat=mats["sign_milk_bg"],
        col=col,
        parent=m_root,
        bevel_width=0.025,
    )
    create_beveled_box(
        "Placa_Leite_Moldura",
        size_xyz=(0.93, 0.05, 0.89),
        location=(0.0, 0.015, 0.0),
        mat=mats["sign_border_blue"],
        col=col,
        parent=m_root,
        bevel_width=0.025,
    )

    # Green Checkmark (✓) in top-right corner of Milk Sign
    create_beveled_box(
        "Placa_Leite_Check_Curto",
        size_xyz=(0.13, 0.045, 0.048),
        location=(0.16, -0.055, 0.205),
        mat=mats["sign_check_green"],
        col=col,
        parent=m_root,
        rot=(0.0, math.radians(40), 0.0),
        bevel_width=0.008,
    )
    create_beveled_box(
        "Placa_Leite_Check_Longo",
        size_xyz=(0.24, 0.045, 0.048),
        location=(0.265, -0.055, 0.245),
        mat=mats["sign_check_green"],
        col=col,
        parent=m_root,
        rot=(0.0, math.radians(-45), 0.0),
        bevel_width=0.008,
    )

    # 3D Milk Carton inside the Sign (scaled prominently for instant mobile recognition)
    carton_root = create_empty("Icone_Caixa_Leite_3D", (-0.12, -0.08, -0.06), col, parent=m_root, empty_size=0.08)
    create_beveled_box(
        "Leite_Corpo_Branco",
        size_xyz=(0.30, 0.20, 0.36),
        location=(0.0, 0.0, 0.0),
        mat=mats["milk_white"],
        col=col,
        parent=carton_root,
        bevel_width=0.015,
    )
    create_beveled_box(
        "Leite_Faixa_Azul",
        size_xyz=(0.31, 0.21, 0.13),
        location=(0.0, 0.0, 0.0),
        mat=mats["milk_blue"],
        col=col,
        parent=carton_root,
        bevel_width=0.01,
    )
    create_uv_sphere(
        "Leite_Gota_Frontal",
        radius=0.048,
        segments=12,
        rings=10,
        location=(0.0, -0.108, 0.0),
        mat=mats["milk_white"],
        col=col,
        parent=carton_root,
        scale_xyz=(0.75, 0.35, 1.18),
        shade_smooth=True,
    )
    create_gabled_roof(
        "Leite_Topo_Gable",
        width_x=0.30,
        depth_y=0.20,
        height_z=0.12,
        location=(0.0, 0.0, 0.18),
        mat=mats["milk_blue"],
        col=col,
        parent=carton_root,
        bevel_width=0.01,
    )
    create_beveled_box(
        "Leite_Aba_Selada",
        size_xyz=(0.30, 0.03, 0.045),
        location=(0.0, 0.0, 0.315),
        mat=mats["milk_white"],
        col=col,
        parent=carton_root,
        bevel_width=0.005,
    )
    create_cylinder(
        "Leite_Tampa_Rosca",
        radius1=0.036,
        radius2=0.036,
        depth=0.03,
        vertices=12,
        location=(0.06, -0.05, 0.24),
        mat=mats["milk_white"],
        col=col,
        parent=carton_root,
        rot=(math.radians(38), 0.0, 0.0),
        bevel_width=0.005,
    )

    # Full Milk Glass right beside the Carton
    create_cylinder(
        "Leite_Copo_Cheio",
        radius1=0.075,
        radius2=0.095,
        depth=0.24,
        vertices=16,
        location=(0.18, -0.09, -0.10),
        mat=mats["milk_white"],
        col=col,
        parent=m_root,
        bevel_width=0.01,
        shade_smooth=True,
    )
    create_cylinder(
        "Leite_Copo_DetalheAzul",
        radius1=0.084,
        radius2=0.088,
        depth=0.045,
        vertices=16,
        location=(0.18, -0.09, -0.09),
        mat=mats["milk_blue"],
        col=col,
        parent=m_root,
        bevel_width=0.005,
        shade_smooth=True,
    )

    return {"x_sign": x_root, "milk_sign": m_root}


def build_and_animate_refusal_and_milk_signs(col, mats):
    """Build and keyframe the 3D Red X Sign (Frames 348-450) and 3D Milk Sign (Frames 370-450)."""
    signs = build_story_signs_geometry(col, mats)
    x_root = signs["x_sign"]
    m_root = signs["milk_sign"]

    # Elastic Pop Animation for Red X Sign (Frames 348-364)
    x_keyframes = [
        (1, (0.001, 0.001, 0.001), (0.0, 0.0, math.radians(8))),
        (347, (0.001, 0.001, 0.001), (0.0, 0.0, math.radians(8))),
        (355, (1.28, 1.28, 1.28), (0.0, math.radians(8), math.radians(8))),
        (360, (0.92, 0.92, 0.92), (0.0, math.radians(-4), math.radians(8))),
        (365, (1.0, 1.0, 1.0), (0.0, 0.0, math.radians(8))),
        (450, (1.0, 1.0, 1.0), (0.0, 0.0, math.radians(8))),
    ]
    for fr, sc, rot in x_keyframes:
        x_root.scale = sc
        x_root.rotation_euler = rot
        x_root.keyframe_insert(data_path="scale", frame=fr)
        x_root.keyframe_insert(data_path="rotation_euler", frame=fr)

    # Elastic Pop Animation for Large Milk Sign (Frames 370-386)
    m_keyframes = [
        (1, (0.001, 0.001, 0.001), (0.0, 0.0, math.radians(-10))),
        (369, (0.001, 0.001, 0.001), (0.0, 0.0, math.radians(-10))),
        (377, (1.18, 1.18, 1.18), (0.0, math.radians(-8), math.radians(-10))),
        (382, (0.90, 0.90, 0.90), (0.0, math.radians(4), math.radians(-10))),
        (387, (0.96, 0.96, 0.96), (0.0, 0.0, math.radians(-10))),
        (450, (0.96, 0.96, 0.96), (0.0, 0.0, math.radians(-10))),
    ]
    for fr, sc, rot in m_keyframes:
        m_root.scale = sc
        m_root.rotation_euler = rot
        m_root.keyframe_insert(data_path="scale", frame=fr)
        m_root.keyframe_insert(data_path="rotation_euler", frame=fr)

    set_interpolation(x_root, interpolation="BEZIER")
    set_interpolation(m_root, interpolation="BEZIER")

    return signs
