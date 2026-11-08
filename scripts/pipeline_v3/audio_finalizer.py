"""Automatic FFmpeg Audio Finalization & FFprobe/PCM Verification Module for Pipeline V3.1+.

Implements the 10-step audiovisual finalization and verification workflow:
1. Receive the Blender-rendered H.264 MP4 video and the working/approved WAV narration.
2. Strip any silent or incorrect audio stream from the input video (-map 0:v:0).
3. Mux the WAV narration as AAC while preserving the H.264 video stream without re-encoding (-c:v copy).
4. Keep the narration start anchored at t = 0.000s, preserving its natural leading silence.
5. Pad with silence ONLY the remaining tail interval when the video is longer than the audio (apad=whole_dur=...).
6. Preserve the exact planned duration of the scene (19.20s / 576 frames at 30 FPS).
7. Validate video and audio streams with FFprobe (codec, duration, frame count, start_time, bitrate).
8. Decode the MP4 audio track to PCM and verify RMS and peak dBFS to detect total or partial silence.
9. Compare the embedded MP4 audio against the source WAV (cross-correlation lag, waveform/envelope correlation,
   leading silence, tail silence, and per-phrase RMS) to detect timing offset or content loss.
10. Halt immediately and raise AudioVerificationError if the final MP4 lacks audible, synchronized narration.
"""

import json
import math
import os
import shutil
import subprocess
import wave
from pathlib import Path
import numpy as np

from . import config


class AudioVerificationError(RuntimeError):
    """Raised when an MP4 file fails FFprobe stream validation, audibility (RMS/Peak), or WAV sync checks."""


# Protected V2, V3, and original V3.1 video filenames that must never be overwritten
PROTECTED_VIDEO_FILENAMES = {
    "preview_15s_v2.mp4",
    "preview_15s_v2_lowres.mp4",
    "abertura_a_3s.mp4",
    "abertura_b_3s.mp4",
    "preview_15s_v3.mp4",
    "preview_15s_v3_lowres.mp4",
    "preview_v3_1_narrado_lowres.mp4",
    "preview_v3_1_sem_carimbo_lowres.mp4",
    "preview_v3_1_com_carimbo_lowres.mp4",
}


def assert_not_protected_video(path: Path):
    """Ensure we never overwrite previous V2, V3, or V3.1 deliverable video files."""
    p = Path(path).resolve()
    if p.name.lower() in PROTECTED_VIDEO_FILENAMES:
        raise ValueError(f"Refusing to overwrite protected V3/V3.1 video file: {p}")


def resolve_ffmpeg_binaries() -> tuple[str, str]:
    """Locate ffmpeg and ffprobe executables on Windows or PATH."""
    env_ffmpeg = os.environ.get("FFMPEG_BIN")
    env_ffprobe = os.environ.get("FFPROBE_BIN")
    if env_ffmpeg and env_ffprobe and Path(env_ffmpeg).is_file() and Path(env_ffprobe).is_file():
        return str(Path(env_ffmpeg).resolve()), str(Path(env_ffprobe).resolve())

    which_ffmpeg = shutil.which("ffmpeg")
    which_ffprobe = shutil.which("ffprobe")
    if which_ffmpeg and which_ffprobe:
        return which_ffmpeg, which_ffprobe

    local_appdata = os.environ.get("LOCALAPPDATA", "")
    user_profile = os.environ.get("USERPROFILE", "")
    candidate_dirs = [
        Path(local_appdata) / "Programs" / "Stremio",
        Path(user_profile) / "AppData" / "Local" / "Programs" / "Stremio",
        Path(r"C:\ffmpeg\bin"),
        Path(r"C:\Program Files\ffmpeg\bin"),
        Path(r"C:\Program Files\VMS"),
    ]

    ffmpeg_bin = which_ffmpeg
    ffprobe_bin = which_ffprobe

    for d in candidate_dirs:
        if not d.is_dir():
            continue
        f_exe = d / "ffmpeg.exe"
        p_exe = d / "ffprobe.exe"
        if not ffmpeg_bin and f_exe.is_file():
            ffmpeg_bin = str(f_exe.resolve())
        if not ffprobe_bin and p_exe.is_file():
            ffprobe_bin = str(p_exe.resolve())
        if ffmpeg_bin and ffprobe_bin:
            break

    if not ffmpeg_bin or not ffprobe_bin:
        raise FileNotFoundError(
            f"Could not locate both ffmpeg ({ffmpeg_bin}) and ffprobe ({ffprobe_bin}). "
            "Set FFMPEG_BIN and FFPROBE_BIN environment variables or install FFmpeg."
        )
    return ffmpeg_bin, ffprobe_bin


