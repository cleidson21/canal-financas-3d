"""Automated Verification Suite for MISSÃO V3.1 & V3.1.1 — Montagem Narrada + Finalização FFmpeg/FFprobe.

Includes mandatory negative tests that fail when an MP4 has an audio stream present but silent,
shifted, or truncated, and positive tests validating the finalized V3.1.1 MP4 deliverables.

Run inside Blender 5.2 LTS headless:
  blender -b --factory-startup -P testes/test_pipeline_v3_1.py
"""

import json
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path
import bpy

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from pipeline_v3 import audio_finalizer
from pipeline_v3.audio_finalizer import AudioVerificationError

EP001_DIR = PROJECT_ROOT / "arquivo" / "EP001" / "piloto"
VIDEOS_DIR = EP001_DIR / "videos"
WAV_PATH = PROJECT_ROOT / "audio" / "narracoes" / "EP001" / "testes" / "narracao_B_flash_lite_V1.wav"
TIMING_PATH = PROJECT_ROOT / "timing.json"
V3_BLEND = EP001_DIR / "cenas" / "cena_01_V3.blend"
V3_1_BLEND = EP001_DIR / "cenas" / "cena_01_V3_1.blend"
V3_1_CARIMBO_BLEND = EP001_DIR / "cenas" / "cena_01_V3_1_com_carimbo.blend"
CARIMBO_LIB_BLEND = PROJECT_ROOT / "objetos" / "carimbo_duvida.blend"


