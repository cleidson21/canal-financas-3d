"""Procedural articulated low-poly character Nico (and the Shoe Stall Seller)."""

import math
from . import config
from .primitives import (
    create_beveled_box,
    create_cylinder,
    create_empty,
    create_icosphere,
    create_tapered_box,
    create_uv_sphere,
)


def build_character_nico(col, mats):
    """Build articulated low-poly Nico with oversized expressive head, cap, and damaged sneaker.

    Local coordinate convention for Nico:
    - Forward (face direction): -Y
    - Back: +Y
    - Left side of screen / right body side: -X
    - Right side of screen / forward-featured side: +X
    - Up: +Z (Soles touch Z = 0.0 when pelvis is at Z = 0.78)
    """
    start_pos = config.POSITIONS["nico_start"]
    root = create_empty("Nico_Root", start_pos, col, rot=(0.0, 0.0, math.radians(38)), empty_size=0.25)

    # Pelvis pivot at Z = 0.78
    pelvis = create_empty("Nico_Pelvis", (0.0, 0.0, 0.78), col, parent=root, empty_size=0.15)
    create_beveled_box(
        "Nico_Bermuda_Quadril",
        size_xyz=(0.44, 0.28, 0.18),
        location=(0.0, 0.0, 0.02),
        mat=mats["nico_shorts_blue"],
        col=col,
        parent=pelvis,
        bevel_width=0.025,
    )

    # Torso pivot at Z = +0.07 relative to Pelvis (World Z = 0.85)
    torso = create_empty("Nico_Torso", (0.0, 0.0, 0.07), col, parent=pelvis, empty_size=0.15)
    create_tapered_box(
        "Nico_Camisa_Torso",
        bottom_xy=(0.42, 0.26),
        top_xy=(0.50, 0.30),
        height_z=0.52,
        location=(0.0, 0.0, 0.26),
        mat=mats["nico_shirt"],
        col=col,
        parent=torso,
        bevel_width=0.03,
    )
    # Shirt collar detail
    create_beveled_box(
        "Nico_Camisa_Gola",
        size_xyz=(0.26, 0.24, 0.06),
        location=(0.0, -0.01, 0.52),
        mat=mats["awning_cream"],
        col=col,
        parent=torso,
        bevel_width=0.015,
    )

    # Head pivot at Z = +0.55 relative to Torso (World Z = 1.40)
    head = create_empty("Nico_Head", (0.0, 0.0, 0.55), col, parent=torso, empty_size=0.15)
    # Neck
    create_cylinder(
        "Nico_Pescoco",
        radius1=0.085,
        radius2=0.085,
        depth=0.10,
        vertices=10,
        location=(0.0, 0.0, 0.03),
        mat=mats["nico_skin"],
        col=col,
        parent=head,
        bevel_width=0.01,
        shade_smooth=True,
    )
    # Oversized Stylized Low-Poly Head
    create_beveled_box(
        "Nico_Cabeca_Mesh",
        size_xyz=(0.50, 0.45, 0.46),
        location=(0.0, 0.0, 0.26),
        mat=mats["nico_skin"],
        col=col,
        parent=head,
        bevel_width=0.11,
        bevel_segments=3,
        shade_smooth=True,
    )
    # Ears
    for side_s, x_ear in (("L", -0.26), ("R", 0.26)):
        create_beveled_box(
            f"Nico_Orelha_{side_s}",
            size_xyz=(0.07, 0.09, 0.12),
            location=(x_ear, 0.02, 0.25),
            mat=mats["nico_skin"],
            col=col,
            parent=head,
            bevel_width=0.02,
            shade_smooth=True,
        )
    # Nose (pointing -Y)
    create_beveled_box(
        "Nico_Nariz",
        size_xyz=(0.08, 0.09, 0.08),
        location=(0.0, -0.24, 0.23),
        mat=mats["nico_skin"],
        col=col,
        parent=head,
        bevel_width=0.025,
        shade_smooth=True,
    )

    # Expressive Eyes (Sclera + Pupil + Specular Highlight)
    for side_s, x_eye in (("L", -0.115), ("R", 0.115)):
        create_uv_sphere(
            f"Nico_Olho_Branco_{side_s}",
            radius=0.058,
            segments=14,
            rings=10,
            location=(x_eye, -0.205, 0.27),
            mat=mats["eye_white"],
            col=col,
            parent=head,
            scale_xyz=(1.0, 0.45, 1.15),
            shade_smooth=True,
        )
        create_uv_sphere(
            f"Nico_Pupila_{side_s}",
            radius=0.036,
            segments=12,
            rings=8,
            location=(x_eye, -0.228, 0.27),
            mat=mats["eye_dark"],
            col=col,
            parent=head,
            scale_xyz=(1.0, 0.45, 1.15),
            shade_smooth=True,
        )
        create_uv_sphere(
            f"Nico_Brilho_Olho_{side_s}",
            radius=0.013,
            segments=8,
            rings=6,
            location=(x_eye - 0.015, -0.242, 0.29),
            mat=mats["eye_white"],
            col=col,
            parent=head,
            shade_smooth=True,
        )

    # Articulated Eyebrows for Expressions
    eyebrow_l = create_beveled_box(
        "Nico_Sobrancelha_L",
        size_xyz=(0.11, 0.04, 0.032),
        location=(-0.115, -0.232, 0.36),
        mat=mats["eyebrow_dark"],
        col=col,
        parent=head,
        bevel_width=0.008,
    )
    eyebrow_r = create_beveled_box(
        "Nico_Sobrancelha_R",
        size_xyz=(0.11, 0.04, 0.032),
        location=(0.115, -0.232, 0.36),
        mat=mats["eyebrow_dark"],
        col=col,
        parent=head,
        bevel_width=0.008,
    )

    # Articulated Mouth for Expressions
    mouth = create_beveled_box(
        "Nico_Boca",
        size_xyz=(0.12, 0.035, 0.035),
        location=(0.0, -0.228, 0.145),
        mat=mats["mouth_dark"],
        col=col,
        parent=head,
        bevel_width=0.01,
    )

    # Stylized Blue Cap (Fitted on top, angled slightly up in front so eyes stay 100% clear)
    create_beveled_box(
        "Nico_Bone_Copa",
        size_xyz=(0.53, 0.50, 0.19),
        location=(0.0, 0.01, 0.46),
        mat=mats["nico_cap_blue"],
        col=col,
        parent=head,
        bevel_width=0.06,
        bevel_segments=3,
        shade_smooth=True,
    )
    # Front Emblem on Cap
    create_beveled_box(
        "Nico_Bone_Emblema",
        size_xyz=(0.14, 0.03, 0.08),
        location=(0.0, -0.24, 0.47),
        mat=mats["awning_cream"],
        col=col,
        parent=head,
        bevel_width=0.008,
    )
    # Cap Visor (pointing forward -Y, slightly tilted up so eyebrows remain visible)
    create_beveled_box(
        "Nico_Bone_Aba",
        size_xyz=(0.46, 0.28, 0.042),
        location=(0.0, -0.29, 0.42),
        mat=mats["nico_cap_blue"],
        col=col,
        parent=head,
        rot=(math.radians(-10), 0.0, 0.0),
        bevel_width=0.015,
    )
    create_uv_sphere(
        "Nico_Bone_Botao",
        radius=0.035,
        segments=10,
        rings=6,
        location=(0.0, 0.01, 0.56),
        mat=mats["awning_cream"],
        col=col,
        parent=head,
        scale_xyz=(1.0, 1.0, 0.5),
    )

    # Articulated Arms (Shoulder -> Forearm -> Hand with Thumb)
    arms = {}
    for side_s, x_sign in (("L", -1.0), ("R", 1.0)):
        sh_pivot = create_empty(
            f"Nico_Arm_{side_s}",
            location=(x_sign * 0.29, 0.0, 0.45),
            col=col,
            parent=torso,
            empty_size=0.1,
        )
        # Orange short sleeve
        create_tapered_box(
            f"Nico_Manga_{side_s}",
            bottom_xy=(0.15, 0.15),
            top_xy=(0.17, 0.17),
            height_z=0.18,
            location=(x_sign * 0.02, 0.0, -0.07),
            mat=mats["nico_shirt"],
            col=col,
            parent=sh_pivot,
            bevel_width=0.02,
        )
        # Upper arm skin
        create_beveled_box(
            f"Nico_Braco_Sup_{side_s}",
            size_xyz=(0.11, 0.11, 0.16),
            location=(x_sign * 0.02, 0.0, -0.20),
            mat=mats["nico_skin"],
            col=col,
            parent=sh_pivot,
            bevel_width=0.02,
        )
        # Elbow / Forearm Pivot at Z = -0.26
        el_pivot = create_empty(
            f"Nico_Forearm_{side_s}",
            location=(x_sign * 0.02, 0.0, -0.26),
            col=col,
            parent=sh_pivot,
            empty_size=0.08,
        )
        create_tapered_box(
            f"Nico_Antebraco_{side_s}",
            bottom_xy=(0.095, 0.095),
            top_xy=(0.11, 0.11),
            height_z=0.22,
            location=(0.0, 0.0, -0.11),
            mat=mats["nico_skin"],
            col=col,
            parent=el_pivot,
            bevel_width=0.02,
        )
        # Natural Mitten Hand + Thumb at Z = -0.25
        create_beveled_box(
            f"Nico_Mao_Palma_{side_s}",
            size_xyz=(0.11, 0.13, 0.13),
            location=(0.0, -0.01, -0.25),
            mat=mats["nico_skin"],
            col=col,
            parent=el_pivot,
            bevel_width=0.028,
            shade_smooth=True,
        )
        create_beveled_box(
            f"Nico_Mao_Polegar_{side_s}",
            size_xyz=(0.045, 0.07, 0.05),
            location=(-x_sign * 0.04, -0.06, -0.23),
            mat=mats["nico_skin"],
            col=col,
            parent=el_pivot,
            bevel_width=0.015,
            shade_smooth=True,
        )
        arms[side_s] = (sh_pivot, el_pivot)

    # Articulated Legs (Hip -> Knee -> Ankle/Foot)
    # Note: Side "R" (+X local, closer to center of frame & stall) has the DAMAGED SHOE!
    legs = {}
    damaged_sole_pivot = None
    for side_s, x_sign in (("L", -1.0), ("R", 1.0)):
        hip_pivot = create_empty(
            f"Nico_Leg_{side_s}",
            location=(x_sign * 0.145, 0.0, 0.0),
            col=col,
            parent=pelvis,
            empty_size=0.1,
        )
        # Blue shorts leg
        create_tapered_box(
            f"Nico_Bermuda_Perna_{side_s}",
            bottom_xy=(0.19, 0.21),
            top_xy=(0.21, 0.23),
            height_z=0.26,
            location=(0.0, 0.0, -0.13),
            mat=mats["nico_shorts_blue"],
            col=col,
            parent=hip_pivot,
            bevel_width=0.02,
        )
        # Upper knee skin
        create_beveled_box(
            f"Nico_Coxa_Inf_{side_s}",
            size_xyz=(0.13, 0.14, 0.14),
            location=(0.0, 0.0, -0.30),
            mat=mats["nico_skin"],
            col=col,
            parent=hip_pivot,
            bevel_width=0.02,
        )
        # Knee Pivot at Z = -0.36
        knee_pivot = create_empty(
            f"Nico_Knee_{side_s}",
            location=(0.0, 0.0, -0.36),
            col=col,
            parent=hip_pivot,
            empty_size=0.08,
        )
        # Lower leg (shin)
        create_tapered_box(
            f"Nico_Canela_{side_s}",
            bottom_xy=(0.105, 0.11),
            top_xy=(0.125, 0.13),
            height_z=0.22,
            location=(0.0, 0.0, -0.11),
            mat=mats["nico_skin"],
            col=col,
            parent=knee_pivot,
            bevel_width=0.018,
        )
        # Sock above ankle
        create_beveled_box(
            f"Nico_Meia_{side_s}",
            size_xyz=(0.115, 0.12, 0.10),
            location=(0.0, 0.0, -0.25),
            mat=mats["awning_cream"],
            col=col,
            parent=knee_pivot,
            bevel_width=0.01,
        )
        # Ankle / Foot Pivot at Z = -0.30 (World Z = 0.12 when standing)
        foot_pivot = create_empty(
            f"Nico_Foot_{side_s}",
            location=(0.0, 0.0, -0.30),
            col=col,
            parent=knee_pivot,
            empty_size=0.08,
        )

        if side_s == "L":
            # Intact Sneaker (Bottom at Z = -0.12 relative to foot_pivot)
            create_beveled_box(
                "Nico_Tenis_Sola_L",
                size_xyz=(0.18, 0.36, 0.045),
                location=(0.0, -0.06, -0.0975),
                mat=mats["nico_shoe_sole"],
                col=col,
                parent=foot_pivot,
                bevel_width=0.01,
            )
            create_tapered_box(
                "Nico_Tenis_Corpo_L",
                bottom_xy=(0.17, 0.34),
                top_xy=(0.14, 0.24),
                height_z=0.10,
                location=(0.0, -0.05, -0.03),
                mat=mats["nico_shoe_body"],
                col=col,
                parent=foot_pivot,
                bevel_width=0.02,
            )
        else:
            # DAMAGED RIGHT SNEAKER ("Sapato Danificado")
            # Back heel sole (intact)
            create_beveled_box(
                "Nico_Tenis_SolaTraseira_R",
                size_xyz=(0.18, 0.18, 0.045),
                location=(0.0, 0.03, -0.0975),
                mat=mats["nico_shoe_sole"],
                col=col,
                parent=foot_pivot,
                bevel_width=0.008,
            )
            # Flapping Front Sole Pivot (hinged under arch at Y = -0.04, Z = -0.095)
            damaged_sole_pivot = create_empty(
                "Nico_Sola_Descolada_Pivot_R",
                location=(0.0, -0.04, -0.095),
                col=col,
                parent=foot_pivot,
                empty_size=0.06,
            )
            create_beveled_box(
                "Nico_Tenis_SolaFrontal_R",
                size_xyz=(0.185, 0.21, 0.04),
                location=(0.0, -0.10, -0.005),
                mat=mats["nico_shoe_sole"],
                col=col,
                parent=damaged_sole_pivot,
                bevel_width=0.008,
            )
            # Worn/ripped upper body of right shoe
            create_tapered_box(
                "Nico_Tenis_Corpo_R",
                bottom_xy=(0.175, 0.28),
                top_xy=(0.14, 0.22),
                height_z=0.10,
                location=(0.0, -0.02, -0.03),
                mat=mats["nico_shoe_body"],
                col=col,
                parent=foot_pivot,
                bevel_width=0.018,
            )
            # Ripped hole dark edge at the toe
            create_beveled_box(
                "Nico_Tenis_Rasgo_R",
                size_xyz=(0.13, 0.08, 0.06),
                location=(0.0, -0.16, -0.04),
                mat=mats["wood_dark"],
                col=col,
                parent=foot_pivot,
                bevel_width=0.01,
            )
            # Bright Red Sock & Wiggling Big Toe sticking out of the broken shoe!
            create_uv_sphere(
                "Nico_Dedao_MeiaVermelha_R",
                radius=0.052,
                segments=12,
                rings=8,
                location=(0.02, -0.21, -0.042),
                mat=mats["nico_sock_red"],
                col=col,
                parent=foot_pivot,
                scale_xyz=(0.95, 1.25, 0.85),
                shade_smooth=True,
            )
            create_uv_sphere(
                "Nico_Dedao_Pele_R",
                radius=0.038,
                segments=10,
                rings=8,
                location=(0.02, -0.25, -0.040),
                mat=mats["nico_skin"],
                col=col,
                parent=foot_pivot,
                scale_xyz=(0.95, 1.15, 0.85),
                shade_smooth=True,
            )

        legs[side_s] = (hip_pivot, knee_pivot, foot_pivot)

    return {
        "root": root,
        "pelvis": pelvis,
        "torso": torso,
        "head": head,
        "eyebrow_l": eyebrow_l,
        "eyebrow_r": eyebrow_r,
        "mouth": mouth,
        "arm_l": arms["L"][0],
        "forearm_l": arms["L"][1],
        "arm_r": arms["R"][0],
        "forearm_r": arms["R"][1],
        "leg_l": legs["L"][0],
        "knee_l": legs["L"][1],
        "foot_l": legs["L"][2],
        "leg_r": legs["R"][0],
        "knee_r": legs["R"][1],
        "foot_r": legs["R"][2],
        "damaged_sole": damaged_sole_pivot,
    }