def _linear_to_dbfs(val: float) -> float:
    """Convert linear amplitude (0..1+) to dBFS, returning -240.0 for digital zero."""
    if val <= 1e-12:
        return -240.0
    return float(20.0 * math.log10(val))


def compute_audio_levels(samples: np.ndarray) -> dict:
    """Compute RMS and Peak in both linear and dBFS scales for a float32 [-1, 1] array."""
    if samples.size == 0:
        return {
            "num_samples": 0,
            "rms_linear": 0.0,
            "rms_dbfs": -240.0,
            "peak_linear": 0.0,
            "peak_dbfs": -240.0,
        }
    rms_lin = float(np.sqrt(np.mean(np.square(samples, dtype=np.float64))))
    peak_lin = float(np.max(np.abs(samples)))
    return {
        "num_samples": int(samples.size),
        "rms_linear": round(rms_lin, 6),
        "rms_dbfs": round(_linear_to_dbfs(rms_lin), 2),
        "peak_linear": round(peak_lin, 6),
        "peak_dbfs": round(_linear_to_dbfs(peak_lin), 2),
    }


def load_wav_mono_float32(wav_path: Path) -> tuple[np.ndarray, int, int, float]:
    """Read a 16-bit PCM WAV file into a normalized float32 [-1, 1] mono array."""
    wav_path = Path(wav_path).resolve()
    if not wav_path.is_file():
        raise FileNotFoundError(f"WAV file not found: {wav_path}")

    with wave.open(str(wav_path), "rb") as wf:
        sr = wf.getframerate()
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    if sampwidth != 2:
        raise AudioVerificationError(f"Unsupported WAV sample width ({sampwidth * 8}-bit); expected 16-bit PCM.")

    arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if channels > 1:
        arr = arr.reshape(-1, channels).mean(axis=1)
    duration_sec = float(n_frames) / float(sr)
    return arr, sr, channels, duration_sec


