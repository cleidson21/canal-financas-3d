"""Render, validation, and contact-sheet utilities for Pipeline V3 (Blender 5.2 LTS)."""

from pathlib import Path
import bpy
from . import config
from .scene_setup import configure_scene_and_render


def embed_script_in_blend(script_path: Path, text_name="build_scene.py"):
    """Store the entry script inside the .blend Text Editor for convenient inspection inside Blender."""
    p = Path(script_path)
    if not p.is_file():
        return
    code = p.read_text(encoding="utf-8")
    txt = bpy.data.texts.get(text_name)
    if not txt:
        txt = bpy.data.texts.new(text_name)
    txt.clear()
    txt.write(code)


def save_blend_file(blend_path: Path):
    """Save the current Blender scene to the target .blend path (protecting V1/V2 backups)."""
    p = Path(blend_path).resolve()
    if p.name.lower() in ("teste1.blend", "teste1_v2.blend", "cena_01_v2.blend"):
        raise ValueError(f"Refusing to overwrite protected legacy file: {p}")
    p.parent.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.frame_set(1)
    # Evita o erro de caminho do cache de miniaturas neste processo.
    bpy.context.preferences.filepaths.file_preview_type = 'NONE'
    bpy.ops.wm.save_as_mainfile(filepath=str(p), relative_remap=True)
    print(f"[OK] Saved V3 blend file: {p}")


def render_frame_list(scene, output_dir: Path, frame_list, preset_name="preview_stills"):
    """Render a list of (frame_num, label) PNG stills for visual inspection."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    configure_scene_and_render(scene, preset_name=preset_name)
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"

    rendered = []
    for frame_num, label in frame_list:
        scene.frame_set(frame_num)
        out_path = out_dir / f"frame_{frame_num:03d}_{label}.png"
        scene.render.filepath = str(out_path)
        bpy.ops.render.render(write_still=True)
        rendered.append(out_path)
        print(f"[OK] Rendered still frame {frame_num}: {out_path}")

    return rendered


def render_character_and_shoe_closeups(scene, output_dir: Path, preset_name="high_stills"):
    """Render dedicated close-ups of Nico V3 (face, full body, and damaged sneaker opening) using a dedicated temp camera."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    configure_scene_and_render(scene, preset_name=preset_name)
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"

    orig_cam = scene.camera

    # Create un-keyframed temporary camera and target so scene.frame_set() never overrides close-up angles
    tgt_temp = bpy.data.objects.new("Target_Closeup_Temp", None)
    scene.collection.objects.link(tgt_temp)

    cam_data = bpy.data.cameras.new(name="Cam_Closeup_Temp")
    cam_data.type = "PERSP"
    cam_data.lens = 50.0
    cam_data.clip_start = 0.05
    cam_data.clip_end = 100.0
    cam_temp = bpy.data.objects.new("Cam_Closeup_Temp", cam_data)
    scene.collection.objects.link(cam_temp)

    track = cam_temp.constraints.new(type="TRACK_TO")
    track.target = tgt_temp
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    scene.camera = cam_temp
    scene.frame_set(15)

    closeups = [
        ("closeup_01_sapato_descolado_frontal.png", 15, (-1.66, -1.72, 0.32), (-2.04, -0.66, 0.18)),
        ("closeup_02_sapato_descolado_perfil.png", 15, (-1.28, -1.18, 0.25), (-2.04, -0.66, 0.17)),
        ("closeup_03_nico_v3_rosto_expressao.png", 105, (-1.45, -2.42, 1.48), (-1.72, -0.54, 1.38)),
        ("closeup_04_nico_v3_corpo_inteiro.png", 15, (-1.82, -3.55, 1.02), (-2.12, -0.61, 0.85)),
    ]
    paths = []
    for fname, fr, c_loc, t_loc in closeups:
        scene.frame_set(fr)
        cam_temp.location = c_loc
        tgt_temp.location = t_loc
        bpy.context.view_layer.update()
        out_path = out_dir / fname
        scene.render.filepath = str(out_path)
        bpy.ops.render.render(write_still=True)
        paths.append(out_path)
        print(f"[OK] Rendered close-up: {out_path}")

    # Restore original camera and clean up temporary objects
    scene.camera = orig_cam
    bpy.data.objects.remove(cam_temp, do_unlink=True)
    bpy.data.cameras.remove(cam_data, do_unlink=True)
    bpy.data.objects.remove(tgt_temp, do_unlink=True)
    scene.frame_set(1)
    return paths


