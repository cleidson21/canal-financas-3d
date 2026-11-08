"""Nico V3: Organic subdivided character with Armature skinning and reconstructed damaged sneaker."""

import math
import bpy
import bmesh
from mathutils import Vector
from . import config
from .primitives import (
    bind_mesh_to_armature,
    create_beveled_box,
    create_cylinder,
    create_empty,
    create_segmented_organic_tube,
    create_tapered_box,
    create_uv_sphere,
    finalize_mesh_object,
    smoothstep,
)
from .scene_setup import link_to_collection


def _create_sculpted_head_mesh(name, location, mat, col, parent):
    """Create an appealing, slightly caricatured organic head mesh with soft cheeks and rounded jaw."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=18, radius=0.24)
    for v in bm.verts:
        x, y, z = v.co.x, v.co.y, v.co.z
        # Slightly wider width, slightly flattened front-to-back
        x *= 1.06
        y *= 0.94
        z *= 0.98
        # Cheek fullness in lower-front face
        if -0.14 < z < 0.04 and y < -0.02:
            cheek_factor = math.exp(-((z + 0.05) / 0.08) ** 2)
            x *= 1.0 + 0.08 * cheek_factor
            y *= 1.0 + 0.04 * cheek_factor
        # Slightly flatter face front plane (-Y) for clean eye/mouth placement
        if y < -0.185 and -0.12 < z < 0.12:
            y = -0.185 + (y + 0.185) * 0.45
        v.co = Vector((x, y, z))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finalize_mesh_object(
        name,
        bm,
        location,
        (0.0, 0.0, 0.0),
        mat,
        col,
        parent=parent,
        subsurf_levels=1,
        shade_smooth=True,
    )


def _create_curved_cap_visor(name, location, mat, col, parent):
    """Create a realistic curved baseball cap visor arched along X and projecting toward -Y."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    # Subdivide along X so we can arch the visor smoothly
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=3, use_grid_fill=True)
    for v in bm.verts:
        # Scale to visor dimensions: width 0.44, depth 0.25, thickness 0.032
        x = v.co.x * 0.44
        y = (v.co.y - 0.5) * 0.25  # 0 at back, -0.25 at tip
        z = v.co.z * 0.032
        # Arch curve across X (middle is higher, edges curve down)
        arch = -0.22 * (x * x)
        # Slight downward slope toward front tip
        slope = 0.08 * y
        v.co = Vector((x, y, z + arch + slope))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finalize_mesh_object(
        name,
        bm,
        location,
        (math.radians(-6), 0.0, 0.0),
        mat,
        col,
        parent=parent,
        subsurf_levels=1,
        shade_smooth=True,
    )


def _create_sneaker_sole_mesh(name, length_y, width_x, height_z, y_center, location, mat, col, parent):
    """Create a thin, rounded-contour sneaker rubber sole."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
    for v in bm.verts:
        nx = v.co.x  # -0.5 to +0.5
        ny = v.co.y  # -0.5 to +0.5
        nz = v.co.z  # -0.5 to +0.5
        # Round the front (-Y) and rear (+Y) corners for an authentic sneaker footprint
        round_factor = 1.0 - 0.22 * (ny * 2.0) ** 4
        x = nx * width_x * round_factor
        y = y_center + ny * length_y
        z = nz * height_z
        v.co = Vector((x, y, z))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finalize_mesh_object(
        name,
        bm,
        location,
        (0.0, 0.0, 0.0),
        mat,
        col,
        parent=parent,
        bevel_width=0.004,
        bevel_segments=2,
        subsurf_levels=1,
        shade_smooth=True,
    )


def _create_sneaker_upper_mesh(name, location, mat_body, mat_toecap, col, parent):
    """Create a recognizable stylized sneaker upper with integrated white toe-cap material (zero z-fighting)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=3, use_grid_fill=True)
    for v in bm.verts:
        nx = v.co.x  # -0.5 to 0.5
        ny = v.co.y  # -0.5 (front toe) to +0.5 (back heel)
        nz = v.co.z  # -0.5 (bottom) to +0.5 (top collar)

        toe_round = 1.0 - 0.26 * max(0.0, -ny * 2.0) ** 2.4
        top_taper = 1.0 - 0.15 * max(0.0, nz + 0.5)
        x = nx * 0.168 * toe_round * top_taper
        y = -0.055 + ny * 0.33

        if nz > -0.2:
            if ny < -0.02:
                t_toe = min(1.0, (-0.02 - ny) / 0.48)
                max_h = 0.096 * (1.0 - 0.45 * smoothstep(0.0, 1.0, t_toe))
            else:
                max_h = 0.096
            z = -0.082 + (nz + 0.5) * max_h
        else:
            z = -0.082 + (nz + 0.5) * 0.096

        v.co = Vector((x, y, z))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # Assign material index 1 (white toe cap) to front toe faces (y < -0.145)
    for f in bm.faces:
        center = f.calc_center_median()
        if center.y < -0.145 and center.z > -0.080:
            f.material_index = 1
        else:
            f.material_index = 0

    obj = finalize_mesh_object(
        name,
        bm,
        location,
        (0.0, 0.0, 0.0),
        mat_body,
        col,
        parent=parent,
        subsurf_levels=1,
        shade_smooth=True,
    )
    obj.data.materials.append(mat_toecap)
    return obj