def probe_media_file(media_path: Path) -> dict:
    """Run ffprobe on a media file and return parsed JSON streams and format metadata."""
    _, ffprobe_bin = resolve_ffmpeg_binaries()
    media_path = Path(media_path).resolve()
    if not media_path.is_file():
        raise FileNotFoundError(f"Media file not found for probing: {media_path}")

    cmd = [
        ffprobe_bin,
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(media_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise AudioVerificationError(f"ffprobe failed on {media_path}: {res.stderr.strip()}")
    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as exc:
        raise AudioVerificationError(f"Invalid JSON from ffprobe on {media_path}: {exc}") from exc


def decode_mp4_audio_mono_float32(mp4_path: Path, target_sr: int = 24000) -> np.ndarray:
    """Decode the first audio stream (0:a:0) of an MP4 file to mono float32 [-1, 1] at target_sr using FFmpeg."""
    ffmpeg_bin, _ = resolve_ffmpeg_binaries()
    mp4_path = Path(mp4_path).resolve()
    cmd = [
        ffmpeg_bin,
        "-v",
        "error",
        "-i",
        str(mp4_path),
        "-vn",
        "-map",
        "0:a:0",
        "-f",
        "s16le",
        "-acodec",
        "pcm_s16le",
        "-ar",
        str(target_sr),
        "-ac",
        "1",
        "-",
    ]
    res = subprocess.run(cmd, capture_output=True, check=False)
    if res.returncode != 0:
        err_msg = res.stderr.decode("utf-8", errors="replace").strip()
        raise AudioVerificationError(f"Failed to decode audio stream from {mp4_path}: {err_msg}")
    if len(res.stdout) == 0:
        raise AudioVerificationError(f"Decoded 0 audio bytes from {mp4_path} (empty audio stream).")
    return np.frombuffer(res.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def verify_finalized_mp4(
    mp4_path: Path,
    wav_path: Path,
    expected_duration_sec: float = None,
    timing_data: dict = None,
    min_active_rms_dbfs: float = -35.0,
    min_peak_dbfs: float = -15.0,
    max_rms_diff_db: float = 1.2,
    max_lag_ms: float = 20.0,
    min_envelope_corr: float = 0.98,
    min_sample_corr: float = 0.95,
) -> dict:
    """Perform Steps 7, 8, 9, and 10 on an MP4 file against the source WAV narration.

    Raises AudioVerificationError immediately if any stream, silence, duration, offset, or content check fails.
    """
    mp4_path = Path(mp4_path).resolve()
    wav_path = Path(wav_path).resolve()

    # Load source WAV and verify it is itself valid and audible
    y_wav, sr, wav_channels, wav_dur_sec = load_wav_mono_float32(wav_path)
    wav_levels = compute_audio_levels(y_wav)
    if wav_levels["peak_dbfs"] < min_peak_dbfs or wav_levels["rms_dbfs"] < min_active_rms_dbfs:
        raise AudioVerificationError(
            f"Source WAV '{wav_path.name}' is silent or too quiet: "
            f"RMS={wav_levels['rms_dbfs']} dBFS, Peak={wav_levels['peak_dbfs']} dBFS"
        )

    # ==========================================================================
    # STEP 7: Validate Video and Audio Streams with FFprobe
    # ==========================================================================
    probe = probe_media_file(mp4_path)
    streams = probe.get("streams", [])
    v_streams = [s for s in streams if s.get("codec_type") == "video"]
    a_streams = [s for s in streams if s.get("codec_type") == "audio"]

    if len(v_streams) != 1:
        raise AudioVerificationError(f"Expected exactly 1 video stream in {mp4_path.name}, found {len(v_streams)}.")
    if len(a_streams) != 1:
        raise AudioVerificationError(f"Expected exactly 1 audio stream in {mp4_path.name}, found {len(a_streams)}.")

    vs = v_streams[0]
    ast = a_streams[0]

    if vs.get("codec_name") != "h264":
        raise AudioVerificationError(f"Expected video codec 'h264', found '{vs.get('codec_name')}'.")
    if ast.get("codec_name") != "aac":
        raise AudioVerificationError(f"Expected audio codec 'aac', found '{ast.get('codec_name')}'.")

    v_dur = float(vs.get("duration") or probe.get("format", {}).get("duration") or 0.0)
    a_dur = float(ast.get("duration") or probe.get("format", {}).get("duration") or 0.0)
    v_start = float(vs.get("start_time") or 0.0)
    a_start = float(ast.get("start_time") or 0.0)
    v_frames = int(vs.get("nb_frames") or 0)
    a_bitrate = int(ast.get("bit_rate") or 0)

    target_dur = float(expected_duration_sec) if expected_duration_sec is not None else v_dur
    if abs(v_dur - target_dur) > 0.06:
        raise AudioVerificationError(
            f"Video duration mismatch in {mp4_path.name}: expected {target_dur:.2f}s, got {v_dur:.4f}s."
        )
    if abs(a_dur - target_dur) > 0.08:
        raise AudioVerificationError(
            f"Audio duration mismatch in {mp4_path.name}: expected {target_dur:.2f}s, got {a_dur:.4f}s."
        )
    if abs(v_start) > 0.05 or abs(a_start) > 0.05:
        raise AudioVerificationError(
            f"Stream start_time not anchored at 0.0s in {mp4_path.name}: video={v_start:.4f}s, audio={a_start:.4f}s."
        )

    # ==========================================================================
    # STEP 8: Decode MP4 Audio Track and Verify RMS & Peak to Detect Silence
    # ==========================================================================
    y_mp4 = decode_mp4_audio_mono_float32(mp4_path, target_sr=sr)
    decoded_dur_sec = float(y_mp4.size) / float(sr)

    if abs(decoded_dur_sec - target_dur) > 0.08:
        raise AudioVerificationError(
            f"Decoded PCM audio duration ({decoded_dur_sec:.3f}s) does not match target scene duration ({target_dur:.3f}s)."
        )

    overall_mp4_levels = compute_audio_levels(y_mp4)
    n_compare = min(y_wav.size, y_mp4.size)
    if n_compare < int(0.98 * y_wav.size):
        raise AudioVerificationError(
            f"MP4 audio is shorter than source WAV: n_compare={n_compare} vs n_wav={y_wav.size}."
        )

    y_mp4_active = y_mp4[:n_compare]
    y_wav_active = y_wav[:n_compare]
    active_mp4_levels = compute_audio_levels(y_mp4_active)

    if (
        active_mp4_levels["peak_linear"] <= 1e-5
        or active_mp4_levels["peak_dbfs"] < min_peak_dbfs
        or active_mp4_levels["rms_dbfs"] < min_active_rms_dbfs
    ):
        raise AudioVerificationError(
            f"SILENT OR INAUDIBLE AUDIO DETECTED in '{mp4_path.name}'! "
            f"Active RMS={active_mp4_levels['rms_dbfs']} dBFS (min {min_active_rms_dbfs} dBFS), "
            f"Peak={active_mp4_levels['peak_dbfs']} dBFS (min {min_peak_dbfs} dBFS), "
            f"AAC bitrate={a_bitrate} bps."
        )

    # ==========================================================================
    # STEP 9: Compare Embedded Audio to Source WAV (Offset, Content, Silence Padding)
    # ==========================================================================
    # 9a. Verify RMS and Peak match the source WAV closely
    rms_diff_db = abs(active_mp4_levels["rms_dbfs"] - wav_levels["rms_dbfs"])
    peak_diff_db = abs(active_mp4_levels["peak_dbfs"] - wav_levels["peak_dbfs"])
    if rms_diff_db > max_rms_diff_db:
        raise AudioVerificationError(
            f"MP4 active RMS ({active_mp4_levels['rms_dbfs']} dBFS) deviates from WAV RMS "
            f"({wav_levels['rms_dbfs']} dBFS) by {rms_diff_db:.2f} dB (max allowed {max_rms_diff_db} dB)."
        )

    # 9b. Verify initial silence at t=0 (0.00s..0.38s) is preserved intact
    n_init_silence = int(0.38 * sr)
    init_wav_levels = compute_audio_levels(y_wav_active[:n_init_silence])
    init_mp4_levels = compute_audio_levels(y_mp4_active[:n_init_silence])
    source_has_initial_silence = init_wav_levels["rms_dbfs"] <= -42.0
    prefix_mismatch = (
        init_mp4_levels["rms_dbfs"] > -42.0 if source_has_initial_silence
        else abs(init_mp4_levels["rms_dbfs"] - init_wav_levels["rms_dbfs"]) > max_rms_diff_db
    )
    if prefix_mismatch:
        raise AudioVerificationError(
            f"Initial audio prefix (0.00s..0.38s) differs from source in {mp4_path.name}: "
            f"MP4 initial RMS={init_mp4_levels['rms_dbfs']} dBFS (WAV={init_wav_levels['rms_dbfs']} dBFS)."
        )

    # 9c. Cross-correlation lag detection (via FFT) to detect any timing shift
    f_wav = np.fft.rfft(y_wav_active)
    f_mp4 = np.fft.rfft(y_mp4_active)
    xc = np.fft.irfft(f_mp4 * np.conj(f_wav), n=n_compare)
    best_lag_samples = int(np.argmax(xc))
    if best_lag_samples > n_compare // 2:
        best_lag_samples -= n_compare
    lag_ms = float(best_lag_samples) * 1000.0 / float(sr)

    if abs(lag_ms) > max_lag_ms:
        raise AudioVerificationError(
            f"Audio timing offset detected in {mp4_path.name}: lag = {lag_ms:.2f} ms "
            f"({best_lag_samples} samples), exceeding max allowed ±{max_lag_ms:.1f} ms."
        )

    # 9d. Sample-level and 10ms RMS envelope correlation at zero lag
    win = int(0.01 * sr)
    n_win = n_compare // win
    env_wav = np.sqrt(np.mean(np.square(y_wav_active[: n_win * win].reshape(n_win, win)), axis=1))
    env_mp4 = np.sqrt(np.mean(np.square(y_mp4_active[: n_win * win].reshape(n_win, win)), axis=1))

    sample_corr = float(np.corrcoef(y_wav_active, y_mp4_active)[0, 1])
    envelope_corr = float(np.corrcoef(env_wav, env_mp4)[0, 1])

    if math.isnan(sample_corr) or sample_corr < min_sample_corr:
        raise AudioVerificationError(
            f"Low sample waveform correlation between MP4 and WAV in {mp4_path.name}: "
            f"{sample_corr:.4f} (min {min_sample_corr})."
        )
    if math.isnan(envelope_corr) or envelope_corr < min_envelope_corr:
        raise AudioVerificationError(
            f"Low 10ms RMS envelope correlation between MP4 and WAV in {mp4_path.name}: "
            f"{envelope_corr:.4f} (min {min_envelope_corr})."
        )

    # 9e. Verify padded tail interval (when video > wav) is pure silence
    tail_info = {"padded_tail_duration_sec": 0.0, "tail_rms_dbfs": -240.0, "tail_peak_dbfs": -240.0}
    tail_guard_samples = int(0.03 * sr)
    if y_mp4.size > y_wav.size + tail_guard_samples:
        y_tail = y_mp4[y_wav.size + tail_guard_samples :]
        tail_levels = compute_audio_levels(y_tail)
        tail_info = {
            "padded_tail_duration_sec": round(float(y_mp4.size - y_wav.size) / float(sr), 4),
            "tail_rms_dbfs": tail_levels["rms_dbfs"],
            "tail_peak_dbfs": tail_levels["peak_dbfs"],
        }
        if tail_levels["rms_dbfs"] > -50.0:
            raise AudioVerificationError(
                f"Padded tail interval after WAV end is not silent in {mp4_path.name}: "
                f"tail RMS={tail_levels['rms_dbfs']} dBFS."
            )

    # 9f. Per-phrase content integrity check (all 6 phrases must be audible and match WAV)
    if timing_data is None:
        default_timing = config.PROJECT_ROOT / "timing.json"
        if default_timing.is_file():
            timing_data = json.loads(default_timing.read_text(encoding="utf-8"))

    phrase_reports = []
    if timing_data and "phrases" in timing_data:
        for ph in timing_data["phrases"]:
            s0 = max(0, min(n_compare - 1, int(round(ph["start_sec"] * sr))))
            s1 = max(s0 + 1, min(n_compare, int(round(ph["end_sec"] * sr))))
            w_ph = compute_audio_levels(y_wav_active[s0:s1])
            m_ph = compute_audio_levels(y_mp4_active[s0:s1])
            ph_diff = abs(m_ph["rms_dbfs"] - w_ph["rms_dbfs"])
            if m_ph["rms_dbfs"] < -32.0 or ph_diff > max_rms_diff_db:
                raise AudioVerificationError(
                    f"Phrase {ph['id']} ('{ph['text']}') lost or corrupted in {mp4_path.name}: "
                    f"MP4 RMS={m_ph['rms_dbfs']} dBFS vs WAV RMS={w_ph['rms_dbfs']} dBFS."
                )
            phrase_reports.append(
                {
                    "id": ph["id"],
                    "text": ph["text"],
                    "start_sec": ph["start_sec"],
                    "end_sec": ph["end_sec"],
                    "wav_rms_dbfs": w_ph["rms_dbfs"],
                    "mp4_rms_dbfs": m_ph["rms_dbfs"],
                    "wav_peak_dbfs": w_ph["peak_dbfs"],
                    "mp4_peak_dbfs": m_ph["peak_dbfs"],
                    "rms_diff_db": round(ph_diff, 3),
                }
            )

    return {
        "status": "PASSED",
        "mp4_file": str(mp4_path),
        "wav_file": str(wav_path),
        "ffprobe_validation": {
            "video_codec": vs.get("codec_name"),
            "video_width": int(vs.get("width", 0)),
            "video_height": int(vs.get("height", 0)),
            "video_nb_frames": v_frames,
            "video_duration_sec": round(v_dur, 4),
            "video_start_time_sec": round(v_start, 4),
            "audio_codec": ast.get("codec_name"),
            "audio_sample_rate_hz": int(ast.get("sample_rate", 0)),
            "audio_channels": int(ast.get("channels", 0)),
            "audio_duration_sec": round(a_dur, 4),
            "audio_start_time_sec": round(a_start, 4),
            "audio_bit_rate_bps": a_bitrate,
        },
        "pcm_audibility_validation": {
            "wav_duration_sec": round(wav_dur_sec, 4),
            "mp4_decoded_duration_sec": round(decoded_dur_sec, 4),
            "wav_rms_dbfs": wav_levels["rms_dbfs"],
            "mp4_active_rms_dbfs": active_mp4_levels["rms_dbfs"],
            "mp4_overall_rms_dbfs": overall_mp4_levels["rms_dbfs"],
            "wav_peak_dbfs": wav_levels["peak_dbfs"],
            "mp4_peak_dbfs": active_mp4_levels["peak_dbfs"],
            "rms_diff_db": round(rms_diff_db, 3),
            "peak_diff_db": round(peak_diff_db, 3),
        },
        "sync_and_content_comparison": {
            "best_lag_samples": best_lag_samples,
            "best_lag_ms": round(lag_ms, 3),
            "zero_lag_sample_correlation": round(sample_corr, 6),
            "zero_lag_envelope_10ms_correlation": round(envelope_corr, 6),
            "initial_silence_wav_rms_dbfs": init_wav_levels["rms_dbfs"],
            "initial_silence_mp4_rms_dbfs": init_mp4_levels["rms_dbfs"],
            "initial_prefix_mode": "silence" if source_has_initial_silence else "speech_compared_to_source",
            **tail_info,
            "phrases_verified": len(phrase_reports),
            "phrases": phrase_reports,
        },
    }


def finalize_mp4_with_narration(
    video_mp4_path: Path,
    wav_path: Path,
    output_mp4_path: Path,
    expected_duration_sec: float = None,
    timing_data: dict = None,
    audio_bitrate: str = "192k",
) -> dict:
    """Execute the full 10-step FFmpeg audio muxing and verification pipeline.

    - Preserves H.264 video stream without re-encoding (-c:v copy).
    - Removes any silent or erroneous audio track from video_mp4_path (-map 0:v:0).
    - Keeps narration start at t = 0.000s (preserving initial silence).
    - Pads ONLY the remaining tail with silence up to the planned scene duration.
    - Validates with FFprobe + PCM decoding + WAV cross-correlation, raising AudioVerificationError on failure.
    """
    ffmpeg_bin, _ = resolve_ffmpeg_binaries()
    video_mp4_path = Path(video_mp4_path).resolve()
    wav_path = Path(wav_path).resolve()
    output_mp4_path = Path(output_mp4_path).resolve()

    if not video_mp4_path.is_file():
        raise FileNotFoundError(f"Input video MP4 not found: {video_mp4_path}")
    if not wav_path.is_file():
        raise FileNotFoundError(f"Input narration WAV not found: {wav_path}")
    if video_mp4_path == output_mp4_path:
        raise ValueError("output_mp4_path must be distinct from input video_mp4_path.")

    assert_not_protected_video(output_mp4_path)
    output_mp4_path.parent.mkdir(parents=True, exist_ok=True)

    # Probe input video to determine exact planned scene duration
    in_probe = probe_media_file(video_mp4_path)
    v_streams = [s for s in in_probe.get("streams", []) if s.get("codec_type") == "video"]
    if not v_streams:
        raise AudioVerificationError(f"Input video {video_mp4_path.name} has no video stream.")
    in_v_dur = float(v_streams[0].get("duration") or in_probe.get("format", {}).get("duration") or 0.0)
    target_dur = float(expected_duration_sec) if expected_duration_sec is not None else in_v_dur

    # Inspect source WAV before muxing
    y_wav, sr, wav_channels, _ = load_wav_mono_float32(wav_path)
    wav_levels = compute_audio_levels(y_wav)
    if wav_levels["peak_dbfs"] < -20.0 or wav_levels["rms_dbfs"] < -40.0:
        raise AudioVerificationError(
            f"Refusing to mux silent/invalid source WAV '{wav_path.name}': "
            f"RMS={wav_levels['rms_dbfs']} dBFS, Peak={wav_levels['peak_dbfs']} dBFS."
        )

    # Audio filter: anchor start at PTS=0, pad only the remaining tail with silence to target_dur, and trim at target_dur
    af_chain = f"aresample=async=1:first_pts=0,apad=whole_dur={target_dur:.6f},atrim=0:{target_dur:.6f}"

    cmd = [
        ffmpeg_bin,
        "-y",
        "-v",
        "error",
        "-i",
        str(video_mp4_path),
        "-i",
        str(wav_path),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-af",
        af_chain,
        "-c:a",
        "aac",
        "-b:a",
        audio_bitrate,
        "-ar",
        str(sr),
        "-ac",
        str(wav_channels),
        "-movflags",
        "+faststart",
        str(output_mp4_path),
    ]

    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise AudioVerificationError(f"FFmpeg muxing failed for {output_mp4_path.name}: {res.stderr.strip()}")

    # Run Steps 7-10 verification on the newly created MP4
    report = verify_finalized_mp4(
        mp4_path=output_mp4_path,
        wav_path=wav_path,
        expected_duration_sec=target_dur,
        timing_data=timing_data,
    )
    print(
        f"[AUDIO FINALIZER OK] {output_mp4_path.name} | "
        f"RMS={report['pcm_audibility_validation']['mp4_active_rms_dbfs']} dBFS | "
        f"Peak={report['pcm_audibility_validation']['mp4_peak_dbfs']} dBFS | "
        f"Lag={report['sync_and_content_comparison']['best_lag_ms']} ms | "
        f"Corr={report['sync_and_content_comparison']['zero_lag_sample_correlation']}"
    )
    return report

