"""Render and validation utilities for saving Teste1_V2.blend, rendering keyframe previews, and exporting MP4."""

import os
import bpy
from . import config
from .scene_setup import configure_scene_and_render


def embed_script_in_blend(script_path, text_name="build_scene_v2.py"):
    """Store the entry script inside the .blend Text Editor for convenient inspection inside Blender."""
    if not os.path.isfile(script_path):
        return
    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()
    txt = bpy.data.texts.get(text_name)
    if not txt:
        txt = bpy.data.texts.new(text_name)
    txt.clear()
    txt.write(code)


def save_blend_file(blend_path):
    """Save the current Blender scene to the target .blend path (never overwriting Teste1.blend)."""
    if os.path.basename(blend_path).lower() == "teste1.blend":
        raise ValueError("Refusing to overwrite protected file Teste1.blend!")
    os.makedirs(os.path.dirname(os.path.abspath(blend_path)), exist_ok=True)
    bpy.context.scene.frame_set(1)
    # Evita o erro de caminho do cache de miniaturas neste processo.
    bpy.context.preferences.filepaths.file_preview_type = 'NONE'
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved blend file: {blend_path}")


def render_representative_frames(scene, output_dir, preset_name="preview_stills"):
    """Render representative PNG frames for visual quality inspection across all storyboard beats."""
    os.makedirs(output_dir, exist_ok=True)
    configure_scene_and_render(scene, preset_name=preset_name)
    scene.render.image_settings.media_type = "IMAGE"
    scene.render.image_settings.file_format = "PNG"

    rendered_paths = []
    for frame_num, label in config.REPRESENTATIVE_FRAMES:
        scene.frame_set(frame_num)
        out_path = os.path.join(output_dir, f"frame_{frame_num:03d}_{label}.png")
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        rendered_paths.append(out_path)
        print(f"[OK] Rendered still frame {frame_num}: {out_path}")

    return rendered_paths


def render_mp4_animation(scene, output_mp4_path, preset_name="preview_video"):
    """Render the full 450-frame (15s @ 30 FPS) animation to an H.264 MP4 video file."""
    os.makedirs(os.path.dirname(os.path.abspath(output_mp4_path)), exist_ok=True)
    configure_scene_and_render(scene, preset_name=preset_name)

    # Blender 5.0+ requires media_type = 'VIDEO' before setting FFMPEG container/codec
    scene.render.image_settings.media_type = "VIDEO"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    scene.render.ffmpeg.gopsize = 15
    scene.render.ffmpeg.audio_codec = "NONE"

    scene.render.filepath = output_mp4_path
    bpy.ops.render.render(animation=True)
    print(f"[OK] Rendered MP4 animation: {output_mp4_path}")
    return output_mp4_path

