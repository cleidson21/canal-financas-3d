"""Scene initialization, idempotent cleanup, collections, and Blender 5.2 Slotted Action F-Curve helpers."""

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
    if bpy.context.active_object and bpy.context.active_object.mode != "OBJECT":
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass

    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)

    for block_collection in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.lights,
        bpy.data.cameras,
        bpy.data.armatures,
        bpy.data.actions,
        bpy.data.curves,
    ):
        for block in list(block_collection):
            block_collection.remove(block)


def create_collections(scene):
    """Create and link organized semantic collections to the scene master collection."""
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
    if obj.name not in col.objects:
        col.objects.link(obj)


def configure_scene_and_render(scene, preset_name="preview_stills"):
    """Configure 9:16 vertical format (1080x1920), 30 FPS, 450 frames, and EEVEE Next in Blender 5.2."""
    preset = config.RENDER_PRESETS.get(preset_name, config.RENDER_PRESETS["preview_stills"])

    scene.frame_start = config.FRAME_START
    scene.frame_end = config.FRAME_END
    scene.render.fps = config.FPS
    scene.render.fps_base = 1.0

    scene.render.resolution_x = config.RES_X
    scene.render.resolution_y = config.RES_Y
    scene.render.resolution_percentage = preset["resolution_percentage"]
    scene.render.use_sequencer = False

    # Blender 5.2 EEVEE engine
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            scene.render.engine = eng
            break
        except Exception:
            continue

    eevee = getattr(scene, "eevee", None)
    if eevee:
        if hasattr(eevee, "taa_render_samples"):
            eevee.taa_render_samples = preset["taa_render_samples"]
        if hasattr(eevee, "taa_samples"):
            eevee.taa_samples = 16
        if hasattr(eevee, "use_shadows"):
            eevee.use_shadows = True
        if hasattr(eevee, "use_raytracing"):
            eevee.use_raytracing = False
        if hasattr(eevee, "use_fast_gi"):
            eevee.use_fast_gi = False

    if hasattr(scene, "view_settings"):
        try:
            scene.view_settings.view_transform = "AgX"
            if hasattr(scene.view_settings, "look"):
                scene.view_settings.look = "AgX - Medium High Contrast"
        except Exception:
            pass
        scene.view_settings.exposure = 0.08
        scene.view_settings.gamma = 1.0

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
    """Set keyframe interpolation on an object's F-Curves (compatible with Blender 5.2 Slotted Actions)."""
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


def set_camera_cut_holds(obj, cut_Hold_frames):
    """Set specific keyframe frames (e.g., frame right before a hard camera cut) to CONSTANT or VECTOR so camera cuts instantaneously without drifting across the cut boundary."""
    cut_set = set(cut_Hold_frames)
    for fc in iter_object_fcurves(obj):
        n = len(fc.keyframe_points)
        for i, kp in enumerate(fc.keyframe_points):
            fr = int(round(kp.co[0]))
            if fr in cut_set:
                # Hold or linear up to the exact cut frame, then jump on the next frame
                kp.interpolation = "CONSTANT"
            else:
                kp.interpolation = "BEZIER"
                kp.handle_left_type = "AUTO_CLAMPED"
                kp.handle_right_type = "AUTO_CLAMPED"
                # If previous keyframe was a cut hold, make left handle vector to avoid overshoot after cut
                if i > 0 and int(round(fc.keyframe_points[i - 1].co[0])) in cut_set:
                    kp.handle_left_type = "VECTOR"
                # If next keyframe is a cut hold, make right handle vector
                if i + 1 < n and int(round(fc.keyframe_points[i + 1].co[0])) in cut_set:
                    kp.handle_right_type = "VECTOR"
        fc.update()