def _build_sneaker(side_s, foot_pivot, mats, col, damaged=False):
    """Build either the intact left sneaker or the worn right sneaker with an articulated detached front sole."""
    damaged_sole_pivot = None

    # 1. Upper Sneaker Body with integrated white toe cap (100% smooth, zero intersection artifacts)
    _create_sneaker_upper_mesh(
        f"Nico_Tenis_Corpo_{side_s}",
        location=(0.0, 0.0, 0.0),
        mat_body=mats["nico_shoe_body"],
        mat_toecap=mats["nico_shoe_sole"],
        col=col,
        parent=foot_pivot,
    )

    # Shoelaces (3 crisp white bars across the instep)
    for idx, (ly, lz) in enumerate(((-0.048, 0.016), (-0.082, 0.004), (-0.115, -0.008))):
        create_beveled_box(
            f"Nico_Tenis_Cadarco_{side_s}_{idx+1}",
            size_xyz=(0.095, 0.020, 0.014),
            location=(0.0, ly, lz),
            mat=mats["nico_shoe_sole"],
            col=col,
            parent=foot_pivot,
            rot=(math.radians(22), 0.0, 0.0),
            bevel_width=0.004,
            shade_smooth=True,
        )

    if not damaged:
        # INTACT LEFT SNEAKER: Single thin continuous rubber sole (bottom at Z = -0.12)
        _create_sneaker_sole_mesh(
            name=f"Nico_Tenis_Sola_{side_s}",
            length_y=0.345,
            width_x=0.174,
            height_z=0.026,
            y_center=-0.055,
            location=(0.0, 0.0, -0.097),
            mat=mats["nico_shoe_sole"],
            col=col,
            parent=foot_pivot,
        )
    else:
        # DAMAGED RIGHT SNEAKER ("Sapato com a sola frontal descolada / boca de jacaré")
        # A. Intact Rear Heel Sole (from heel Y=+0.12 to mid-arch Y=-0.03)
        _create_sneaker_sole_mesh(
            name="Nico_Tenis_SolaTraseira_R",
            length_y=0.155,
            width_x=0.172,
            height_z=0.026,
            y_center=0.042,
            location=(0.0, 0.0, -0.097),
            mat=mats["nico_shoe_sole"],
            col=col,
            parent=foot_pivot,
        )

        # B. Dark Interior Under-Sole Cavity tucked cleanly under the upper shoe
        _create_sneaker_sole_mesh(
            name="Nico_Tenis_InteriorEscuro_R",
            length_y=0.165,
            width_x=0.142,
            height_z=0.008,
            y_center=-0.105,
            location=(0.0, 0.0, -0.083),
            mat=mats["nico_shoe_inside"],
            col=col,
            parent=foot_pivot,
        )

        # C. Discreet internal red sock glimpse visible inside the gap when the sole opens
        _create_sneaker_sole_mesh(
            name="Nico_Tenis_MeiaInterna_R",
            length_y=0.115,
            width_x=0.118,
            height_z=0.010,
            y_center=-0.130,
            location=(0.0, 0.0, -0.085),
            mat=mats["nico_sock_red"],
            col=col,
            parent=foot_pivot,
        )

        # D. Articulated Detached Front Sole Pivot (hinged under the mid-arch at Y = -0.03, Z = -0.097)
        damaged_sole_pivot = create_empty(
            "Nico_Sola_Descolada_Pivot_R",
            location=(0.0, -0.03, -0.097),
            col=col,
            parent=foot_pivot,
            empty_size=0.06,
        )
        # Thin, recognizable front rubber sole extending from hinge (0.0) to toe tip (-0.195)
        _create_sneaker_sole_mesh(
            name="Nico_Tenis_SolaFrontal_R",
            length_y=0.195,
            width_x=0.174,
            height_z=0.024,
            y_center=-0.097,
            location=(0.0, 0.0, 0.0),
            mat=mats["nico_shoe_sole"],
            col=col,
            parent=damaged_sole_pivot,
        )
        # Thin dark rubber upper liner on the flapping sole so the open gap has crisp visual contrast
        _create_sneaker_sole_mesh(
            name="Nico_Tenis_SolaFrontal_CamadaInterna_R",
            length_y=0.175,
            width_x=0.150,
            height_z=0.005,
            y_center=-0.095,
            location=(0.0, 0.0, 0.011),
            mat=mats["nico_shoe_inside"],
            col=col,
            parent=damaged_sole_pivot,
        )

    return damaged_sole_pivot


