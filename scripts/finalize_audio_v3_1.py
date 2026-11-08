"""Standalone CLI for Automatic FFmpeg Audiovisual Finalization & Verification (Pipeline V3.1+).

Takes a Blender-rendered H.264 MP4 video and a WAV narration file, removes any silent/erroneous audio
stream, muxes the WAV as AAC without re-encoding the H.264 video, pads only the remaining tail with
silence up to the planned scene duration, and verifies streams + RMS/Peak + WAV correlation.

Usage (default V3.1 batch finalization without re-rendering in Blender):
  blender -b --factory-startup -P scripts/finalize_audio_v3_1.py

Usage (custom single file):
  blender -b --factory-startup -P scripts/finalize_audio_v3_1.py -- --video input.mp4 --audio narr.wav --output output.mp4
"""

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_scene_v3_1 import DEFAULT_TIMING, DEFAULT_WAV, finalize_existing_v3_1_videos
from pipeline_v3 import audio_finalizer, v3_1_narrated_scene


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="FFmpeg Audiovisual Finalizer & Verifier")
    parser.add_argument("--video", type=str, default=None, help="Input H.264 MP4 video rendered by Blender.")
    parser.add_argument("--audio", type=str, default=str(DEFAULT_WAV), help="Input narration WAV file.")
    parser.add_argument("--output", type=str, default=None, help="Output finalized MP4 path (must not overwrite protected files).")
    parser.add_argument("--timing", type=str, default=str(DEFAULT_TIMING), help="Path to timing.json.")
    return parser.parse_args(argv)


def main():
    args = parse_args()
    wav_path = Path(args.audio).resolve()
    timing_path = Path(args.timing).resolve()

    if args.video and args.output:
        timing_data = v3_1_narrated_scene.load_timing_json(timing_path) if timing_path.is_file() else None
        expected_dur = float(timing_data["timeline_config"]["scene_duration_sec"]) if timing_data else None
        audio_finalizer.finalize_mp4_with_narration(
            video_mp4_path=Path(args.video).resolve(),
            wav_path=wav_path,
            output_mp4_path=Path(args.output).resolve(),
            expected_duration_sec=expected_dur,
            timing_data=timing_data,
        )
    else:
        finalize_existing_v3_1_videos(wav_path, timing_path)


if __name__ == "__main__":
    main()

