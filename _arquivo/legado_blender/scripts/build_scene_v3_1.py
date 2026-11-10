"""Master CLI Orchestrator for MISSÃO V3.1 — Primeira montagem narrada do Nico (Blender 5.2 LTS).

Integrates the working Gemini TTS narration (`audio/narracoes/EP001/testes/narracao_B_flash_lite_V1.wav`)
into the existing V3 scene (`arquivo/EP001/piloto/cenas/cena_01_V3.blend`) WITHOUT rebuilding the
character, environment, or modeling pipeline.

Usage:
  blender -b -P scripts/build_scene_v3_1.py -- --mode build
  blender -b -P scripts/build_scene_v3_1.py -- --mode audit-stills
  blender -b -P scripts/build_scene_v3_1.py -- --mode preview-videos
  blender -b -P scripts/build_scene_v3_1.py -- --mode replace-voice --audio <novo_arquivo.wav>
"""

import argparse
import json
import shutil
import sys
from pathlib import Path
import bpy

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from pipeline_v3 import audio_finalizer, config, render_pipeline, scene_setup, v3_1_narrated_scene

PILOT_CACHE = config.PROJECT_CACHE_DIR / "EP001" / "piloto_V3_1"
SCENES_DIR = PILOT_CACHE / "cenas"
PREVIEWS_DIR = PILOT_CACHE / "previews"
VIDEOS_DIR = PILOT_CACHE / "videos"

BASE_V3_BLEND = config.EP001_PILOT_DIR / "cenas" / "cena_01_V3.blend"
V3_1_BLEND = SCENES_DIR / "cena_01_V3_1.blend"
V3_1_CARIMBO_BLEND = SCENES_DIR / "cena_01_V3_1_com_carimbo.blend"
CARIMBO_ASSET_BLEND = PILOT_CACHE / "objetos" / "carimbo_duvida.blend"

DEFAULT_WAV = PROJECT_ROOT / "audio" / "narracoes" / "EP001" / "testes" / "narracao_B_flash_lite_V1.wav"
DEFAULT_TIMING = PROJECT_ROOT / "timing.json"
V3_1_PREVIEWS_DIR = PREVIEWS_DIR / "v3_1"


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="EP001 V3.1 Narrated Synchronization Pipeline")
    parser.add_argument(
        "--mode",
        choices=["build", "audit-stills", "preview-videos", "finalize-audio", "replace-voice", "all-preview"],
        default="build",
        help="Execution mode for V3.1 narrated montage.",
    )
    parser.add_argument(
        "--audio",
        type=str,
        default=str(DEFAULT_WAV),
        help="Path to the narration WAV file (defaults to working narration narracao_B_flash_lite_V1.wav).",
    )
    parser.add_argument(
        "--timing",
        type=str,
        default=str(DEFAULT_TIMING),
        help="Path to timing.json containing phrase boundaries.",
    )
    return parser.parse_args(argv)


def build_v3_1_scenes(wav_path: Path, timing_path: Path):
    """Build standalone Carimbo library, waveform PNG, and both V3.1 .blend variants from cena_01_V3.blend."""
    if not BASE_V3_BLEND.is_file():
        raise FileNotFoundError(f"Base V3 scene not found: {BASE_V3_BLEND}")
    if not wav_path.is_file():
        raise FileNotFoundError(f"Narration WAV not found: {wav_path}")

    timing_data = v3_1_narrated_scene.load_timing_json(timing_path)

    # 1. Save standalone reusable 'Carimbo da Dúvida' asset library (objetos/carimbo_duvida.blend)
    v3_1_narrated_scene.save_standalone_carimbo_library(CARIMBO_ASSET_BLEND)

    # 2. Generate waveform + RMS envelope visualization PNG with phrase boundaries
    waveform_png = V3_1_PREVIEWS_DIR / "waveform_timing_v3_1.png"
    v3_1_narrated_scene.generate_waveform_visualization(wav_path, timing_data, waveform_png)

    SCENES_DIR.mkdir(parents=True, exist_ok=True)

    # 3. Open cena_01_V3.blend (preserving 100% of character, environment, and materials)
    #    First save variant WITHOUT visual signature (cena_01_V3_1.blend)
    bpy.ops.wm.open_mainfile(filepath=str(BASE_V3_BLEND))
    scene = bpy.context.scene
    info = v3_1_narrated_scene.retime_scene_to_timing_data(scene, timing_data, include_carimbo=False)
    v3_1_narrated_scene.setup_vse_narration_audio(scene, wav_path)
    render_pipeline.embed_script_in_blend(Path(__file__), text_name="build_scene_v3_1.py")
    scene.frame_set(1)
    render_pipeline.save_blend_file(V3_1_BLEND)
    print(f"[OK] Saved V3.1 narrated scene (without Carimbo): {V3_1_BLEND}")

    # 4. Save variant WITH 'Carimbo da Dúvida' visual signature (cena_01_V3_1_com_carimbo.blend)
    v3_1_narrated_scene.retime_scene_to_timing_data(scene, timing_data, include_carimbo=True)
    v3_1_narrated_scene.setup_vse_narration_audio(scene, wav_path)
    scene.frame_set(1)
    render_pipeline.save_blend_file(V3_1_CARIMBO_BLEND)
    print(f"[OK] Saved V3.1 narrated scene (with Carimbo da Dúvida): {V3_1_CARIMBO_BLEND}")

    return timing_data, info


