"""Procedural environment & market stall V3: refined proportions, wood detail, stepping stones, and background depth."""

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


def _build_stylized_tree(name, pos, scale, mats, col, pine=False):
    """Create a reusable stylized tree (either layered pine or soft polyhedral canopy)."""
    root = create_empty(f"{name}_Root", pos, col, empty_size=0.1)
    trunk_h = 0.98 * scale
    create_cylinder(
        f"{name}_Tronco",
        radius1=0.13 * scale,
        radius2=0.08 * scale,
        depth=trunk_h,
        vertices=10,
        location=(0.0, 0.0, trunk_h * 0.5),
        mat=mats["tree_trunk"],
        col=col,
        parent=root,
        bevel_width=0.01,
        shade_smooth=True,
    )
    if pine:
        layers = [
            (0.62 * scale, 0.85 * scale, 0.95 * scale, "foliage_dark"),
            (0.48 * scale, 0.72 * scale, 1.42 * scale, "foliage_light"),
            (0.32 * scale, 0.58 * scale, 1.82 * scale, "foliage_light"),
        ]
        for idx, (rad, h, z, mkey) in enumerate(layers):
            create_cylinder(
                f"{name}_Copa_{idx}",
                radius1=rad,
                radius2=0.02,
                depth=h,
                vertices=9,
                location=(0.0, 0.0, z),
                mat=mats[mkey],
                col=col,
                parent=root,
                bevel_width=0.015,
            )
    else:
        blobs = [
            ((0.0, 0.0, 1.25 * scale), 0.55 * scale, (1.06, 1.0, 0.92), "foliage_light"),
            ((-0.28 * scale, 0.12 * scale, 1.08 * scale), 0.38 * scale, (1.0, 1.0, 0.90), "foliage_dark"),
            ((0.26 * scale, -0.08 * scale, 1.12 * scale), 0.36 * scale, (1.0, 1.0, 0.90), "foliage_dark"),
            ((0.05 * scale, 0.18 * scale, 1.50 * scale), 0.34 * scale, (1.0, 1.0, 0.95), "foliage_light"),
        ]
        for idx, (loc, rad, sc, mkey) in enumerate(blobs):
            create_icosphere(
                f"{name}_Copa_{idx}",
                radius=rad,
                subdivisions=2,
                location=loc,
                mat=mats[mkey],
                col=col,
                parent=root,
                scale_xyz=sc,
            )
    return root


def _build_distant_house(name, pos, rot_z, scale, wall_mat, roof_mat, mats, col):
    """Create a cozy background village house to frame the horizon without visual clutter."""
    root = create_empty(f"{name}_Root", pos, col, rot=(0.0, 0.0, rot_z), empty_size=0.1)
    w, d, h = 1.65 * scale, 1.35 * scale, 1.25 * scale
    create_beveled_box(
        f"{name}_Paredes",
        size_xyz=(w, d, h),
        location=(0.0, 0.0, h * 0.5),
        mat=wall_mat,
        col=col,
        parent=root,
        bevel_width=0.025,
    )
    create_gabled_roof(
        f"{name}_Telhado",
        width_x=w * 1.14,
        depth_y=d * 1.16,
        height_z=0.72 * scale,
        location=(0.0, 0.0, h),
        mat=roof_mat,
        col=col,
        parent=root,
        bevel_width=0.02,
    )
    create_beveled_box(
        f"{name}_Porta",
        size_xyz=(0.34 * scale, 0.06 * scale, 0.62 * scale),
        location=(0.0, -d * 0.5 - 0.01, 0.31 * scale),
        mat=mats["wood_dark"],
        col=col,
        parent=root,
        bevel_width=0.01,
    )
    return root


