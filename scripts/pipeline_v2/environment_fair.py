"""Procedural low-poly environment: village ground, stone path, market stall, crates, trees, and distant houses."""

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


def _build_stylized_tree(name, pos, scale, mats, col, pine=False):
    """Create a reusable stylized low-poly tree (either pine cone layers or polyhedral canopy)."""
    root = create_empty(f"{name}_Root", pos, col, empty_size=0.1)
    # Trunk
    trunk_h = 0.95 * scale
    create_cylinder(
        f"{name}_Tronco",
        radius1=0.13 * scale,
        radius2=0.08 * scale,
        depth=trunk_h,
        vertices=7,
        location=(0.0, 0.0, trunk_h * 0.5),
        mat=mats["tree_trunk"],
        col=col,
        parent=root,
        bevel_width=0.01,
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
                vertices=7,
                location=(0.0, 0.0, z),
                mat=mats[mkey],
                col=col,
                parent=root,
                bevel_width=0.015,
            )
    else:
        blobs = [
            ((0.0, 0.0, 1.25 * scale), 0.55 * scale, (1.05, 1.0, 0.92), "foliage_light"),
            ((-0.28 * scale, 0.12 * scale, 1.08 * scale), 0.38 * scale, (1.0, 1.0, 0.9), "foliage_dark"),
            ((0.26 * scale, -0.10 * scale, 1.12 * scale), 0.36 * scale, (1.0, 1.0, 0.9), "foliage_light"),
            ((0.0, 0.05 * scale, 1.58 * scale), 0.35 * scale, (1.0, 1.0, 0.95), "foliage_light"),
        ]
        for idx, (bpos, rad, sc, mkey) in enumerate(blobs):
            create_icosphere(
                f"{name}_Copa_{idx}",
                radius=rad,
                subdivisions=2,
                location=bpos,
                mat=mats[mkey],
                col=col,
                parent=root,
                scale_xyz=sc,
                shade_smooth=False,
            )
    return root


def _build_distant_house(name, pos, rot_z, wall_mat, roof_mat, mats, col, scale=1.0):
    """Create a simple low-poly background house to establish the village setting without clutter."""
    root = create_empty(f"{name}_Root", pos, col, rot=(0.0, 0.0, rot_z), empty_size=0.1)
    w, d, h = 1.65 * scale, 1.35 * scale, 1.25 * scale
    create_beveled_box(
        f"{name}_Corpo",
        size_xyz=(w, d, h),
        location=(0.0, 0.0, h * 0.5),
        mat=wall_mat,
        col=col,
        parent=root,
        bevel_width=0.02,
    )
    create_gabled_roof(
        f"{name}_Telhado",
        width_x=w * 1.14,
        depth_y=d * 1.16,
        height_z=0.68 * scale,
        location=(0.0, 0.0, h),
        mat=roof_mat,
        col=col,
        parent=root,
        bevel_width=0.02,
    )
    # Simple door and warm window
    create_beveled_box(
        f"{name}_Porta",
        size_xyz=(0.34 * scale, 0.06 * scale, 0.62 * scale),
        location=(-0.22 * scale, -d * 0.5, 0.31 * scale),
        mat=mats["wood_warm"],
        col=col,
        parent=root,
        bevel_width=0.01,
    )
    create_beveled_box(
        f"{name}_Janela",
        size_xyz=(0.36 * scale, 0.06 * scale, 0.36 * scale),
        location=(0.32 * scale, -d * 0.5, 0.68 * scale),
        mat=mats["awning_cream"],
        col=col,
        parent=root,
        bevel_width=0.01,
    )
    return root


def _build_crate_with_items(name, pos, rot_z, item_mat, mats, col):
    """Create a small wooden market crate filled with stylized round items."""
    root = create_empty(f"{name}_Root", pos, col, rot=(0.0, 0.0, rot_z), empty_size=0.08)
    create_tapered_box(
        f"{name}_Caixa",
        bottom_xy=(0.42, 0.32),
        top_xy=(0.48, 0.36),
        height_z=0.26,
        location=(0.0, 0.0, 0.13),
        mat=mats["wood_light"],
        col=col,
        parent=root,
        bevel_width=0.015,
    )
    offsets = [(-0.11, -0.06, 0.24), (0.0, 0.05, 0.25), (0.11, -0.04, 0.24), (-0.04, 0.02, 0.30)]
    for idx, opos in enumerate(offsets):
        create_icosphere(
            f"{name}_Item_{idx}",
            radius=0.085,
            subdivisions=2,
            location=opos,
            mat=item_mat,
            col=col,
            parent=root,
        )
    return root