def render_v3_1_audit_stills(wav_path: Path, timing_path: Path):
    """Render the 9 phrase synchronization stills and the side-by-side Carimbo da Dúvida comparison."""
    if not V3_1_BLEND.is_file() or not V3_1_CARIMBO_BLEND.is_file():
        build_v3_1_scenes(wav_path, timing_path)

    timing_data = v3_1_narrated_scene.load_timing_json(timing_path)
    V3_1_PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

    # Open base V3.1 scene (without Carimbo) and render the 9 phrase audit frames
    bpy.ops.wm.open_mainfile(filepath=str(V3_1_BLEND))
    scene = bpy.context.scene
    info = v3_1_narrated_scene.retime_scene_to_timing_data(scene, timing_data, include_carimbo=False)

    orig_start, orig_end = scene.frame_start, scene.frame_end
    scene_setup.configure_scene_and_render(scene, preset_name="preview_stills")
    scene.frame_start, scene.frame_end = orig_start, orig_end

    for fr, label in info["key_audit_frames"]:
        scene.frame_set(fr)
        out_png = V3_1_PREVIEWS_DIR / f"frame_{fr:03d}_{label}.png"
        scene.render.filepath = str(out_png)
        bpy.ops.render.render(write_still=True)
        print(f"[OK] Rendered V3.1 audit still (f{fr}): {out_png}")

    # Render Frame 530 WITHOUT Carimbo da Dúvida
    f_comp = info["key_audit_frames"][-1][0]
    no_carimbo_png = V3_1_PREVIEWS_DIR / f"carimbo_sem_assinatura_f{f_comp:03d}.png"
    scene.frame_set(f_comp)
    scene.render.filepath = str(no_carimbo_png)
    bpy.ops.render.render(write_still=True)

    # Switch to WITH Carimbo da Dúvida and render Frame 530
    v3_1_narrated_scene.retime_scene_to_timing_data(scene, timing_data, include_carimbo=True)
    with_carimbo_png = V3_1_PREVIEWS_DIR / f"carimbo_com_assinatura_f{f_comp:03d}.png"
    scene.frame_set(f_comp)
    scene.render.filepath = str(with_carimbo_png)
    bpy.ops.render.render(write_still=True)

    # Build side-by-side comparison sheet
    comp_sheet_png = V3_1_PREVIEWS_DIR / "comparativo_carimbo_duvida.png"
    v3_1_narrated_scene.generate_carimbo_comparison_sheet(
        no_carimbo_png,
        with_carimbo_png,
        comp_sheet_png,
    )