def _build_Wooden_handcart(name, pos, mats, col):
    """Create a charming 2-wheel wooden handcart (Carrinho de Mão / Feira) that holds Nico's 40kg potato sack."""
    # Rotated -95 deg around Z so the cart sits parallel to the path and handles point toward -X (away from Nico's legs)
    cart_root = create_empty(f"{name}_Root", pos, col, rot=(0.0, 0.0, math.radians(-95)), empty_size=0.15)

    # Wooden bed platform at Z = 0.28 (top surface at Z = 0.32)
    for idx, px in enumerate((-0.22, -0.075, 0.075, 0.22)):
        create_beveled_box(
            f"{name}_Tabua_Base_{idx+1}",
            size_xyz=(0.135, 0.72, 0.045),
            location=(px, 0.0, 0.295),
            mat=mats["wood_light"] if idx % 2 == 0 else mats["wood_warm"],
            col=col,
            parent=cart_root,
            bevel_width=0.008,
        )

    # Side & back wooden rails
    for side_s, sx in (("L", -0.28), ("R", 0.28)):
        create_beveled_box(
            f"{name}_Lateral_{side_s}",
            size_xyz=(0.038, 0.70, 0.14),
            location=(sx, 0.0, 0.39),
            mat=mats["wood_warm"],
            col=col,
            parent=cart_root,
            bevel_width=0.008,
        )
        # Extended handles toward -Y/back
        create_cylinder(
            f"{name}_Cabo_{side_s}",
            radius1=0.024,
            radius2=0.020,
            depth=0.38,
            vertices=10,
            location=(sx, -0.46, 0.32),
            mat=mats["wood_dark"],
            col=col,
            parent=cart_root,
            rot=(math.radians(82), 0.0, 0.0),
            shade_smooth=True,
        )
        # Spoked Wooden Wheel with dark iron rim at Y = +0.16, Z = 0.16
        create_cylinder(
            f"{name}_Roda_Aro_{side_s}",
            radius1=0.16,
            radius2=0.16,
            depth=0.045,
            vertices=18,
            location=(sx + (0.04 if sx > 0 else -0.04), 0.14, 0.16),
            mat=mats["iron_dark"],
            col=col,
            parent=cart_root,
            rot=(0.0, math.radians(90), 0.0),
            bevel_width=0.006,
            shade_smooth=True,
        )
        create_cylinder(
            f"{name}_Roda_Miolo_{side_s}",
            radius1=0.125,
            radius2=0.125,
            depth=0.052,
            vertices=16,
            location=(sx + (0.04 if sx > 0 else -0.04), 0.14, 0.16),
            mat=mats["wood_warm"],
            col=col,
            parent=cart_root,
            rot=(0.0, math.radians(90), 0.0),
            bevel_width=0.005,
            shade_smooth=True,
        )
        # Front resting leg at Y = -0.24 so the cart sits level on the ground
        create_beveled_box(
            f"{name}_Pe_Apoio_{side_s}",
            size_xyz=(0.04, 0.04, 0.28),
            location=(sx * 0.82, -0.24, 0.14),
            mat=mats["wood_dark"],
            col=col,
            parent=cart_root,
            bevel_width=0.006,
        )

    # Extra loose golden potatoes sitting in the cart bed around the main sack
    for idx, (px, py, pz) in enumerate(((-0.16, 0.18, 0.35), (0.17, 0.16, 0.35), (-0.14, -0.20, 0.35), (0.15, -0.18, 0.35))):
        create_uv_sphere(
            f"{name}_Batata_Extra_{idx+1}",
            radius=0.062,
            segments=12,
            rings=8,
            location=(px, py, pz),
            mat=mats["potato_gold"],
            col=col,
            parent=cart_root,
            scale_xyz=(1.2, 0.9, 0.8),
            shade_smooth=True,
        )

    return cart_root