def _setup_nico_armature_and_skinning(root, pivots, mats, col):
    """Build Nico_Armature_V3 and skin continuous organic limb meshes with smooth Vertex Groups."""
    arm_data = bpy.data.armatures.new("Nico_Armature_V3_Data")
    arm_obj = bpy.data.objects.new("Nico_Armature_V3", arm_data)
    link_to_collection(arm_obj, col)
    arm_obj.parent = root
    arm_obj.location = (0.0, 0.0, 0.0)

    # Create bones in Edit Mode matching the exact rest positions of the hierarchy pivots
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones

    bone_specs = {
        "pelvis": ((0.0, 0.0, 0.78), None),
        "torso": ((0.0, 0.0, 0.85), "pelvis"),
        "head": ((0.0, 0.0, 1.40), "torso"),
        "arm_l": ((-0.28, 0.0, 1.30), "torso"),
        "forearm_l": ((-0.30, 0.0, 1.04), "arm_l"),
        "arm_r": ((0.28, 0.0, 1.30), "torso"),
        "forearm_r": ((0.30, 0.0, 1.04), "arm_r"),
        "leg_l": ((-0.14, 0.0, 0.78), "pelvis"),
        "knee_l": ((-0.14, 0.0, 0.42), "leg_l"),
        "leg_r": ((0.14, 0.0, 0.78), "pelvis"),
        "knee_r": ((0.14, 0.0, 0.42), "leg_r"),
    }

    created_bones = {}
    for bname, (h_co, parent_name) in bone_specs.items():
        b = eb.new(bname)
        b.head = Vector(h_co)
        # Align bone rest axes (+X, +Y, +Z) with Empty control axes by pointing tail along +Y with roll=0
        b.tail = Vector((h_co[0], h_co[1] + 0.12, h_co[2]))
        b.roll = 0.0
        if parent_name and parent_name in created_bones:
            b.parent = created_bones[parent_name]
        created_bones[bname] = b

    bpy.ops.object.mode_set(mode="OBJECT")

    # Bind each PoseBone to follow its corresponding control pivot via COPY_TRANSFORMS
    for bname in bone_specs:
        pb = arm_obj.pose.bones.get(bname)
        target_obj = pivots.get(bname)
        if pb and target_obj:
            con = pb.constraints.new(type="COPY_TRANSFORMS")
            con.target = target_obj
            con.target_space = "WORLD"
            con.owner_space = "WORLD"

    # Build continuous organic skinned Arms (Upper arm + Elbow + Forearm in ONE seamless mesh per side)
    for side_s, x_sign, b_upper, b_lower in (
        ("L", -1.0, "arm_l", "forearm_l"),
        ("R", 1.0, "arm_r", "forearm_r"),
    ):
        x_base = x_sign * 0.30
        # Rings from Z = 1.24 (inside sleeve) through Elbow (Z = 1.04) down to Wrist (Z = 0.80)
        arm_rings = [
            (1.24, 0.062, 0.062, x_base, 0.0),
            (1.18, 0.058, 0.058, x_base, 0.0),
            (1.12, 0.055, 0.055, x_base, 0.0),
            (1.08, 0.053, 0.053, x_base, 0.0),
            (1.055, 0.052, 0.052, x_base, 0.0),
            (1.04, 0.052, 0.053, x_base, 0.0),  # Elbow center
            (1.025, 0.052, 0.052, x_base, 0.0),
            (0.99, 0.053, 0.053, x_base, 0.0),
            (0.94, 0.051, 0.051, x_base, 0.0),
            (0.88, 0.047, 0.047, x_base, 0.0),
            (0.83, 0.043, 0.043, x_base, 0.0),
            (0.79, 0.040, 0.040, x_base, 0.0),
        ]
        arm_mesh_obj = create_segmented_organic_tube(
            f"Nico_Braco_Continuo_{side_s}",
            profile_rings=arm_rings,
            segments=16,
            location=(0.0, 0.0, 0.0),
            mat=mats["nico_skin"],
            col=col,
            subsurf_levels=2,
            shade_smooth=True,
        )
        vg_up = arm_mesh_obj.vertex_groups.new(name=b_upper)
        vg_lo = arm_mesh_obj.vertex_groups.new(name=b_lower)
        for v in arm_mesh_obj.data.vertices:
            # Smooth transition across elbow Z = 1.04 (from 0.98 to 1.10)
            w_up = smoothstep(0.98, 1.10, v.co.z)
            w_lo = 1.0 - w_up
            if w_up > 0.001:
                vg_up.add([v.index], w_up, "REPLACE")
            if w_lo > 0.001:
                vg_lo.add([v.index], w_lo, "REPLACE")
        bind_mesh_to_armature(arm_mesh_obj, arm_obj, preserve_volume=True)

    # Build continuous organic skinned Legs (Thigh + Knee + Calf in ONE seamless mesh per side)
    for side_s, x_sign, b_thigh, b_shin in (
        ("L", -1.0, "leg_l", "knee_l"),
        ("R", 1.0, "leg_r", "knee_r"),
    ):
        x_base = x_sign * 0.14
        # Rings from Z = 0.58 (inside shorts) through Knee (Z = 0.42) down to Sock/Ankle (Z = 0.16)
        leg_rings = [
            (0.58, 0.072, 0.075, x_base, 0.0),
            (0.52, 0.068, 0.070, x_base, 0.0),
            (0.47, 0.064, 0.066, x_base, 0.0),
            (0.44, 0.062, 0.065, x_base, 0.0),
            (0.42, 0.061, 0.065, x_base, 0.0),  # Knee center
            (0.40, 0.060, 0.063, x_base, 0.0),
            (0.36, 0.062, 0.064, x_base, 0.0),  # Upper calf fullness
            (0.30, 0.056, 0.058, x_base, 0.0),
            (0.24, 0.050, 0.052, x_base, 0.0),
            (0.18, 0.046, 0.048, x_base, 0.0),
        ]
        leg_mesh_obj = create_segmented_organic_tube(
            f"Nico_Perna_Continua_{side_s}",
            profile_rings=leg_rings,
            segments=16,
            location=(0.0, 0.0, 0.0),
            mat=mats["nico_skin"],
            col=col,
            subsurf_levels=2,
            shade_smooth=True,
        )
        vg_th = leg_mesh_obj.vertex_groups.new(name=b_thigh)
        vg_sh = leg_mesh_obj.vertex_groups.new(name=b_shin)
        for v in leg_mesh_obj.data.vertices:
            # Smooth transition across knee Z = 0.42 (from 0.36 to 0.48)
            w_th = smoothstep(0.36, 0.48, v.co.z)
            w_sh = 1.0 - w_th
            if w_th > 0.001:
                vg_th.add([v.index], w_th, "REPLACE")
            if w_sh > 0.001:
                vg_sh.add([v.index], w_sh, "REPLACE")
        bind_mesh_to_armature(leg_mesh_obj, arm_obj, preserve_volume=True)

    return arm_obj