def render_v3_1_preview_videos(wav_path: Path, timing_path: Path):
    """Render low-resolution (540x960) MP4 previews with synchronized AAC audio (with and without Carimbo)."""
    if not V3_1_BLEND.is_file() or not V3_1_CARIMBO_BLEND.is_file():
        build_v3_1_scenes(wav_path, timing_path)

    # 1. Low-res MP4 WITHOUT Carimbo da Dúvida (clean baseline)
    bpy.ops.wm.open_mainfile(filepath=str(V3_1_BLEND))
    scene = bpy.context.scene
    mp4_without = VIDEOS_DIR / "preview_V3_1_1_sem_carimbo_lowres.mp4"
    v3_1_narrated_scene.render_narrated_mp4_preview(
        scene,
        output_mp4_path=mp4_without,
        wav_path=wav_path,
        preset_name="preview_video",
    )
    # Also copy to canonical preview_V3_1_1_narrado_lowres.mp4
    mp4_canonical = VIDEOS_DIR / "preview_V3_1_1_narrado_lowres.mp4"
    shutil.copy2(mp4_without, mp4_canonical)
    print(f"[OK] Copied canonical narrated preview: {mp4_canonical}")

    # 2. Low-res MP4 WITH Carimbo da Dúvida (optional visual signature variant)
    bpy.ops.wm.open_mainfile(filepath=str(V3_1_CARIMBO_BLEND))
    scene = bpy.context.scene
    mp4_with = VIDEOS_DIR / "preview_V3_1_1_com_carimbo_lowres.mp4"
    v3_1_narrated_scene.render_narrated_mp4_preview(
        scene,
        output_mp4_path=mp4_with,
        wav_path=wav_path,
        preset_name="preview_video",
    )


def finalize_existing_v3_1_videos(wav_path: Path, timing_path: Path) -> dict:
    """Finalize existing Blender-rendered V3.1 MP4 videos with FFmpeg AAC muxing & verification (NO re-render)."""
    timing_data = v3_1_narrated_scene.load_timing_json(timing_path)
    expected_dur = float(timing_data["timeline_config"]["scene_duration_sec"])

    in_without = config.EP001_PILOT_DIR / "videos" / "preview_V3_1_sem_carimbo_lowres.mp4"
    in_with = config.EP001_PILOT_DIR / "videos" / "preview_V3_1_com_carimbo_lowres.mp4"

    out_without = VIDEOS_DIR / "preview_V3_1_1_sem_carimbo_lowres.mp4"
    out_canonical = VIDEOS_DIR / "preview_V3_1_1_narrado_lowres.mp4"
    out_with = VIDEOS_DIR / "preview_V3_1_1_com_carimbo_lowres.mp4"

    rep_without = audio_finalizer.finalize_mp4_with_narration(
        video_mp4_path=in_without,
        wav_path=wav_path,
        output_mp4_path=out_without,
        expected_duration_sec=expected_dur,
        timing_data=timing_data,
    )
    shutil.copy2(out_without, out_canonical)
    rep_canonical = audio_finalizer.verify_finalized_mp4(
        mp4_path=out_canonical,
        wav_path=wav_path,
        expected_duration_sec=expected_dur,
        timing_data=timing_data,
    )

    rep_with = audio_finalizer.finalize_mp4_with_narration(
        video_mp4_path=in_with,
        wav_path=wav_path,
        output_mp4_path=out_with,
        expected_duration_sec=expected_dur,
        timing_data=timing_data,
    )

    summary = {
        "mission": "V3.1.1 — Correção e Validação Automática de Áudio FFmpeg/FFprobe",
        "re_rendered_in_blender": False,
        "preserved_previous_v3_and_v3_1_files": True,
        "outputs": {
            "sem_carimbo": rep_without,
            "narrado_canonical": rep_canonical,
            "com_carimbo": rep_with,
        },
    }
    report_path = VIDEOS_DIR / "relatorio_auditoria_audio_V3_1_1.json"
    report_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] Saved audio verification report: {report_path}")
    return summary


def main():
    args = parse_args()
    wav_path = Path(args.audio).resolve()
    timing_path = Path(args.timing).resolve()

    if args.mode == "build":
        build_v3_1_scenes(wav_path, timing_path)
    elif args.mode == "audit-stills":
        render_v3_1_audit_stills(wav_path, timing_path)
    elif args.mode == "preview-videos":
        render_v3_1_preview_videos(wav_path, timing_path)
    elif args.mode == "finalize-audio":
        finalize_existing_v3_1_videos(wav_path, timing_path)
    elif args.mode == "replace-voice":
        print(f"[REPLACE VOICE] Updating V3.1 scene with audio={wav_path} and timing={timing_path}")
        build_v3_1_scenes(wav_path, timing_path)
        render_v3_1_preview_videos(wav_path, timing_path)
    elif args.mode == "all-preview":
        build_v3_1_scenes(wav_path, timing_path)
        render_v3_1_audit_stills(wav_path, timing_path)
        render_v3_1_preview_videos(wav_path, timing_path)


if __name__ == "__main__":
    main()