def build_pair_of_new_shoes(name, pos, rot_z, mats, col):
    """Build the gleaming pair of desirable new red & gold sneakers on an elevated display stand."""
    root = create_empty(f"{name}_Root", pos, col, rot=(0.0, 0.0, rot_z), empty_size=0.12)

    # Tiered Display Stand (Stand base + angled velvet/cream top pad)
    create_beveled_box(
        f"{name}_Pedestal_Madeira",
        size_xyz=(0.56, 0.38, 0.045),
        location=(0.0, 0.0, -0.035),
        mat=mats["wood_dark"],
        col=col,
        parent=root,
        bevel_width=0.01,
    )
    create_beveled_box(
        f"{name}_Base_Expositor",
        size_xyz=(0.52, 0.34, 0.038),
        location=(0.0, 0.0, 0.005),
        mat=mats["awning_cream"],
        col=col,
        parent=root,
        bevel_width=0.01,
    )

    for side_label, x_off, yaw in (("Esq", -0.13, math.radians(-8)), ("Dir", 0.13, math.radians(8))):
        shoe_grp = create_empty(
            f"{name}_{side_label}",
            location=(x_off, 0.0, 0.024),
            col=col,
            parent=root,
            rot=(math.radians(6), 0.0, yaw),
            empty_size=0.06,
        )
        # Thick white sneaker outsole
        create_beveled_box(
            f"{name}_{side_label}_Sola",
            size_xyz=(0.155, 0.32, 0.038),
            location=(0.0, 0.0, 0.019),
            mat=mats["nico_shoe_sole"],
            col=col,
            parent=shoe_grp,
            bevel_width=0.012,
            subsurf_levels=1,
            shade_smooth=True,
        )
        # Vibrant Red Sneaker Upper
        create_tapered_box(
            f"{name}_{side_label}_Corpo",
            bottom_xy=(0.148, 0.29),
            top_xy=(0.122, 0.20),
            height_z=0.105,
            location=(0.0, 0.01, 0.088),
            mat=mats["new_shoe_red"],
            col=col,
            parent=shoe_grp,
            bevel_width=0.022,
            subsurf_levels=1,
            shade_smooth=True,
        )
        # White Rubber Toe Cap
        create_uv_sphere(
            f"{name}_{side_label}_Biqueira",
            radius=0.065,
            segments=14,
            rings=10,
            location=(0.0, -0.115, 0.052),
            mat=mats["nico_shoe_sole"],
            col=col,
            parent=shoe_grp,
            scale_xyz=(1.04, 0.75, 0.45),
            shade_smooth=True,
        )
        # Gleaming Gold Side Star / Emblem & Laces
        create_beveled_box(
            f"{name}_{side_label}_FaixaOuro",
            size_xyz=(0.156, 0.065, 0.042),
            location=(0.0, -0.01, 0.085),
            mat=mats["new_shoe_gold"],
            col=col,
            parent=shoe_grp,
            bevel_width=0.008,
            shade_smooth=True,
        )
        for l_idx, ly in enumerate((-0.03, -0.065)):
            create_beveled_box(
                f"{name}_{side_label}_Cadarco_{l_idx+1}",
                size_xyz=(0.09, 0.018, 0.012),
                location=(0.0, ly, 0.132 - l_idx * 0.012),
                mat=mats["new_shoe_gold"],
                col=col,
                parent=shoe_grp,
                rot=(math.radians(18), 0.0, 0.0),
                bevel_width=0.004,
            )

    return root


