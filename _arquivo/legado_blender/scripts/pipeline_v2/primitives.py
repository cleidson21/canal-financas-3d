"""Procedural low-poly geometry primitives built with bmesh and modifiers (Blender 5.2 LTS)."""

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


def _finalize_mesh_object(name, bm, location, rot, mat, col, parent, bevel_width=0.0, bevel_segments=2, shade_smooth=False):
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
    shade_smooth=False,
    offset_xyz=(0.0, 0.0, 0.0),
):
    """Create a box with optional local vertex offset and bevel modifier."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = size_xyz
    ox, oy, oz = offset_xyz
    bmesh.ops.scale(bm, vec=Vector((sx, sy, sz)), verts=bm.verts)
    if ox != 0.0 or oy != 0.0 or oz != 0.0:
        bmesh.ops.translate(bm, vec=Vector((ox, oy, oz)), verts=bm.verts)
    return _finalize_mesh_object(
        name, bm, location, rot, mat, col, parent, bevel_width, bevel_segments, shade_smooth
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
    shade_smooth=False,
    offset_xyz=(0.0, 0.0, 0.0),
):
    """Create a tapered box (frustum) useful for stylized torsos, crates, and limbs."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bx, by = bottom_xy
    tx, ty = top_xy
    ox, oy, oz = offset_xyz
    for v in bm.verts:
        is_top = v.co.z > 0
        v.co.x = v.co.x * (tx if is_top else bx) + ox
        v.co.y = v.co.y * (ty if is_top else by) + oy
        v.co.z = v.co.z * height_z + oz
    return _finalize_mesh_object(
        name, bm, location, rot, mat, col, parent, bevel_width, bevel_segments, shade_smooth
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
    bevel_width=0.01,
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
    return _finalize_mesh_object(
        name, bm, location, rot, mat, col, parent, bevel_width, 2, shade_smooth
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
    """Create a low-poly icosphere with optional non-uniform scale."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=radius)
    bmesh.ops.scale(bm, vec=Vector(scale_xyz), verts=bm.verts)
    ox, oy, oz = offset_xyz
    if ox != 0.0 or oy != 0.0 or oz != 0.0:
        bmesh.ops.translate(bm, vec=Vector((ox, oy, oz)), verts=bm.verts)
    return _finalize_mesh_object(
        name, bm, location, rot, mat, col, parent, 0.0, 1, shade_smooth
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
    shade_smooth=True,
    offset_xyz=(0.0, 0.0, 0.0),
):
    """Create a UV sphere with optional non-uniform scale."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=radius)
    bmesh.ops.scale(bm, vec=Vector(scale_xyz), verts=bm.verts)
    ox, oy, oz = offset_xyz
    if ox != 0.0 or oy != 0.0 or oz != 0.0:
        bmesh.ops.translate(bm, vec=Vector((ox, oy, oz)), verts=bm.verts)
    return _finalize_mesh_object(
        name, bm, location, rot, mat, col, parent, 0.0, 1, shade_smooth
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

    bm.faces.new((v0, v3, v2, v1))  # Bottom
    bm.faces.new((v0, v1, v5, v4))  # Front slope (-Y)
    bm.faces.new((v2, v3, v4, v5))  # Back slope (+Y)
    bm.faces.new((v0, v4, v3))      # Left gable (-X)
    bm.faces.new((v1, v2, v5))      # Right gable (+X)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    return _finalize_mesh_object(
        name, bm, location, rot, mat, col, parent, bevel_width, 2, False
    )