def generate_v2_v3_contact_sheet(v2_dir: Path, v3_dir: Path, output_path: Path):
    """Create a side-by-side V2 vs. V3 contact sheet PNG from the 8 equivalent narrative frames."""
    import numpy as np

    v2_dir = Path(v2_dir)
    v3_dir = Path(v3_dir)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pairs = []
    for fr, label in config.V2_EQUIVALENT_FRAMES:
        p2 = v2_dir / f"frame_{fr:03d}_{label}.png"
        p3 = v3_dir / f"frame_{fr:03d}_{label}.png"
        if p2.is_file() and p3.is_file():
            pairs.append((p2, p3))

    if not pairs:
        print("[WARN] Could not find matching V2 and V3 frames for contact sheet.")
        return None

    cell_w, cell_h = 270, 480
    pad = 8
    cols = 2  # 2 pairs per row = 4 images per row (V2, V3 | V2, V3)
    rows = (len(pairs) + cols - 1) // cols

    sheet_w = cols * (cell_w * 2 + pad * 3) + pad
    sheet_h = rows * (cell_h + pad * 2) + pad

    # Dark slate background (RGBA float32, bottom-to-top in Blender image coordinates)
    canvas = np.full((sheet_h, sheet_w, 4), (0.10, 0.11, 0.13, 1.0), dtype=np.float32)

    def _load_resized(img_path: Path, target_w: int, target_h: int) -> np.ndarray:
        img = bpy.data.images.load(str(img_path), check_existing=False)
        img.scale(target_w, target_h)
        arr = np.empty(target_w * target_h * 4, dtype=np.float32)
        img.pixels.foreach_get(arr)
        bpy.data.images.remove(img)
        return arr.reshape((target_h, target_w, 4))

    for idx, (p2, p3) in enumerate(pairs):
        r = idx // cols
        c = idx % cols
        # Invert row index so pair 0 is at the top of the image
        inv_r = (rows - 1) - r
        y0 = pad + inv_r * (cell_h + pad * 2) + pad
        x0_v2 = pad + c * (cell_w * 2 + pad * 3) + pad
        x0_v3 = x0_v2 + cell_w + pad

        arr2 = _load_resized(p2, cell_w, cell_h)
        arr3 = _load_resized(p3, cell_w, cell_h)

        # Subtle red border above V2, green border above V3
        canvas[y0 + cell_h : y0 + cell_h + 4, x0_v2 : x0_v2 + cell_w] = (0.85, 0.22, 0.20, 1.0)
        canvas[y0 + cell_h : y0 + cell_h + 4, x0_v3 : x0_v3 + cell_w] = (0.18, 0.80, 0.35, 1.0)

        canvas[y0 : y0 + cell_h, x0_v2 : x0_v2 + cell_w] = arr2
        canvas[y0 : y0 + cell_h, x0_v3 : x0_v3 + cell_w] = arr3

    out_img = bpy.data.images.new("Comparativo_V2_vs_V3", width=sheet_w, height=sheet_h, alpha=True)
    out_img.pixels.foreach_set(canvas.ravel())
    out_img.filepath_raw = str(output_path)
    out_img.file_format = "PNG"
    out_img.save()
    bpy.data.images.remove(out_img)
    print(f"[OK] Generated V2 vs. V3 contact sheet: {output_path}")
    return output_path


def render_mp4_animation(
    scene,
    output_mp4_path: Path,
    preset_name="preview_video",
    frame_start=None,
    frame_end=None,
):
    """Render an H.264 MP4 animation (either full 15s 450 frames or a custom range such as 3s Opening test)."""
    out_mp4 = Path(output_mp4_path).resolve()
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    configure_scene_and_render(scene, preset_name=preset_name)

    orig_start = scene.frame_start
    orig_end = scene.frame_end
    if frame_start is not None:
        scene.frame_start = frame_start
    if frame_end is not None:
        scene.frame_end = frame_end

    scene.render.image_settings.media_type = "VIDEO"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    scene.render.ffmpeg.gopsize = 15
    scene.render.ffmpeg.audio_codec = "NONE"

    scene.render.filepath = str(out_mp4)
    bpy.ops.render.render(animation=True)

    scene.frame_start = orig_start
    scene.frame_end = orig_end
    print(f"[OK] Rendered MP4 animation: {out_mp4}")
    return out_mp4
