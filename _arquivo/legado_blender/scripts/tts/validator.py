"""Validação técnica de arquivos de áudio WAV gerados pelo módulo TTS."""

from __future__ import annotations

import array
import math
import wave
from pathlib import Path
from typing import Dict, Union


def validate_wav_file(
    wav_path: Union[str, Path],
    silence_threshold_dbfs: float = -45.0,
    max_allowed_silence_ratio: float = 0.65,
) -> Dict[str, object]:
    """Valida cabeçalho RIFF/WAVE, formato, duração real, amplitude e ausência de silêncio excessivo."""
    path = Path(wav_path)
    if not path.is_file():
        return {
            "exists": False,
            "valid": False,
            "error": f"Arquivo não encontrado: {path}",
        }

    file_size = path.stat().st_size
    if file_size < 44:
        return {
            "exists": True,
            "file_size_bytes": file_size,
            "valid": False,
            "error": "Arquivo menor que um cabeçalho WAV mínimo (44 bytes).",
        }

    with path.open("rb") as f:
        header = f.read(12)

    has_riff_header = len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WAVE"
    if not has_riff_header:
        return {
            "exists": True,
            "file_size_bytes": file_size,
            "has_riff_wave_header": False,
            "valid": False,
            "error": "Cabeçalho RIFF/WAVE inválido.",
        }

    try:
        with wave.open(str(path), "rb") as wf:
            channels = wf.getnchannels()
            sample_width_bytes = wf.getsampwidth()
            sample_rate_hz = wf.getframerate()
            num_frames = wf.getnframes()
            compression_type = wf.getcomptype()
            raw_frames = wf.readframes(num_frames)
    except wave.Error as exc:
        return {
            "exists": True,
            "file_size_bytes": file_size,
            "has_riff_wave_header": True,
            "valid": False,
            "error": f"Erro ao abrir WAV: {exc}",
        }

    duration_seconds = (num_frames / float(sample_rate_hz)) if sample_rate_hz > 0 else 0.0

    # Análise de sinal PCM de 16 bits (padrão Gemini TTS)
    peak_normalized = 0.0
    rms_normalized = 0.0
    peak_dbfs = -120.0
    rms_dbfs = -120.0
    leading_silence_sec = 0.0
    trailing_silence_sec = 0.0
    silence_ratio = 1.0

    if sample_width_bytes == 2 and len(raw_frames) >= 2:
        samples = array.array("h")
        samples.frombytes(raw_frames[: len(raw_frames) - (len(raw_frames) % 2)])
        total_samples = len(samples)

        if total_samples > 0:
            max_abs = max(abs(s) for s in samples)
            sum_sq = sum(float(s) * float(s) for s in samples)
            peak_normalized = max_abs / 32768.0
            rms_normalized = math.sqrt(sum_sq / total_samples) / 32768.0

            peak_dbfs = 20.0 * math.log10(peak_normalized) if peak_normalized > 1e-9 else -120.0
            rms_dbfs = 20.0 * math.log10(rms_normalized) if rms_normalized > 1e-9 else -120.0

            # Análise em janelas de 20 ms para medir silêncio inicial, final e proporção total
            window_frames = max(1, int(sample_rate_hz * 0.02))
            window_samples = window_frames * channels
            threshold_linear = (10.0 ** (silence_threshold_dbfs / 20.0)) * 32768.0

            window_is_silent = []
            for idx in range(0, total_samples, window_samples):
                chunk = samples[idx : idx + window_samples]
                if not chunk:
                    continue
                chunk_rms = math.sqrt(sum(float(x) * float(x) for x in chunk) / len(chunk))
                window_is_silent.append(chunk_rms < threshold_linear)

            if window_is_silent:
                total_windows = len(window_is_silent)
                silent_windows = sum(1 for flag in window_is_silent if flag)
                silence_ratio = silent_windows / float(total_windows)

                lead_count = 0
                for flag in window_is_silent:
                    if flag:
                        lead_count += 1
                    else:
                        break

                trail_count = 0
                for flag in reversed(window_is_silent):
                    if flag:
                        trail_count += 1
                    else:
                        break

                leading_silence_sec = round(lead_count * 0.02, 3)
                trailing_silence_sec = round(trail_count * 0.02, 3)

    non_empty_audio = duration_seconds > 0.2 and peak_normalized > 0.01 and rms_normalized > 0.001
    excessive_silence = silence_ratio > max_allowed_silence_ratio

    valid = (
        has_riff_header
        and compression_type == "NONE"
        and channels >= 1
        and sample_rate_hz > 0
        and non_empty_audio
        and not excessive_silence
    )

    return {
        "exists": True,
        "valid": valid,
        "file_size_bytes": file_size,
        "has_riff_wave_header": has_riff_header,
        "format": "WAV (PCM)",
        "compression_type": compression_type,
        "channels": channels,
        "sample_width_bits": sample_width_bytes * 8,
        "sample_rate_hz": sample_rate_hz,
        "num_frames": num_frames,
        "duration_seconds": round(duration_seconds, 3),
        "peak_normalized": round(peak_normalized, 4),
        "rms_normalized": round(rms_normalized, 4),
        "peak_dbfs": round(peak_dbfs, 2),
        "rms_dbfs": round(rms_dbfs, 2),
        "non_empty_audio": non_empty_audio,
        "silence_ratio": round(silence_ratio, 3),
        "leading_silence_seconds": leading_silence_sec,
        "trailing_silence_seconds": trailing_silence_sec,
        "excessive_silence": excessive_silence,
    }