class TestPipelineV31(unittest.TestCase):
    def test_01_original_files_and_overwrite_protection(self):
        """Ensure original V3/V3.1 blends, WAV narration, and previous MP4s remain intact and protected."""
        self.assertTrue(V3_BLEND.is_file(), "Original cena_01_V3.blend must be preserved")
        self.assertTrue(V3_1_BLEND.is_file(), "Original cena_01_V3_1.blend must be preserved")
        self.assertTrue(V3_1_CARIMBO_BLEND.is_file(), "Original cena_01_V3_1_com_carimbo.blend must be preserved")
        self.assertTrue(WAV_PATH.is_file(), "Original working WAV must be preserved")

        with wave.open(str(WAV_PATH), "rb") as wf:
            self.assertEqual(wf.getframerate(), 24000)
            self.assertEqual(wf.getnchannels(), 1)
            self.assertEqual(wf.getnframes(), 449280)  # 18.72s exact

        meta_path = Path(str(WAV_PATH) + ".meta.json")
        self.assertTrue(meta_path.is_file())
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        self.assertFalse(meta.get("approved", True), "Working narration must NOT be marked emotionally approved")

        # Verify overwrite protection on previous V3 and V3.1 video files
        for protected_name in (
            "preview_15s_V3.mp4",
            "preview_15s_V3_lowres.mp4",
            "preview_V3_1_sem_carimbo_lowres.mp4",
            "preview_V3_1_com_carimbo_lowres.mp4",
            "preview_V3_1_narrado_lowres.mp4",
        ):
            protected_path = VIDEOS_DIR / protected_name
            self.assertTrue(protected_path.is_file(), f"Protected file must exist: {protected_path}")
            with self.assertRaises(ValueError):
                audio_finalizer.assert_not_protected_video(protected_path)

    def test_02_timing_json_phrases_and_silences(self):
        """Verify timing.json has 6 valid phrases and silence intervals derived from the 18.72s WAV."""
        self.assertTrue(TIMING_PATH.is_file(), "timing.json must exist at project root")
        data = json.loads(TIMING_PATH.read_text(encoding="utf-8"))
        self.assertFalse(data["audio_source"]["approved_by_human"])
        self.assertAlmostEqual(data["audio_source"]["audio_duration_sec"], 18.72, places=2)

        phrases = data["phrases"]
        self.assertEqual(len(phrases), 6, "Must have exactly 6 narration phrases")
        prev_end = 0.0
        for idx, ph in enumerate(phrases, start=1):
            self.assertEqual(ph["id"], idx)
            self.assertGreater(ph["start_sec"], prev_end)
            self.assertGreater(ph["end_sec"], ph["start_sec"])
            self.assertGreater(ph["end_frame"], ph["start_frame"])
            prev_end = ph["end_sec"]

    def test_03_scene_v3_1_synchronization_and_context_props(self):
        """Verify cena_01_V3_1.blend has 576 frames, No-Money badge, X, Milk sign, and Carimbo synced."""
        self.assertTrue(V3_1_BLEND.is_file(), "cena_01_V3_1.blend must exist")
        self.assertTrue(CARIMBO_LIB_BLEND.is_file(), "Standalone objetos/carimbo_duvida.blend must exist")

        bpy.ops.wm.open_mainfile(filepath=str(V3_1_BLEND))
        scene = bpy.context.scene
        self.assertEqual(scene.render.fps, 30)
        self.assertEqual(scene.frame_start, 1)
        self.assertEqual(scene.frame_end, 576)

        objs = bpy.data.objects
        no_money = objs.get("Selo_Sem_Dinheiro_Root")
        x_sign = objs.get("Placa_Recusa_X_Root")
        milk_sign = objs.get("Placa_Desejo_Leite_Root")
        carimbo = objs.get("Carimbo_Duvida_Root")
        self.assertIsNotNone(no_money)
        self.assertIsNotNone(x_sign)
        self.assertIsNotNone(milk_sign)
        self.assertIsNotNone(carimbo)

        # Phrase 2 (f155): No-Money badge visible, X and Milk hidden
        scene.frame_set(155)
        self.assertGreater(no_money.scale.x, 0.8)
        self.assertLess(x_sign.scale.x, 0.05)
        self.assertLess(milk_sign.scale.x, 0.05)

        # Phrase 4 (f392): Red X visible, Milk still hidden
        scene.frame_set(392)
        self.assertLess(no_money.scale.x, 0.05)
        self.assertGreater(x_sign.scale.x, 0.8)
        self.assertLess(milk_sign.scale.x, 0.05)

        # Phrase 5 (f451): Milk sign visible
        scene.frame_set(451)
        self.assertGreater(milk_sign.scale.x, 0.8)

        # Phrase 6 (f530): Carimbo hidden in base V3.1 scene
        scene.frame_set(530)
        self.assertLess(carimbo.scale.x, 0.05)

        # Open variant with Carimbo and verify Carimbo is visible at f530
        bpy.ops.wm.open_mainfile(filepath=str(V3_1_CARIMBO_BLEND))
        scene2 = bpy.context.scene
        scene2.frame_set(530)
        carimbo2 = bpy.data.objects.get("Carimbo_Duvida_Root")
        self.assertGreater(carimbo2.scale.x, 0.8)

    def test_04_verifier_fails_when_audio_stream_present_but_silent(self):
        """MANDATORY: Verify that an MP4 with a present-but-silent AAC track fails verification."""
        # 1. Verify that the un-muxed Blender V3.1 MP4 (which has a 19.20s silent AAC stream) is rejected
        silent_blender_mp4 = VIDEOS_DIR / "preview_V3_1_sem_carimbo_lowres.mp4"
        probe = audio_finalizer.probe_media_file(silent_blender_mp4)
        a_streams = [s for s in probe.get("streams", []) if s.get("codec_type") == "audio"]
        self.assertEqual(len(a_streams), 1, "Precondition: silent MP4 has 1 AAC audio stream present")

        with self.assertRaises(AudioVerificationError) as ctx:
            audio_finalizer.verify_finalized_mp4(
                mp4_path=silent_blender_mp4,
                wav_path=WAV_PATH,
                expected_duration_sec=19.20,
            )
        self.assertIn("SILENT OR INAUDIBLE AUDIO DETECTED", str(ctx.exception))

        # 2. Also test a synthetic MP4 with a newly generated 192k silent AAC stream (anullsrc)
        ffmpeg_bin, _ = audio_finalizer.resolve_ffmpeg_binaries()
        with tempfile.TemporaryDirectory() as tmpdir:
            synth_silent_mp4 = Path(tmpdir) / "synthetic_silent_aac.mp4"
            subprocess.run(
                [
                    ffmpeg_bin,
                    "-y",
                    "-v",
                    "error",
                    "-i",
                    str(silent_blender_mp4),
                    "-f",
                    "lavfi",
                    "-i",
                    "anullsrc=r=24000:cl=mono",
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:a:0",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-t",
                    "19.200000",
                    str(synth_silent_mp4),
                ],
                check=True,
            )
            with self.assertRaises(AudioVerificationError) as ctx2:
                audio_finalizer.verify_finalized_mp4(
                    mp4_path=synth_silent_mp4,
                    wav_path=WAV_PATH,
                    expected_duration_sec=19.20,
                )
            self.assertIn("SILENT OR INAUDIBLE AUDIO DETECTED", str(ctx2.exception))

    def test_05_verifier_fails_on_audio_offset_or_content_loss(self):
        """Verify that shifted/delayed audio (+250ms) or truncated audio (missing last phrase) fails."""
        ffmpeg_bin, _ = audio_finalizer.resolve_ffmpeg_binaries()
        in_video = VIDEOS_DIR / "preview_V3_1_sem_carimbo_lowres.mp4"

        with tempfile.TemporaryDirectory() as tmpdir:
            # A. Shifted audio (+250ms delay via adelay=250)
            shifted_mp4 = Path(tmpdir) / "shifted_audio.mp4"
            subprocess.run(
                [
                    ffmpeg_bin,
                    "-y",
                    "-v",
                    "error",
                    "-i",
                    str(in_video),
                    "-i",
                    str(WAV_PATH),
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:a:0",
                    "-c:v",
                    "copy",
                    "-af",
                    "adelay=250|250,apad=whole_dur=19.200000,atrim=0:19.200000",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-ar",
                    "24000",
                    "-ac",
                    "1",
                    str(shifted_mp4),
                ],
                check=True,
            )
            with self.assertRaises(AudioVerificationError) as ctx_shift:
                audio_finalizer.verify_finalized_mp4(
                    mp4_path=shifted_mp4,
                    wav_path=WAV_PATH,
                    expected_duration_sec=19.20,
                )
            self.assertIn("offset", str(ctx_shift.exception).lower())

            # B. Truncated audio (muted after 15.8s, cutting off Phrase 6 "Nico... aí complicou.")
            truncated_mp4 = Path(tmpdir) / "truncated_phrase6.mp4"
            subprocess.run(
                [
                    ffmpeg_bin,
                    "-y",
                    "-v",
                    "error",
                    "-i",
                    str(in_video),
                    "-i",
                    str(WAV_PATH),
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:a:0",
                    "-c:v",
                    "copy",
                    "-af",
                    "atrim=0:15.800000,apad=whole_dur=19.200000,atrim=0:19.200000",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-ar",
                    "24000",
                    "-ac",
                    "1",
                    str(truncated_mp4),
                ],
                check=True,
            )
            with self.assertRaises(AudioVerificationError):
                audio_finalizer.verify_finalized_mp4(
                    mp4_path=truncated_mp4,
                    wav_path=WAV_PATH,
                    expected_duration_sec=19.20,
                )

    def test_06_finalized_v3_1_1_mp4_previews_pass_all_10_checks(self):
        """Verify all 3 finalized V3.1.1 MP4 deliverables pass FFprobe, PCM RMS/Peak, lag, and phrase checks."""
        finalized_mp4s = [
            VIDEOS_DIR / "preview_V3_1_1_sem_carimbo_lowres.mp4",
            VIDEOS_DIR / "preview_V3_1_1_narrado_lowres.mp4",
            VIDEOS_DIR / "preview_V3_1_1_com_carimbo_lowres.mp4",
        ]
        timing_data = json.loads(TIMING_PATH.read_text(encoding="utf-8"))

        for mp4_path in finalized_mp4s:
            self.assertTrue(mp4_path.is_file(), f"Missing finalized MP4: {mp4_path}")
            report = audio_finalizer.verify_finalized_mp4(
                mp4_path=mp4_path,
                wav_path=WAV_PATH,
                expected_duration_sec=19.20,
                timing_data=timing_data,
            )
            self.assertEqual(report["status"], "PASSED")
            self.assertEqual(report["ffprobe_validation"]["video_codec"], "h264")
            self.assertEqual(report["ffprobe_validation"]["video_nb_frames"], 576)
            self.assertEqual(report["ffprobe_validation"]["audio_codec"], "aac")
            self.assertGreater(report["ffprobe_validation"]["audio_bit_rate_bps"], 80_000)

            pcm = report["pcm_audibility_validation"]
            self.assertGreater(pcm["mp4_active_rms_dbfs"], -22.0)
            self.assertGreater(pcm["mp4_peak_dbfs"], -4.0)
            self.assertLessEqual(pcm["rms_diff_db"], 0.2)

            sync = report["sync_and_content_comparison"]
            self.assertEqual(sync["best_lag_samples"], 0)
            self.assertAlmostEqual(sync["best_lag_ms"], 0.0, places=2)
            self.assertGreater(sync["zero_lag_sample_correlation"], 0.999)
            self.assertGreater(sync["zero_lag_envelope_10ms_correlation"], 0.999)
            self.assertLess(sync["tail_rms_dbfs"], -80.0)
            self.assertEqual(sync["phrases_verified"], 6)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPipelineV31)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
