"""Scene initialization, idempotent cleanup, collections, and Blender 5.2 fcurve helpers."""

import bpy
from . import config

COLLECTION_NAMES = (
    "Col_Cenario_Vila",
    "Col_Feira_Barraca",
    "Col_Personagem_Nico",
    "Col_Props_Animados",
    "Col_Luzes_Cameras",
)


def clean_scene():
    """Remove all existing objects, collections, and orphan data blocks for idempotent execution."""
    # Ensure we are in Object mode if there is an active object
    if bpy.context.active_object and bpy.context.active_object.mode != "OBJECT":
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass

    # Remove all objects
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    # Remove all custom collections
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)

    # Purge data-blocks to avoid duplicates (.001, .002)
    for block_collection in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.lights,
        bpy.data.cameras,
        bpy.data.actions,
        bpy.data.curves,
    ):
        for block in list(block_collection):
            block_collection.remove(block)


def create_collections(scene):
    """Create and link organized collections to the scene master collection."""
    cols = {}
    for name in COLLECTION_NAMES:
        col = bpy.data.collections.get(name)
        if not col:
            col = bpy.data.collections.new(name)
            scene.collection.children.link(col)
        cols[name] = col
    return cols


def link_to_collection(obj, col):
    """Ensure an object is linked only to the target collection."""
    for existing_col in list(obj.users_collection):
        existing_col.objects.unlink(obj)
    col.objects.link(obj)


def configure_scene_and_render(scene, preset_name="preview_stills"):
    """Configure timeline (30 FPS, 450 frames), 9:16 vertical resolution, and EEVEE settings."""
    scene.frame_start = config.FRAME_START
    scene.frame_end = config.FRAME_END
    scene.render.fps = config.FPS
    scene.render.fps_base = 1.0

    scene.render.resolution_x = config.RES_X
    scene.render.resolution_y = config.RES_Y

    preset = config.RENDER_PRESETS.get(preset_name, config.RENDER_PRESETS["preview_stills"])
    scene.render.resolution_percentage = preset["resolution_percentage"]

    # Configure EEVEE for Blender 5.2 LTS
    scene.render.engine = "BLENDER_EEVEE"
    eevee = scene.eevee
    eevee.taa_render_samples = preset["taa_render_samples"]
    eevee.taa_samples = 16
    eevee.use_shadows = True
    if hasattr(eevee, "shadow_ray_count"):
        eevee.shadow_ray_count = 2
    if hasattr(eevee, "shadow_step_count"):
        eevee.shadow_step_count = 6
    if hasattr(eevee, "use_fast_gi"):
        eevee.use_fast_gi = False

    # Color management
    if hasattr(scene, "view_settings"):
        try:
            scene.view_settings.view_transform = "AgX"
        except Exception:
            pass
        scene.view_settings.exposure = 0.0
        scene.view_settings.gamma = 1.0

    # Default output format to PNG image
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"


def iter_object_fcurves(obj):
    """Yield all F-Curves for an object across Blender 4.x and Blender 5.2 Slotted Actions."""
    if not obj or not obj.animation_data or not obj.animation_data.action:
        return
    act = obj.animation_data.action
    if hasattr(act, "fcurves"):
        for fc in act.fcurves:
            yield fc
    if hasattr(act, "layers"):
        for layer in act.layers:
            for strip in layer.strips:
                if hasattr(strip, "channelbags"):
                    for bag in strip.channelbags:
                        for fc in bag.fcurves:
                            yield fc


def set_interpolation(obj, data_path_prefix=None, interpolation="BEZIER", frame_range=None):
    """Set keyframe interpolation on an object's F-Curves (compatible with Blender 5.2)."""
    for fc in iter_object_fcurves(obj):
        if data_path_prefix and not fc.data_path.startswith(data_path_prefix):
            continue
        for kp in fc.keyframe_points:
            if frame_range is not None:
                f_min, f_max = frame_range
                if not (f_min - 0.1 <= kp.co[0] <= f_max + 0.1):
                    continue
            kp.interpolation = interpolation
            if interpolation == "BEZIER":
                kp.handle_left_type = "AUTO_CLAMPED"
                kp.handle_right_type = "AUTO_CLAMPED"
        fc.update()