def _build_pair_of_new_shoes(name, pos, rot_z, mats, col):
    """Create the gleaming pair of brand-new sneakers on a display cushion on the counter."""
    root = create_empty(f"{name}_Root", pos, col, rot=(0.0, 0.0, rot_z), empty_size=0.1)
    # Display pedestal/cushion
    create_beveled_box(
        f"{name}_Pedestal",
        size_xyz=(0.56, 0.40, 0.06),
        location=(0.0, 0.0, 0.03),
        mat=mats["awning_cream"],
        col=col,
        parent=root,
        bevel_width=0.015,
    )
    for side, x_off in (("L", -0.13), ("R", 0.13)):
        shoe_rot = (0.0, 0.0, math.radians(-12 if side == "L" else 8))
        s_root = create_empty(f"{name}_{side}", (x_off, 0.0, 0.06), col, parent=root, rot=shoe_rot, empty_size=0.05)
        # White sole
        create_beveled_box(
            f"{name}_Sola_{side}",
            size_xyz=(0.15, 0.31, 0.045),
            location=(0.0, -0.02, 0.022),
            mat=mats["nico_shoe_sole"],
            col=col,
            parent=s_root,
            bevel_width=0.01,
        )
        # Vibrant Red & Gold upper body
        create_tapered_box(
            f"{name}_Corpo_{side}",
            bottom_xy=(0.145, 0.29),
            top_xy=(0.12, 0.22),
            height_z=0.10,
            location=(0.0, -0.01, 0.09),
            mat=mats["new_shoe_red"],
            col=col,
            parent=s_root,
            bevel_width=0.02,
        )
        # Golden stripe / tongue accent
        create_beveled_box(
            f"{name}_DetalheOuro_{side}",
            size_xyz=(0.152, 0.08, 0.06),
            location=(0.0, -0.02, 0.09),
            mat=mats["new_shoe_gold"],
            col=col,
            parent=s_root,
            bevel_width=0.01,
        )
    return root


