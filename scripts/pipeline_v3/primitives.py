"""Procedural geometry & organic subdivision primitives built with bmesh and modifiers (Blender 5.2 LTS)."""

import math
import bpy
import bmesh
from mathutils import Matrix, Vector
from .scene_setup import link_to_collection


def create_empty(name, location, col, parent=None, rot=(0.0, 0.0, 0.0), empty_size=0.15):
    """Create an Empty object for rigging/hierarchy pivots."""
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = empty_size
    obj.location = location
    obj.rotation_euler = rot
    link_to_collection(obj, col)
    if parent:
        obj.parent = parent
    return obj


def finalize_mesh_object(
    name,
    bm,
    location,
    rot,
    mat,
    col,
    parent=None,
    bevel_width=0.0,
    bevel_segments=2,
    subsurf_levels=0,
    shade_smooth=False,
):
    """Convert bmesh to a Blender Object, assign material, modifiers, collection, and parent."""
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = shade_smooth

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rot
    if mat:
        mesh.materials.append(mat)

    if bevel_width > 0.0:
        bev = obj.modifiers.new(name="Bevel", type="BEVEL")
        bev.width = bevel_width
        bev.segments = bevel_segments
        bev.limit_method = "ANGLE"

    if subsurf_levels > 0:
        sub = obj.modifiers.new(name="Subdivision", type="SUBSURF")
        sub.levels = subsurf_levels
        sub.render_levels = subsurf_levels

    link_to_collection(obj, col)
    if parent:
        obj.parent = parent
    return obj


def create_beveled_box(
    name,
    size_xyz,
    location,
    mat,
    col,
    parent=None,
    rot=(0.0, 0.0, 0.0),
    bevel_width=0.02,
    bevel_segments=2,
    subsurf_levels=0,
    shade_smooth=False,
    offset_xyz=(0.0, 0.0, 0.0),
):
    """Create a box with optional local vertex offset, bevel, and subdivision surface."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = size_xyz
    bmesh.ops.scale(bm, vec=Vector((sx, sy, sz)), verts=bm.verts)
    ox, oy, oz = offset_xyz
    if ox != 0.0 or oy != 0.0 or oz != 0.0:
        bmesh.ops.translate(bm, vec=Vector((ox, oy, oz)), verts=bm.verts)
    return finalize_mesh_object(
        name,
        bm,
        location,
        rot,
        mat,
        col,
        parent,
        bevel_width=bevel_width,
        bevel_segments=bevel_segments,
        subsurf_levels=subsurf_levels,
        shade_smooth=shade_smooth,
    )


def create_tapered_box(
    name,
    bottom_xy,
    top_xy,
    height_z,
    location,
    mat,
    col,
    parent=None,
    rot=(0.0, 0.0, 0.0),
    bevel_width=0.02,
    bevel_segments=2,
    subsurf_levels=0,
    shade_smooth=False,
    offset_xyz=(0.0, 0.0, 0.0),
):
    """Create a tapered box (frustum) centered on local origin before offset_xyz."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bx, by = bottom_xy
    tx, ty = top_xy
    for v in bm.verts:
        if v.co.z < 0:
            v.co.x *= bx
            v.co.y *= by
            v.co.z = -height_z * 0.5
        else:
            v.co.x *= tx
            v.co.y *= ty
            v.co.z = height_z * 0.5
    ox, oy, oz = offset_xyz
    if ox != 0.0 or oy != 0.0 or oz != 0.0:
        bmesh.ops.translate(bm, vec=Vector((ox, oy, oz)), verts=bm.verts)
    return finalize_mesh_object(
        name,
        bm,
        location,
        rot,
        mat,
        col,
        parent,
        bevel_width=bevel_width,
        bevel_segments=bevel_segments,
        subsurf_levels=subsurf_levels,
        shade_smooth=shade_smooth,
    )


def create_cylinder(
    name,
    radius1,
    radius2,
    depth,
    vertices,
    location,
    mat,
    col,
    parent=None,
    rot=(0.0, 0.0, 0.0),
    bevel_width=0.0,
    subsurf_levels=0,
    shade_smooth=False,
    offset_xyz=(0.0, 0.0, 0.0),
):
    """Create a cylinder or truncated cone."""
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=vertices,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
    )
    ox, oy, oz = offset_xyz
    if ox != 0.0 or oy != 0.0 or oz != 0.0:
        bmesh.ops.translate(bm, vec=Vector((ox, oy, oz)), verts=bm.verts)
    return finalize_mesh_object(
        name,
        bm,
        location,
        rot,
        mat,
        col,
        parent,
        bevel_width=bevel_width,
        bevel_segments=2,
        subsurf_levels=subsurf_levels,
        shade_smooth=shade_smooth,
    )