def build_village_and_fair(cols, mats):
    """Build the V3 village environment, stone path, handcart, and market stall."""
    col_vila = cols["Col_Cenario_Vila"]
    col_feira = cols["Col_Feira_Barraca"]

    # 1. Ground & Rolling Hills
    create_beveled_box(
        "Chao_Grama_Principal",
        size_xyz=(28.0, 26.0, 0.4),
        location=(0.0, 2.0, -0.20),
        mat=mats["grass_base"],
        col=col_vila,
        bevel_width=0.04,
    )
    hills = [
        ("Colina_Fundo_Esq", (-5.8, 9.8, -0.4), 4.6, (1.6, 1.0, 0.52), "grass_accent"),
        ("Colina_Fundo_Dir", (5.2, 10.6, -0.5), 5.0, (1.7, 1.1, 0.56), "grass_base"),
        ("Colina_Centro", (0.2, 12.8, -0.6), 5.6, (2.0, 1.0, 0.50), "grass_accent"),
    ]
    for hname, hpos, hrad, hscale, mkey in hills:
        create_icosphere(
            hname,
            radius=hrad,
            subdivisions=2,
            location=hpos,
            mat=mats[mkey],
            col=col_vila,
            scale_xyz=hscale,
        )

    # 2. Dirt Path & Stepping Stones (including the Cold Open stumble stone!)
    create_beveled_box(
        "Caminho_Terra_Feira",
        size_xyz=(6.8, 2.35, 0.04),
        location=(-0.55, -0.45, -0.012),
        mat=mats["dirt_path"],
        col=col_vila,
        bevel_width=0.015,
    )

    stones = [
        (-2.55, -0.68, 0.40, 0.28, 8, "stone_grey", 0.028),
        # Stone right where Nico's detached right sole steps in the Cold Open!
        (-2.02, -0.56, 0.38, 0.26, -10, "stone_warm", 0.036),
        (-1.55, -0.58, 0.42, 0.28, 12, "stone_grey", 0.028),
        (-1.02, -0.50, 0.40, 0.28, -6, "stone_warm", 0.028),
        (-0.48, -0.48, 0.44, 0.30, 10, "stone_grey", 0.028),
        (0.05, -0.45, 0.42, 0.28, -5, "stone_warm", 0.028),
    ]
    for idx, (sx, sy, sw, sd, srot, smat, sh) in enumerate(stones):
        create_beveled_box(
            f"Pedra_Caminho_{idx+1:02d}",
            size_xyz=(sw, sd, sh),
            location=(sx, sy, sh * 0.35),
            mat=mats[smat],
            col=col_vila,
            rot=(0.0, 0.0, math.radians(srot)),
            bevel_width=0.008,
        )

    # 3. Trees, Bushes, Distant Houses, and Clouds (balanced so center frame stays clean)
    _build_distant_house(
        "Casa_Vila_Esq",
        pos=(-4.8, 6.2, 0.0),
        rot_z=math.radians(20),
        scale=1.02,
        wall_mat=mats["house_wall_1"],
        roof_mat=mats["house_roof_1"],
        mats=mats,
        col=col_vila,
    )
    _build_distant_house(
        "Casa_Vila_Dir",
        pos=(4.6, 5.8, 0.0),
        rot_z=math.radians(-22),
        scale=0.95,
        wall_mat=mats["house_wall_2"],
        roof_mat=mats["house_roof_2"],
        mats=mats,
        col=col_vila,
    )

    trees = [
        ("Arvore_Esq_01", (-3.85, 2.2, 0.0), 1.15, False),
        ("Arvore_Esq_02", (-2.65, 4.5, 0.0), 1.28, True),
        ("Arvore_Centro_Fundo", (-0.85, 6.5, 0.0), 1.35, True),
        ("Arvore_Dir_01", (3.65, 2.5, 0.0), 1.18, False),
    ]
    for tname, tpos, tscale, is_pine in trees:
        _build_stylized_tree(tname, tpos, tscale, mats, col_vila, pine=is_pine)

    bushes = [
        ("Arbusto_01", (-3.15, 0.85, 0.18), 0.28, "foliage_light"),
        ("Arbusto_02", (2.95, 0.90, 0.16), 0.26, "foliage_dark"),
    ]
    for bname, bpos, brad, bmkey in bushes:
        create_icosphere(
            bname,
            radius=brad,
            subdivisions=2,
            location=bpos,
            mat=mats[bmkey],
            col=col_vila,
            scale_xyz=(1.25, 1.0, 0.72),
        )

    clouds = [
        ("Nuvem_01", (-2.2, 8.5, 4.4), 0.52),
        ("Nuvem_02", (1.2, 9.0, 4.7), 0.60),
    ]
    for cname, cpos, crad in clouds:
        c_root = create_empty(f"{cname}_Root", cpos, col_vila, empty_size=0.1)
        for idx, (ox, oz, r_mult) in enumerate(((-0.45, -0.05, 0.78), (0.0, 0.08, 1.0), (0.48, -0.04, 0.82))):
            create_icosphere(
                f"{cname}_Puff_{idx}",
                radius=crad * r_mult,
                subdivisions=2,
                location=(ox, 0.0, oz),
                mat=mats["cloud_white"],
                col=col_vila,
                parent=c_root,
                scale_xyz=(1.2, 0.8, 0.68),
            )

    # 4. Wooden Handcart for Nico's 40kg Potato Sack
    handcart = _build_Wooden_handcart(
        "Carrinho_Batatas",
        pos=config.POSITIONS["cart_pos"],
        mats=mats,
        col=col_feira,
    )

    # 5. Refined Cobbler Market Stall (Barraca de Sapatos V3)
    stall_root = create_empty("Barraca_Sapateiro_Root", (0.0, 0.0, 0.0), col_feira, empty_size=0.2)

    # Raised wooden deck platform
    create_beveled_box(
        "Barraca_Deck_Piso",
        size_xyz=(2.48, 2.05, 0.08),
        location=(1.18, 0.35, 0.04),
        mat=mats["wood_dark"],
        col=col_feira,
        parent=stall_root,
        bevel_width=0.015,
    )

    # Counter Base & Recessed Cream Panel
    create_beveled_box(
        "Balcao_Corpo_Frente",
        size_xyz=(1.76, 0.62, 0.82),
        location=(1.02, -0.15, 0.49),
        mat=mats["stall_wall"],
        col=col_feira,
        parent=stall_root,
        bevel_width=0.02,
    )
    for idx, vx in enumerate((0.20, 0.75, 1.30, 1.84)):
        create_beveled_box(
            f"Balcao_Ripa_Vertical_{idx+1}",
            size_xyz=(0.075, 0.66, 0.84),
            location=(vx, -0.15, 0.49),
            mat=mats["wood_warm"],
            col=col_feira,
            parent=stall_root,
            bevel_width=0.01,
        )

    # Layered Plank Countertop (Top surface at Z = 0.96)
    for p_idx, py in enumerate((-0.36, -0.15, 0.06)):
        create_beveled_box(
            f"Balcao_Tampo_Prancha_{p_idx+1}",
            size_xyz=(1.94, 0.21, 0.07),
            location=(1.02, py, 0.925),
            mat=mats["wood_light"] if p_idx != 1 else mats["wood_warm"],
            col=col_feira,
            parent=stall_root,
            bevel_width=0.012,
        )

    # Back Wall & Display Shelves (creates warm interior depth behind the seller)
    create_beveled_box(
        "Barraca_Parede_Fundo",
        size_xyz=(1.98, 0.12, 1.65),
        location=(1.15, 1.12, 1.18),
        mat=mats["stall_wall"],
        col=col_feira,
        parent=stall_root,
        bevel_width=0.02,
    )
    for s_idx, sz in enumerate((1.22, 1.66)):
        create_beveled_box(
            f"Barraca_Prateleira_{s_idx+1}",
            size_xyz=(1.76, 0.28, 0.05),
            location=(1.15, 0.96, sz),
            mat=mats["wood_warm"],
            col=col_feira,
            parent=stall_root,
            bevel_width=0.008,
        )
        for b_idx, (bx, bmat) in enumerate(((0.58, "awning_teal"), (1.15, "awning_red"), (1.68, "new_shoe_gold"))):
            create_beveled_box(
                f"Caixa_Estoque_{s_idx+1}_{b_idx+1}",
                size_xyz=(0.30, 0.20, 0.15),
                location=(bx, 0.95, sz + 0.10),
                mat=mats[bmat],
                col=col_feira,
                parent=stall_root,
                bevel_width=0.01,
            )
            create_beveled_box(
                f"Caixa_Tampa_{s_idx+1}_{b_idx+1}",
                size_xyz=(0.32, 0.22, 0.035),
                location=(bx, 0.95, sz + 0.18),
                mat=mats["awning_cream"],
                col=col_feira,
                parent=stall_root,
                bevel_width=0.006,
            )

    # 4 Corner Wooden Posts supporting the Awning (inset at X=0.30 so the left post never tangents Nico's head silhouette)
    posts = [
        ("Poste_Frontal_Esq", (0.30, -0.38, 1.54)),
        ("Poste_Frontal_Dir", (2.06, -0.38, 1.54)),
        ("Poste_Traseiro_Esq", (0.30, 1.06, 1.54)),
        ("Poste_Traseiro_Dir", (2.06, 1.06, 1.54)),
    ]
    for pname, ppos in posts:
        create_beveled_box(
            pname,
            size_xyz=(0.10, 0.10, 2.92),
            location=ppos,
            mat=mats["wood_dark"],
            col=col_feira,
            parent=stall_root,
            bevel_width=0.012,
        )

    # Striped Red & Cream Awning (Z = 2.94 so it never clips the Refusal / Milk signs)
    awning_root = create_empty(
        "Toldo_Barraca_Root",
        location=(1.14, 0.32, 2.94),
        col=col_feira,
        parent=stall_root,
        rot=(math.radians(9), 0.0, 0.0),
        empty_size=0.1,
    )
    num_stripes = 7
    stripe_w = 2.12 / num_stripes
    for i in range(num_stripes):
        sx = -1.06 + (i + 0.5) * stripe_w
        smat = mats["awning_red"] if i % 2 == 0 else mats["awning_cream"]
        create_beveled_box(
            f"Toldo_Faixa_{i+1}",
            size_xyz=(stripe_w * 1.01, 1.86, 0.09),
            location=(sx, 0.0, 0.0),
            mat=smat,
            col=col_feira,
            parent=awning_root,
            bevel_width=0.015,
        )
        create_beveled_box(
            f"Toldo_Babadinho_{i+1}",
            size_xyz=(stripe_w * 0.96, 0.07, 0.18),
            location=(sx, -0.92, -0.10),
            mat=smat,
            col=col_feira,
            parent=awning_root,
            bevel_width=0.012,
        )

    # Gleaming Pair of New Shoes on the Elevated Display Pedestal (Right side of Counter)
    shoes_display = build_pair_of_new_shoes(
        "Par_Sapatos_Novos",
        pos=config.POSITIONS["shoes_on_counter"],
        rot_z=math.radians(-18),
        mats=mats,
        col=col_feira,
    )
    shoes_display.parent = stall_root

    return {
        "stall_root": stall_root,
        "handcart": handcart,
        "shoes_display": shoes_display,
    }