def build_character_nico(col, mats):
    """Build Nico V3 with organic proportions, continuous Armature-skinned limbs, and fixed damaged sneaker.

    Local coordinate convention for Nico:
    - Forward (face direction): -Y
    - Back: +Y
    - Left side of screen / right body side: -X
    - Right side of screen / forward-featured side: +X
    - Up: +Z (Soles touch Z = 0.0 when pelvis is at Z = 0.78)
    """
    start_pos = config.POSITIONS["nico_start"]
    root = create_empty("Nico_Root", start_pos, col, rot=(0.0, 0.0, math.radians(32)), empty_size=0.25)

    # 1. Pelvis pivot at Z = 0.78
    pelvis = create_empty("Nico_Pelvis", (0.0, 0.0, 0.78), col, parent=root, empty_size=0.15)
    # Organic rounded pelvis/shorts waist (smoothly blends into the two shorts legs without blocky corners)
    pelvis_rings = [
        (0.11, 0.215, 0.142, 0.0, 0.0),
        (0.06, 0.228, 0.152, 0.0, 0.0),
        (0.00, 0.225, 0.150, 0.0, 0.0),
        (-0.06, 0.205, 0.138, 0.0, 0.0),
        (-0.10, 0.175, 0.120, 0.0, 0.0),
    ]
    create_segmented_organic_tube(
        "Nico_Bermuda_Quadril",
        profile_rings=pelvis_rings,
        segments=20,
        location=(0.0, 0.0, 0.0),
        mat=mats["nico_shorts_blue"],
        col=col,
        parent=pelvis,
        subsurf_levels=2,
        shade_smooth=True,
    )

    # 2. Torso pivot at Z = +0.07 relative to Pelvis (World Z = 0.85)
    torso = create_empty("Nico_Torso", (0.0, 0.0, 0.07), col, parent=pelvis, empty_size=0.15)
    # Organic subdivided t-shirt torso (soft rounded chest, natural waist, smooth rounded shoulder top)
    torso_rings = [
        (0.53, 0.145, 0.105, 0.0, 0.0),  # Neck base
        (0.49, 0.245, 0.148, 0.0, 0.0),  # Rounded shoulders
        (0.38, 0.252, 0.158, 0.0, -0.005),  # Chest fullness
        (0.24, 0.238, 0.152, 0.0, -0.005),  # Mid-torso
        (0.10, 0.228, 0.148, 0.0, 0.0),  # Lower waist
        (-0.02, 0.224, 0.146, 0.0, 0.0),  # Shirt hem overlapping shorts smoothly
    ]
    create_segmented_organic_tube(
        "Nico_Camisa_Torso",
        profile_rings=torso_rings,
        segments=20,
        location=(0.0, 0.0, 0.0),
        mat=mats["nico_shirt"],
        col=col,
        parent=torso,
        subsurf_levels=2,
        shade_smooth=True,
    )
    # Soft rounded crew-neck collar ring
    collar_rings = [
        (0.545, 0.118, 0.102, 0.0, -0.004),
        (0.515, 0.148, 0.118, 0.0, -0.004),
    ]
    create_segmented_organic_tube(
        "Nico_Camisa_Gola",
        profile_rings=collar_rings,
        segments=18,
        location=(0.0, 0.0, 0.0),
        mat=mats["awning_cream"],
        col=col,
        parent=torso,
        cap_top=False,
        cap_bottom=False,
        subsurf_levels=2,
        shade_smooth=True,
    )

    # 3. Head pivot at Z = +0.55 relative to Torso (World Z = 1.40)
    head = create_empty("Nico_Head", (0.0, 0.0, 0.55), col, parent=torso, empty_size=0.15)
    # Smooth multi-ring cylindrical neck extending deep inside the shirt collar (zero bottom seam)
    neck_rings = [
        (0.12, 0.082, 0.080, 0.0, 0.0),
        (0.05, 0.085, 0.083, 0.0, 0.0),
        (-0.01, 0.090, 0.088, 0.0, 0.0),
        (-0.06, 0.098, 0.095, 0.0, 0.0),
    ]
    create_segmented_organic_tube(
        "Nico_Pescoco",
        profile_rings=neck_rings,
        segments=16,
        location=(0.0, 0.0, 0.0),
        mat=mats["nico_skin"],
        col=col,
        parent=head,
        subsurf_levels=2,
        shade_smooth=True,
    )
    # Sculpted Organic Head Mesh (center at Z = 0.27)
    _create_sculpted_head_mesh(
        "Nico_Cabeca_Mesh",
        location=(0.0, 0.0, 0.27),
        mat=mats["nico_skin"],
        col=col,
        parent=head,
    )

    # Stylized Warm Brown Hair visible under the cap (nape, temples, and sideburns)
    create_uv_sphere(
        "Nico_Cabelo_Base",
        radius=0.242,
        segments=20,
        rings=14,
        location=(0.0, 0.035, 0.305),
        mat=mats["nico_hair"],
        col=col,
        parent=head,
        scale_xyz=(1.05, 0.94, 0.82),
        shade_smooth=True,
    )
    for side_s, x_sign in (("L", -1.0), ("R", 1.0)):
        # Temple hair tuft / sideburn in front of ear
        create_beveled_box(
            f"Nico_Cabelo_Costeleta_{side_s}",
            size_xyz=(0.045, 0.075, 0.11),
            location=(x_sign * 0.238, -0.055, 0.31),
            mat=mats["nico_hair"],
            col=col,
            parent=head,
            rot=(math.radians(8), 0.0, x_sign * math.radians(-6)),
            bevel_width=0.018,
            subsurf_levels=1,
            shade_smooth=True,
        )
        # Organic rounded ear
        create_uv_sphere(
            f"Nico_Orelha_{side_s}",
            radius=0.055,
            segments=14,
            rings=10,
            location=(x_sign * 0.252, 0.01, 0.255),
            mat=mats["nico_skin"],
            col=col,
            parent=head,
            rot=(0.0, x_sign * math.radians(12), x_sign * math.radians(-10)),
            scale_xyz=(0.52, 0.78, 1.12),
            shade_smooth=True,
        )

    # Soft rounded button nose
    create_uv_sphere(
        "Nico_Nariz",
        radius=0.036,
        segments=14,
        rings=10,
        location=(0.0, -0.222, 0.235),
        mat=mats["nico_skin"],
        col=col,
        parent=head,
        scale_xyz=(1.05, 0.85, 0.82),
        shade_smooth=True,
    )

    # Expressive Layered Eyes (Sclera + Iris/Pupil + Dual Catchlights)
    for side_s, x_eye in (("L", -0.102), ("R", 0.102)):
        create_uv_sphere(
            f"Nico_Olho_Branco_{side_s}",
            radius=0.045,
            segments=16,
            rings=12,
            location=(x_eye, -0.202, 0.268),
            mat=mats["eye_white"],
            col=col,
            parent=head,
            scale_xyz=(1.0, 0.38, 1.12),
            shade_smooth=True,
        )
        create_uv_sphere(
            f"Nico_Pupila_{side_s}",
            radius=0.030,
            segments=14,
            rings=10,
            location=(x_eye, -0.219, 0.268),
            mat=mats["eye_dark"],
            col=col,
            parent=head,
            scale_xyz=(1.0, 0.36, 1.12),
            shade_smooth=True,
        )
        # Main specular highlight
        create_uv_sphere(
            f"Nico_Brilho_Olho_{side_s}",
            radius=0.011,
            segments=10,
            rings=8,
            location=(x_eye - 0.012, -0.231, 0.284),
            mat=mats["eye_white"],
            col=col,
            parent=head,
            shade_smooth=True,
        )
        # Secondary smaller lower-right catchlight
        create_uv_sphere(
            f"Nico_Brilho_Sec_{side_s}",
            radius=0.0055,
            segments=8,
            rings=6,
            location=(x_eye + 0.010, -0.230, 0.254),
            mat=mats["eye_white"],
            col=col,
            parent=head,
            shade_smooth=True,
        )

    # Articulated Curved Eyebrows (Clearly visible below the cap visor!)
    eyebrow_l = create_beveled_box(
        "Nico_Sobrancelha_L",
        size_xyz=(0.098, 0.038, 0.026),
        location=(-0.102, -0.228, 0.342),
        mat=mats["eyebrow_dark"],
        col=col,
        parent=head,
        rot=(math.radians(-10), 0.0, 0.0),
        bevel_width=0.010,
        subsurf_levels=1,
        shade_smooth=True,
    )
    eyebrow_r = create_beveled_box(
        "Nico_Sobrancelha_R",
        size_xyz=(0.098, 0.038, 0.026),
        location=(0.102, -0.228, 0.342),
        mat=mats["eyebrow_dark"],
        col=col,
        parent=head,
        rot=(math.radians(-10), 0.0, 0.0),
        bevel_width=0.010,
        subsurf_levels=1,
        shade_smooth=True,
    )

    # Articulated 3D Mouth with inner pink tongue accent
    mouth = create_beveled_box(
        "Nico_Boca",
        size_xyz=(0.102, 0.032, 0.032),
        location=(0.0, -0.214, 0.162),
        mat=mats["mouth_dark"],
        col=col,
        parent=head,
        bevel_width=0.012,
        subsurf_levels=1,
        shade_smooth=True,
    )
    create_uv_sphere(
        "Nico_Lingua",
        radius=0.026,
        segments=10,
        rings=8,
        location=(0.0, -0.006, -0.007),
        mat=mats["tongue_pink"],
        col=col,
        parent=mouth,
        scale_xyz=(1.2, 0.4, 0.45),
        shade_smooth=True,
    )

    # Stylized Blue Baseball Cap (Positioned high enough on forehead so eyebrows are 100% visible)
    create_uv_sphere(
        "Nico_Bone_Copa",
        radius=0.258,
        segments=24,
        rings=16,
        location=(0.0, 0.016, 0.425),
        mat=mats["nico_cap_blue"],
        col=col,
        parent=head,
        rot=(math.radians(-8), 0.0, 0.0),
        scale_xyz=(1.06, 1.02, 0.55),
        subsurf_levels=1,
        shade_smooth=True,
    )
    create_beveled_box(
        "Nico_Bone_Emblema",
        size_xyz=(0.12, 0.025, 0.065),
        location=(0.0, -0.238, 0.472),
        mat=mats["awning_cream"],
        col=col,
        parent=head,
        rot=(math.radians(-10), 0.0, 0.0),
        bevel_width=0.008,
        subsurf_levels=1,
        shade_smooth=True,
    )
    _create_curved_cap_visor(
        "Nico_Bone_Aba",
        location=(0.0, -0.175, 0.438),
        mat=mats["nico_cap_blue"],
        col=col,
        parent=head,
    )
    create_uv_sphere(
        "Nico_Bone_Botao",
        radius=0.030,
        segments=12,
        rings=8,
        location=(0.0, 0.025, 0.568),
        mat=mats["awning_cream"],
        col=col,
        parent=head,
        scale_xyz=(1.0, 1.0, 0.45),
        shade_smooth=True,
    )

    # 4. Arm Control Pivots, Rounded Short Sleeves & Sculpted Hands
    arms = {}
    for side_s, x_sign in (("L", -1.0), ("R", 1.0)):
        sh_pivot = create_empty(
            f"Nico_Arm_{side_s}",
            location=(x_sign * 0.28, 0.0, 0.45),
            col=col,
            parent=torso,
            empty_size=0.1,
        )
        # Organic rounded shoulder cap + sleeve (like reference videos!)
        sleeve_rings = [
            (0.03, 0.075, 0.075, x_sign * 0.01, 0.0),
            (-0.02, 0.088, 0.088, x_sign * 0.02, 0.0),
            (-0.09, 0.084, 0.084, x_sign * 0.02, 0.0),
            (-0.15, 0.076, 0.076, x_sign * 0.02, 0.0),
        ]
        create_segmented_organic_tube(
            f"Nico_Manga_{side_s}",
            profile_rings=sleeve_rings,
            segments=16,
            location=(0.0, 0.0, 0.0),
            mat=mats["nico_shirt"],
            col=col,
            parent=sh_pivot,
            subsurf_levels=2,
            shade_smooth=True,
        )

        # Elbow / Forearm Pivot at Z = -0.26
        el_pivot = create_empty(
            f"Nico_Forearm_{side_s}",
            location=(x_sign * 0.02, 0.0, -0.26),
            col=col,
            parent=sh_pivot,
            empty_size=0.08,
        )
        # Organic Rounded Hand + Sculpted Finger Roll + Thumb at Z = -0.25
        create_uv_sphere(
            f"Nico_Mao_Palma_{side_s}",
            radius=0.062,
            segments=16,
            rings=12,
            location=(0.0, -0.008, -0.255),
            mat=mats["nico_skin"],
            col=col,
            parent=el_pivot,
            scale_xyz=(0.88, 1.05, 1.15),
            subsurf_levels=1,
            shade_smooth=True,
        )
        create_uv_sphere(
            f"Nico_Mao_Polegar_{side_s}",
            radius=0.028,
            segments=12,
            rings=8,
            location=(-x_sign * 0.042, -0.052, -0.235),
            mat=mats["nico_skin"],
            col=col,
            parent=el_pivot,
            rot=(math.radians(28), 0.0, x_sign * math.radians(18)),
            scale_xyz=(0.85, 1.35, 0.90),
            shade_smooth=True,
        )
        arms[side_s] = (sh_pivot, el_pivot)

    # 5. Leg Control Pivots, Tailored Shorts Cuffs, Socks & Reconstructed Sneakers
    legs = {}
    damaged_sole_pivot = None
    for side_s, x_sign in (("L", -1.0), ("R", 1.0)):
        hip_pivot = create_empty(
            f"Nico_Leg_{side_s}",
            location=(x_sign * 0.14, 0.0, 0.0),
            col=col,
            parent=pelvis,
            empty_size=0.1,
        )
        # Organic cylindrical shorts leg cuff (blends seamlessly into Nico_Bermuda_Quadril)
        shorts_leg_rings = [
            (0.02, 0.102, 0.112, 0.0, 0.0),
            (-0.08, 0.098, 0.106, 0.0, 0.0),
            (-0.18, 0.095, 0.102, 0.0, 0.0),
            (-0.24, 0.092, 0.098, 0.0, 0.0),
        ]
        create_segmented_organic_tube(
            f"Nico_Bermuda_Perna_{side_s}",
            profile_rings=shorts_leg_rings,
            segments=16,
            location=(0.0, 0.0, 0.0),
            mat=mats["nico_shorts_blue"],
            col=col,
            parent=hip_pivot,
            subsurf_levels=2,
            shade_smooth=True,
        )

        # Knee Pivot at Z = -0.36
        knee_pivot = create_empty(
            f"Nico_Knee_{side_s}",
            location=(0.0, 0.0, -0.36),
            col=col,
            parent=hip_pivot,
            empty_size=0.08,
        )
        # Smooth ribbed crew sock above ankle
        sock_rings = [
            (-0.20, 0.056, 0.058, 0.0, 0.0),
            (-0.22, 0.058, 0.060, 0.0, 0.0),
            (-0.26, 0.054, 0.056, 0.0, 0.0),
            (-0.31, 0.053, 0.055, 0.0, 0.0),
        ]
        create_segmented_organic_tube(
            f"Nico_Meia_{side_s}",
            profile_rings=sock_rings,
            segments=16,
            location=(0.0, 0.0, 0.0),
            mat=mats["nico_sock_white"],
            col=col,
            parent=knee_pivot,
            subsurf_levels=1,
            shade_smooth=True,
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
            _build_sneaker("L", foot_pivot, mats, col, damaged=False)
        else:
            damaged_sole_pivot = _build_sneaker("R", foot_pivot, mats, col, damaged=True)

        legs[side_s] = (hip_pivot, knee_pivot, foot_pivot)

    # 6. Build Armature & Skin Continuous Organic Limbs (Arms & Legs)
    pivots_map = {
        "pelvis": pelvis,
        "torso": torso,
        "head": head,
        "arm_l": arms["L"][0],
        "forearm_l": arms["L"][1],
        "arm_r": arms["R"][0],
        "forearm_r": arms["R"][1],
        "leg_l": legs["L"][0],
        "knee_l": legs["L"][1],
        "leg_r": legs["R"][0],
        "knee_r": legs["R"][1],
    }
    armature_obj = _setup_nico_armature_and_skinning(root, pivots_map, mats, col)

    # Mark root and collection as Blender Asset Browser assets if supported
    try:
        root.asset_mark()
        col.asset_mark()
    except Exception:
        pass

    return {
        "root": root,
        "armature": armature_obj,
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
    """Build the refined V3 Cobbler / Shoe Seller standing behind the stall counter."""
    pos = config.POSITIONS["seller_pos"]
    root = create_empty("Vendedor_Root", pos, col, rot=(0.0, 0.0, math.radians(-16)), empty_size=0.18)

    torso = create_empty("Vendedor_Torso", (0.0, 0.0, 0.82), col, parent=root, empty_size=0.12)
    torso_rings = [
        (0.55, 0.14, 0.10, 0.0, 0.0),
        (0.50, 0.24, 0.15, 0.0, 0.0),
        (0.32, 0.25, 0.16, 0.0, 0.0),
        (0.02, 0.23, 0.15, 0.0, 0.0),
    ]
    create_segmented_organic_tube(
        "Vendedor_Camisa",
        profile_rings=torso_rings,
        segments=18,
        location=(0.0, 0.0, 0.0),
        mat=mats["seller_shirt"],
        col=col,
        parent=torso,
        subsurf_levels=2,
        shade_smooth=True,
    )
    create_beveled_box(
        "Vendedor_Avental",
        size_xyz=(0.35, 0.30, 0.45),
        location=(0.0, -0.015, 0.24),
        mat=mats["seller_apron"],
        col=col,
        parent=torso,
        bevel_width=0.025,
        subsurf_levels=1,
        shade_smooth=True,
    )

    head = create_empty("Vendedor_Head", (0.0, 0.0, 0.57), col, parent=torso, empty_size=0.12)
    _create_sculpted_head_mesh(
        "Vendedor_Cabeca",
        location=(0.0, 0.0, 0.24),
        mat=mats["nico_skin"],
        col=col,
        parent=head,
    )
    # Expressive handlebar mustache
    create_beveled_box(
        "Vendedor_Bigode",
        size_xyz=(0.23, 0.075, 0.055),
        location=(0.0, -0.215, 0.165),
        mat=mats["wood_dark"],
        col=col,
        parent=head,
        bevel_width=0.02,
        subsurf_levels=1,
        shade_smooth=True,
    )
    for side_s, x_eye in (("L", -0.095), ("R", 0.095)):
        create_uv_sphere(
            f"Vendedor_Olho_{side_s}",
            radius=0.034,
            segments=12,
            rings=10,
            location=(x_eye, -0.20, 0.255),
            mat=mats["eye_dark"],
            col=col,
            parent=head,
            shade_smooth=True,
        )
        create_beveled_box(
            f"Vendedor_Sobrancelha_{side_s}",
            size_xyz=(0.085, 0.03, 0.025),
            location=(x_eye, -0.21, 0.32),
            mat=mats["wood_dark"],
            col=col,
            parent=head,
            bevel_width=0.008,
            shade_smooth=True,
        )

    # Rounded Cobbler Flat Cap (Boina)
    create_uv_sphere(
        "Vendedor_Boina",
        radius=0.245,
        segments=20,
        rings=12,
        location=(0.0, -0.01, 0.42),
        mat=mats["wood_warm"],
        col=col,
        parent=head,
        scale_xyz=(1.04, 1.04, 0.36),
        subsurf_levels=1,
        shade_smooth=True,
    )

    arm_l = create_empty("Vendedor_Arm_L", (-0.27, 0.0, 0.48), col, parent=torso, empty_size=0.08)
    create_cylinder(
        "Vendedor_Braco_L",
        radius1=0.058,
        radius2=0.068,
        depth=0.38,
        vertices=14,
        location=(-0.02, 0.0, -0.18),
        mat=mats["seller_shirt"],
        col=col,
        parent=arm_l,
        subsurf_levels=1,
        shade_smooth=True,
    )
    arm_r = create_empty("Vendedor_Arm_R", (0.27, 0.0, 0.48), col, parent=torso, empty_size=0.08)
    create_cylinder(
        "Vendedor_Braco_R",
        radius1=0.058,
        radius2=0.068,
        depth=0.38,
        vertices=14,
        location=(0.02, 0.0, -0.18),
        mat=mats["seller_shirt"],
        col=col,
        parent=arm_r,
        subsurf_levels=1,
        shade_smooth=True,
    )

    return {
        "root": root,
        "torso": torso,
        "head": head,
        "arm_l": arm_l,
        "arm_r": arm_r,
    }