def build_village_and_fair(cols, mats):
    """Construct the village ground, stone path, background houses, trees, and the shoe stall."""
    col_vila = cols["Col_Cenario_Vila"]
    col_feira = cols["Col_Feira_Barraca"]

    # 1. Ground Base (Top surface at Z = 0.0)
    create_beveled_box(
        "Chao_Vila_Grama",
        size_xyz=(28.0, 28.0, 0.40),
        location=(0.0, 2.5, -0.20),
        mat=mats["grass_base"],
        col=col_vila,
        bevel_width=0.05,
    )

    # Soft rolling low-poly hills in the distant background
    create_icosphere(
        "Colina_Fundo_Esq",
        radius=4.5,
        subdivisions=2,
        location=(-5.5, 11.5, -1.8),
        mat=mats["grass_accent"],
        col=col_vila,
        scale_xyz=(1.8, 1.1, 0.65),
    )
    create_icosphere(
        "Colina_Fundo_Dir",
        radius=5.0,
        subdivisions=2,
        location=(5.0, 12.2, -2.0),
        mat=mats["grass_base"],
        col=col_vila,
        scale_xyz=(1.9, 1.1, 0.68),
    )

    # 2. Dirt Path & Cobblestones leading from left (-X) to the market stall (+X)
    create_beveled_box(
        "Caminho_Terra_Principal",
        size_xyz=(5.8, 1.35, 0.02),
        location=(-0.95, -0.58, 0.005),
        mat=mats["dirt_path"],
        col=col_vila,
        bevel_width=0.01,
    )

    stones = [
        (-3.20, -0.68, 0.36, 0.26, 0.1, "stone_grey"),
        (-2.72, -0.46, 0.32, 0.24, -0.2, "stone_warm"),
        (-2.25, -0.66, 0.42, 0.30, 0.05, "stone_grey"),
        (-1.75, -0.45, 0.30, 0.24, 0.25, "stone_warm"),
        (-1.42, -0.60, 0.40, 0.30, -0.1, "stone_grey"),
        (-0.95, -0.52, 0.35, 0.26, 0.15, "stone_warm"),
        (-0.48, -0.64, 0.38, 0.28, -0.12, "stone_grey"),
        (-0.02, -0.48, 0.34, 0.25, 0.08, "stone_warm"),
        (0.42, -0.58, 0.38, 0.28, -0.05, "stone_grey"),
    ]
    for idx, (sx, sy, sw, sd, srot, smat) in enumerate(stones):
        create_beveled_box(
            f"Pedra_Caminho_{idx+1:02d}",
            size_xyz=(sw, sd, 0.03),
            location=(sx, sy, 0.012),
            mat=mats[smat],
            col=col_vila,
            rot=(0.0, 0.0, srot),
            bevel_width=0.012,
        )

    # 3. Stylized Trees and Bushes framing the diorama
    _build_stylized_tree("Arvore_Esq_01", (-3.8, 1.45, 0.0), 1.10, mats, col_vila, pine=False)
    _build_stylized_tree("Arvore_Esq_02", (-2.1, 2.85, 0.0), 0.95, mats, col_vila, pine=True)
    _build_stylized_tree("Arvore_Fundo_03", (-0.3, 4.10, 0.0), 1.05, mats, col_vila, pine=False)
    _build_stylized_tree("Arvore_Dir_04", (3.35, 1.95, 0.0), 1.12, mats, col_vila, pine=True)
    _build_stylized_tree("Arvore_Dir_05", (3.65, -0.35, 0.0), 0.88, mats, col_vila, pine=False)

    bushes = [
        ((-3.1, 0.45, 0.14), 0.24, "foliage_light"),
        ((-1.2, 1.25, 0.12), 0.20, "foliage_dark"),
        ((2.85, 0.85, 0.15), 0.25, "foliage_light"),
        ((2.65, -0.85, 0.12), 0.19, "foliage_dark"),
    ]
    for idx, (bpos, brad, bmat) in enumerate(bushes):
        create_icosphere(
            f"Arbusto_{idx+1:02d}",
            radius=brad,
            subdivisions=2,
            location=bpos,
            mat=mats[bmat],
            col=col_vila,
            scale_xyz=(1.2, 1.0, 0.75),
        )

    # 4. Distant Low-Poly Houses & Clouds
    _build_distant_house(
        "Casa_Vila_01", (-3.1, 5.8, 0.0), math.radians(18), mats["house_wall_1"], mats["house_roof_1"], mats, col_vila, scale=0.95
    )
    _build_distant_house(
        "Casa_Vila_02", (0.2, 6.8, 0.0), math.radians(-8), mats["house_wall_2"], mats["house_roof_2"], mats, col_vila, scale=1.05
    )
    _build_distant_house(
        "Casa_Vila_03", (3.6, 5.5, 0.0), math.radians(-24), mats["house_wall_1"], mats["house_roof_1"], mats, col_vila, scale=0.90
    )

    clouds = [
        ((-2.2, 8.5, 5.2), 0.55),
        ((1.8, 9.2, 5.8), 0.65),
    ]
    for idx, (cpos, crad) in enumerate(clouds):
        c_root = create_empty(f"Nuvem_{idx+1:02d}_Root", cpos, col_vila, empty_size=0.1)
        for j, (ox, oz, rscale) in enumerate(((-0.4, 0.0, 0.75), (0.0, 0.12, 1.0), (0.42, -0.02, 0.8))):
            create_icosphere(
                f"Nuvem_{idx+1:02d}_Puff_{j}",
                radius=crad * rscale,
                subdivisions=2,
                location=(ox, 0.0, oz),
                mat=mats["cloud_white"],
                col=col_vila,
                parent=c_root,
                scale_xyz=(1.3, 0.8, 0.75),
            )

    # 5. Market Stall ("Barraca do Sapateiro") in Col_Feira_Barraca
    stall_root = create_empty("Barraca_Feira_Root", (0.0, 0.0, 0.0), col_feira, empty_size=0.2)

    # Wooden Deck under the stall (Top at Z = 0.08, starts at X = 0.32 so Nico at X = 0.02 stands 100% on the stone path)
    create_beveled_box(
        "Deck_Madeira_Feira",
        size_xyz=(2.40, 2.50, 0.08),
        location=(1.52, 0.35, 0.04),
        mat=mats["wood_warm"],
        col=col_feira,
        parent=stall_root,
        bevel_width=0.02,
    )

    # Main Counter ("Balcão do Sapateiro"):
    # Spans X from 0.25 to 2.05 (center 1.15, width 1.80), Y from -0.44 to +0.16 (center -0.14, depth 0.60)
    # Top surface of counter is strictly at Z = 0.96!
    create_beveled_box(
        "Balcao_Corpo",
        size_xyz=(1.74, 0.54, 0.82),
        location=(1.15, -0.14, 0.08 + 0.41),
        mat=mats["stall_wall"],
        col=col_feira,
        parent=stall_root,
        bevel_width=0.02,
    )
    # Front decorative wood trim planks on the counter
    for p_idx, px in enumerate((0.40, 0.90, 1.40, 1.90)):
        create_beveled_box(
            f"Balcao_Ripa_{p_idx}",
            size_xyz=(0.08, 0.56, 0.82),
            location=(px, -0.14, 0.49),
            mat=mats["wood_warm"],
            col=col_feira,
            parent=stall_root,
            bevel_width=0.01,
        )
    # Counter Tabletop (Z from 0.88 to 0.96 -> top is exactly Z = 0.96)
    create_beveled_box(
        "Balcao_Tampo_Superior",
        size_xyz=(1.88, 0.66, 0.08),
        location=(1.15, -0.14, 0.92),
        mat=mats["wood_light"],
        col=col_feira,
        parent=stall_root,
        bevel_width=0.018,
    )

    # 4 Wooden Support Posts holding the awning
    post_coords = [
        (0.30, -0.38),
        (2.00, -0.38),
        (0.30, 1.05),
        (2.00, 1.05),
    ]
    for idx, (px, py) in enumerate(post_coords):
        create_beveled_box(
            f"Esteio_Barraca_{idx+1}",
            size_xyz=(0.11, 0.11, 2.82),
            location=(px, py, 0.08 + 1.41),
            mat=mats["wood_dark"],
            col=col_feira,
            parent=stall_root,
            bevel_width=0.015,
        )

    # Low Back Wall & Shoe Shelves behind the seller (keeps sky visible while framing the shop)
    create_beveled_box(
        "Parede_Fundo_Barraca",
        size_xyz=(1.82, 0.12, 1.65),
        location=(1.15, 1.08, 0.08 + 0.825),
        mat=mats["stall_wall"],
        col=col_feira,
        parent=stall_root,
        bevel_width=0.02,
    )
    for s_idx, sz in enumerate((0.95, 1.42)):
        create_beveled_box(
            f"Prateleira_Fundo_{s_idx+1}",
            size_xyz=(1.60, 0.28, 0.05),
            location=(1.15, 0.94, sz),
            mat=mats["wood_warm"],
            col=col_feira,
            parent=stall_root,
            bevel_width=0.01,
        )
        # Shoeboxes on the shelves
        for b_idx, (bx, bmat) in enumerate(((0.68, "awning_teal"), (1.15, "awning_red"), (1.60, "new_shoe_gold"))):
            create_beveled_box(
                f"Caixa_Sapato_{s_idx}_{b_idx}",
                size_xyz=(0.32, 0.22, 0.16),
                location=(bx, 0.93, sz + 0.105),
                mat=mats[bmat],
                col=col_feira,
                parent=stall_root,
                bevel_width=0.01,
            )

    # Striped Colorful Awning (Sloped slightly forward toward -Y, high enough to never clip the refusal signs)
    awning_root = create_empty(
        "Toldo_Barraca_Root",
        location=(1.15, 0.32, 2.92),
        col=col_feira,
        parent=stall_root,
        rot=(math.radians(9), 0.0, 0.0),
        empty_size=0.1,
    )
    num_stripes = 7
    stripe_w = 2.10 / num_stripes
    for i in range(num_stripes):
        sx = -1.05 + (i + 0.5) * stripe_w
        smat = mats["awning_red"] if i % 2 == 0 else mats["awning_cream"]
        create_beveled_box(
            f"Toldo_Faixa_{i+1}",
            size_xyz=(stripe_w * 1.01, 1.85, 0.09),
            location=(sx, 0.0, 0.0),
            mat=smat,
            col=col_feira,
            parent=awning_root,
            bevel_width=0.015,
        )
        # Front scalloped valance flap
        create_beveled_box(
            f"Toldo_Babadinho_{i+1}",
            size_xyz=(stripe_w * 0.96, 0.07, 0.18),
            location=(sx, -0.92, -0.10),
            mat=smat,
            col=col_feira,
            parent=awning_root,
            bevel_width=0.012,
        )

    # Market Crates organized beside the counter
    _build_crate_with_items("Caixa_Feira_01", (2.28, -0.18, 0.08), math.radians(15), mats["nico_shirt"], mats, col_feira)
    _build_crate_with_items("Caixa_Feira_02", (2.35, 0.28, 0.08), math.radians(-10), mats["potato_gold"], mats, col_feira)

    # Gleaming Pair of New Shoes on the right side of the Counter (Z = 0.96)
    shoes_display = _build_pair_of_new_shoes(
        "Par_Sapatos_Novos",
        pos=config.POSITIONS["shoes_on_counter"],
        rot_z=math.radians(-18),
        mats=mats,
        col=col_feira,
    )
    shoes_display.parent = stall_root

    return {
        "stall_root": stall_root,
        "shoes_display": shoes_display,
    }