def create_icosphere(
    name,
    radius,
    subdivisions,
    location,
    mat,
    col,
    parent=None,
    rot=(0.0, 0.0, 0.0),
    scale_xyz=(1.0, 1.0, 1.0),
    shade_smooth=False,
    offset_xyz=(0.0, 0.0, 0.0),
):
    """Create a stylized low-poly icosphere with optional non-uniform scale."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=radius)
    bmesh.ops.scale(bm, vec=Vector(scale_xyz), verts=bm.verts)
    ox, oy, oz = offset_xyz
    if ox != 0.0 or oy != 0.0 or oz != 0.0:
        bmesh.ops.translate(bm, vec=Vector((ox, oy, oz)), verts=bm.verts)
    return finalize_mesh_object(
        name, bm, location, rot, mat, col, parent, shade_smooth=shade_smooth
    )


def create_uv_sphere(
    name,
    radius,
    segments,
    rings,
    location,
    mat,
    col,
    parent=None,
    rot=(0.0, 0.0, 0.0),
    scale_xyz=(1.0, 1.0, 1.0),
    subsurf_levels=0,
    shade_smooth=True,
    offset_xyz=(0.0, 0.0, 0.0),
):
    """Create a UV sphere with optional non-uniform scale and subdivision."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=radius)
    bmesh.ops.scale(bm, vec=Vector(scale_xyz), verts=bm.verts)
    ox, oy, oz = offset_xyz
    if ox != 0.0 or oy != 0.0 or oz != 0.0:
        bmesh.ops.translate(bm, vec=Vector((ox, oy, oz)), verts=bm.verts)
    return finalize_mesh_object(
        name,
        bm,
        location,
        rot,
        mat,
        col,
        parent,
        subsurf_levels=subsurf_levels,
        shade_smooth=shade_smooth,
    )


def create_gabled_roof(
    name,
    width_x,
    depth_y,
    height_z,
    location,
    mat,
    col,
    parent=None,
    rot=(0.0, 0.0, 0.0),
    bevel_width=0.015,
):
    """Create a triangular prism roof (ridge along X axis, base at Z=0, peak at Z=height_z)."""
    bm = bmesh.new()
    hx = width_x * 0.5
    hy = depth_y * 0.5
    v0 = bm.verts.new((-hx, -hy, 0.0))
    v1 = bm.verts.new((hx, -hy, 0.0))
    v2 = bm.verts.new((hx, hy, 0.0))
    v3 = bm.verts.new((-hx, hy, 0.0))
    v4 = bm.verts.new((-hx, 0.0, height_z))
    v5 = bm.verts.new((hx, 0.0, height_z))

    bm.faces.new((v0, v3, v2, v1))
    bm.faces.new((v0, v1, v5, v4))
    bm.faces.new((v2, v3, v4, v5))
    bm.faces.new((v0, v4, v3))
    bm.faces.new((v1, v2, v5))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    return finalize_mesh_object(
        name, bm, location, rot, mat, col, parent, bevel_width=bevel_width, bevel_segments=2, shade_smooth=False
    )


def create_segmented_organic_tube(
    name,
    profile_rings,
    segments,
    location,
    mat,
    col,
    parent=None,
    cap_top=True,
    cap_bottom=True,
    subsurf_levels=1,
    shade_smooth=True,
):
    """Create a continuous multi-ring organic tube mesh along local Z for seamless limb/torso deformation.

    profile_rings: list of (z, rx, ry, offset_x, offset_y) ordered from top to bottom (or bottom to top).
    Returns the finalized Mesh Object ready for Armature vertex group weighting.
    """
    bm = bmesh.new()
    ring_Point_lists = []
    for z, rx, ry, ox, oy in profile_rings:
        ring_verts = []
        for i in range(segments):
            ang = (2.0 * math.pi * i) / segments
            x = ox + rx * math.cos(ang)
            y = oy + ry * math.sin(ang)
            ring_verts.append(bm.verts.new((x, y, z)))
        ring_Point_lists.append(ring_verts)

    for r_idx in range(len(ring_Point_lists) - 1):
        r_a = ring_Point_lists[r_idx]
        r_b = ring_Point_lists[r_idx + 1]
        for i in range(segments):
            i_next = (i + 1) % segments
            bm.faces.new((r_a[i], r_a[i_next], r_b[i_next], r_b[i]))

    if cap_top and ring_Point_lists:
        top_r = ring_Point_lists[0]
        top_z, _, _, ox, oy = profile_rings[0]
        c_top = bm.verts.new((ox, oy, top_z))
        for i in range(segments):
            i_next = (i + 1) % segments
            bm.faces.new((c_top, top_r[i_next], top_r[i]))

    if cap_bottom and ring_Point_lists:
        bot_r = ring_Point_lists[-1]
        bot_z, _, _, ox, oy = profile_rings[-1]
        c_bot = bm.verts.new((ox, oy, bot_z))
        for i in range(segments):
            i_next = (i + 1) % segments
            bm.faces.new((c_bot, bot_r[i], bot_r[i_next]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return finalize_mesh_object(
        name,
        bm,
        location,
        (0.0, 0.0, 0.0),
        mat,
        col,
        parent=parent,
        subsurf_levels=subsurf_levels,
        shade_smooth=shade_smooth,
    )


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Hermite smoothstep interpolation in [0, 1]."""
    if abs(edge1 - edge0) < 1e-6:
        return 1.0 if x >= edge1 else 0.0
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def bind_mesh_to_armature(mesh_obj, armature_obj, preserve_volume=True):
    """Parent mesh_obj to armature_obj and add an Armature modifier placed BEFORE Subdivision Surface."""
    mesh_obj.parent = armature_obj
    arm_mod = mesh_obj.modifiers.new(name="Armature", type="ARMATURE")
    arm_mod.object = armature_obj
    arm_mod.use_deform_preserve_volume = preserve_volume
    # Move Armature modifier to index 0 (before Subsurf) for smooth organic skinning
    if len(mesh_obj.modifiers) > 1:
        try:
            with bpy.context.temp_override(object=mesh_obj):
                bpy.ops.object.modifier_move_to_index(modifier=arm_mod.name, index=0)
        except Exception:
            pass
    return arm_mod

