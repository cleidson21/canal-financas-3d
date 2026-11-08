"""Assemble and finalize the complete EP001-V2 deliverables from verified 1080x1920 rendered frames.

Produces:
- episodios/EP001_dinheiro/ENTREGAS/EP001_COMPLETO_V2_SEM_LEGENDAS.mp4 (1080x1920, 30 FPS, with audio)
- episodios/EP001_dinheiro/ENTREGAS/EP001_COMPLETO_V2_COM_LEGENDAS.mp4 (1080x1920, 30 FPS, with audio & burned-in ASS)
- episodios/EP001_dinheiro/ENTREGAS/EP001_PREVIA_V2.mp4 (360x640, 30 FPS, with audio)
- episodios/EP001_dinheiro/TESTES/EP001_V2_VALIDACAO.json (full audio/video verification report)
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]

from pipeline_v3.audio_finalizer import (
    finalize_mp4_with_narration,
    probe_media_file,
    resolve_ffmpeg_binaries,
    verify_finalized_mp4,
)


def digest(path: Path) -> str:
    with path.open("rb") as s:
        return hashlib.file_digest(s, "sha256").hexdigest()


def verified_frame(path: Path) -> bool:
    sha = path.with_suffix(".sha256")
    try:
        return path.is_file() and sha.is_file() and sha.read_text(encoding="ascii").strip() == digest(path)
    except Exception:
        return False


def decode_check(ffmpeg_bin: str, mp4_path: Path) -> dict:
    t0 = time.perf_counter()
    res = subprocess.run([ffmpeg_bin, "-v", "error", "-xerror", "-i", str(mp4_path), "-f", "null", "-"], capture_output=True, text=True)
    if res.returncode != 0 or res.stderr.strip():
        raise RuntimeError(f"Full decode check failed for {mp4_path.name}: {res.stderr.strip()}")
    return {
        "file": mp4_path.name,
        "status": "PASSED",
        "decode_seconds": round(time.perf_counter() - t0, 3),
        "errors": 0,
        "sha256": digest(mp4_path),
    }


def main():
    t0 = time.perf_counter()
    spec_path = ROOT / "episodios/EP001_dinheiro/TESTES/EP001_V2_DECUPAGEM.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    timing_ep = json.loads((ROOT / spec["timing"]).read_text(encoding="utf-8"))
    total_frames = int(spec["total_quadros"])  # 3064
    fps = int(spec["fps"])  # 30
    expected_dur = round(total_frames / fps, 6)  # 102.133333

    cache_root = ROOT / spec["cache"]
    seq_dir = ROOT / ".cache/EP001/seq_ep001_v2_1080x1920"
    seq_dir.mkdir(parents=True, exist_ok=True)

    # 1. Verify all 3,064 frames across the 24 plans and link/copy into contiguous sequence directory
    frame_sources = {}
    for plan in spec["plans"]:
        pid = plan["id"]
        f_start, f_end = plan["frames"]
        plan_parent = cache_root / pid
        if not plan_parent.is_dir():
            raise FileNotFoundError(f"Missing cache directory for plan {pid}: {plan_parent}")
        sig_dirs = sorted([d for d in plan_parent.iterdir() if d.is_dir()], key=lambda x: x.stat().st_mtime)
        if not sig_dirs:
            raise FileNotFoundError(f"No signature directory inside {plan_parent}")
        latest_dir = sig_dirs[-1]
        for fr in range(f_start, f_end + 1):
            src = latest_dir / f"f_{fr:04d}.png"
            if not verified_frame(src):
                raise RuntimeError(f"Unverified or missing frame {fr} in plan {pid}: {src}")
            dst = seq_dir / f"f_{fr:04d}.png"
            if not dst.is_file() or dst.stat().st_size != src.stat().st_size:
                shutil.copy2(src, dst)
            frame_sources[fr] = str(src.relative_to(ROOT))

    if len(frame_sources) != total_frames:
        raise RuntimeError(f"Expected {total_frames} verified frames, found {len(frame_sources)}")
    print(f"[FRAMES VERIFIED] All {total_frames} frames verified with SHA-256.", flush=True)

    ffmpeg_bin, _ = resolve_ffmpeg_binaries()

    # 2. Encode silent 1080x1920 H.264 master video
    silent_1080 = seq_dir / "EP001_V2_SILENT_1080x1920.mp4"
    subprocess.run(
        [
            ffmpeg_bin,
            "-y",
            "-v",
            "error",
            "-framerate",
            str(fps),
            "-start_number",
            "1",
            "-i",
            str(seq_dir / "f_%04d.png"),
            "-frames:v",
            str(total_frames),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(silent_1080),
        ],
        check=True,
    )

    # 3. Encode silent 1080x1920 H.264 video with burned-in ASS subtitles
    silent_1080_sub = seq_dir / "EP001_V2_SILENT_1080x1920_COM_LEGENDAS.mp4"
    ass_rel = "episodios/EP001_dinheiro/legendas/EP001_LEGENDAS.ass"
    subprocess.run(
        [
            ffmpeg_bin,
            "-y",
            "-v",
            "error",
            "-framerate",
            str(fps),
            "-start_number",
            "1",
            "-i",
            str(seq_dir / "f_%04d.png"),
            "-frames:v",
            str(total_frames),
            "-vf",
            f"ass={ass_rel}",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(silent_1080_sub),
        ],
        check=True,
    )

    # 4. Encode silent 360x640 H.264 low-res preview video
    silent_360 = seq_dir / "EP001_V2_SILENT_360x640.mp4"
    subprocess.run(
        [
            ffmpeg_bin,
            "-y",
            "-v",
            "error",
            "-i",
            str(silent_1080),
            "-vf",
            "scale=360:640:flags=lanczos",
            "-frames:v",
            str(total_frames),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(silent_360),
        ],
        check=True,
    )

    # 5. Build phrase list across all 8 segments for per-phrase RMS verification in audio_finalizer
    phrases = []
    for seg in timing_ep["segmentos"]:
        for idx, fr_obj in enumerate(seg["frases"], 1):
            phrases.append(
                {
                    "id": f"{seg['id']}_F{idx}",
                    "text": fr_obj["texto"],
                    "start_sec": float(fr_obj["inicio_s"]),
                    "end_sec": float(fr_obj["fim_s"]),
                }
            )
    timing_verify = {"phrases": phrases}
    wav_full = ROOT / timing_ep["narracao_completa"]

    entregas_dir = ROOT / "episodios/EP001_dinheiro/ENTREGAS"
    out_sem_leg = entregas_dir / "EP001_COMPLETO_V2_SEM_LEGENDAS.mp4"
    out_com_leg = entregas_dir / "EP001_COMPLETO_V2_COM_LEGENDAS.mp4"
    out_previa = entregas_dir / "EP001_PREVIA_V2.mp4"

    rep_sem_leg = finalize_mp4_with_narration(
        video_mp4_path=silent_1080,
        wav_path=wav_full,
        output_mp4_path=out_sem_leg,
        expected_duration_sec=expected_dur,
        timing_data=timing_verify,
    )
    rep_com_leg = finalize_mp4_with_narration(
        video_mp4_path=silent_1080_sub,
        wav_path=wav_full,
        output_mp4_path=out_com_leg,
        expected_duration_sec=expected_dur,
        timing_data=timing_verify,
    )
    rep_previa = finalize_mp4_with_narration(
        video_mp4_path=silent_360,
        wav_path=wav_full,
        output_mp4_path=out_previa,
        expected_duration_sec=expected_dur,
        timing_data=timing_verify,
    )

    # 6. Full decode checks on all 3 deliverables
    decodes = [
        decode_check(ffmpeg_bin, out_com_leg),
        decode_check(ffmpeg_bin, out_sem_leg),
        decode_check(ffmpeg_bin, out_previa),
    ]

    validation_summary = {
        "episode": "EP001_dinheiro",
        "version": "EP001_V2",
        "status": "PASSED",
        "total_frames": total_frames,
        "fps": fps,
        "duration_video_sec": expected_dur,
        "duration_narration_sec": timing_ep["duracao_narracao_s"],
        "deliverables": {
            "com_legendas": str(out_com_leg.relative_to(ROOT)),
            "sem_legendas": str(out_sem_leg.relative_to(ROOT)),
            "previa_lowres": str(out_previa.relative_to(ROOT)),
            "blend_editavel": spec["blend"],
        },
        "full_decode_checks": decodes,
        "audio_verification": {
            "EP001_COMPLETO_V2_COM_LEGENDAS.mp4": rep_com_leg,
            "EP001_COMPLETO_V2_SEM_LEGENDAS.mp4": rep_sem_leg,
            "EP001_PREVIA_V2.mp4": rep_previa,
        },
        "elapsed_seconds": round(time.perf_counter() - t0, 2),
    }

    report_path = ROOT / "episodios/EP001_dinheiro/TESTES/EP001_V2_VALIDACAO.json"
    report_path.write_text(json.dumps(validation_summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"FINALIZE_EP001_V2_OK {report_path} ({validation_summary['elapsed_seconds']}s)", flush=True)


if __name__ == "__main__":
    main()