def build_character_seller(col, mats):
    """Build a stylized low-poly Shoe Seller standing behind the stall counter."""
    pos = config.POSITIONS["seller_pos"]
    root = create_empty("Vendedor_Root", pos, col, rot=(0.0, 0.0, math.radians(-16)), empty_size=0.18)

    # Torso (visible above the counter)
    torso = create_empty("Vendedor_Torso", (0.0, 0.0, 0.82), col, parent=root, empty_size=0.12)
    create_tapered_box(
        "Vendedor_Camisa",
        bottom_xy=(0.44, 0.28),
        top_xy=(0.48, 0.30),
        height_z=0.56,
        location=(0.0, 0.0, 0.28),
        mat=mats["seller_shirt"],
        col=col,
        parent=torso,
        bevel_width=0.025,
    )
    # Cobbler Green Apron
    create_beveled_box(
        "Vendedor_Avental",
        size_xyz=(0.36, 0.31, 0.46),
        location=(0.0, -0.01, 0.24),
        mat=mats["seller_apron"],
        col=col,
        parent=torso,
        bevel_width=0.015,
    )

    # Head Pivot
    head = create_empty("Vendedor_Head", (0.0, 0.0, 0.58), col, parent=torso, empty_size=0.12)
    create_beveled_box(
        "Vendedor_Cabeca",
        size_xyz=(0.44, 0.40, 0.42),
        location=(0.0, 0.0, 0.24),
        mat=mats["nico_skin"],
        col=col,
        parent=head,
        bevel_width=0.09,
        bevel_segments=3,
        shade_smooth=True,
    )
    # Big Mustache
    create_beveled_box(
        "Vendedor_Bigode",
        size_xyz=(0.24, 0.08, 0.06),
        location=(0.0, -0.21, 0.17),
        mat=mats["wood_dark"],
        col=col,
        parent=head,
        bevel_width=0.015,
    )
    # Eyes
    for side_s, x_eye in (("L", -0.10), ("R", 0.10)):
        create_uv_sphere(
            f"Vendedor_Olho_{side_s}",
            radius=0.032,
            segments=10,
            rings=8,
            location=(x_eye, -0.20, 0.27),
            mat=mats["eye_dark"],
            col=col,
            parent=head,
        )
    # Flat Cap / Hat
    create_beveled_box(
        "Vendedor_Boina",
        size_xyz=(0.46, 0.44, 0.10),
        location=(0.0, -0.02, 0.46),
        mat=mats["wood_warm"],
        col=col,
        parent=head,
        bevel_width=0.03,
    )

    # Arms
    arm_l = create_empty("Vendedor_Arm_L", (-0.28, 0.0, 0.48), col, parent=torso, empty_size=0.08)
    create_beveled_box(
        "Vendedor_Braco_L",
        size_xyz=(0.13, 0.13, 0.38),
        location=(-0.02, 0.0, -0.18),
        mat=mats["seller_shirt"],
        col=col,
        parent=arm_l,
        bevel_width=0.02,
    )
    arm_r = create_empty("Vendedor_Arm_R", (0.28, 0.0, 0.48), col, parent=torso, empty_size=0.08)
    create_beveled_box(
        "Vendedor_Braco_R",
        size_xyz=(0.13, 0.13, 0.38),
        location=(0.02, 0.0, -0.18),
        mat=mats["seller_shirt"],
        col=col,
        parent=arm_r,
        bevel_width=0.02,
    )

    return {
        "root": root,
        "torso": torso,
        "head": head,
        "arm_l": arm_l,
        "arm_r": arm_r,
    }

