"""Render authored Blender shots in one session with verified frame reuse."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from uuid import uuid4

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.dont_write_bytecode = True
from pipeline_v3.config import PROJECT_ROOT


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inside(path, directory):
    path = (PROJECT_ROOT / path).resolve()
    if not path.is_relative_to(directory):
        raise ValueError(f"Path must be inside {directory}: {path}")
    return path


def select_shots(spec, shot_ids):
    ids = [plan["id"] for plan in spec["plans"]]
    if len(ids) != len(set(ids)) or len(shot_ids) != len(set(shot_ids)):
        raise ValueError("Duplicate shot ID")
    plans = []
    for shot_id in shot_ids:
        if shot_id not in ids or not re.fullmatch(r"[A-Za-z0-9_-]+", shot_id):
            raise ValueError(f"Invalid shot ID: {shot_id}")
        plan = spec["plans"][ids.index(shot_id)]
        first, last = plan["frames"]
        audit = plan["audit_frames"]
        if not 1 <= first <= last or not audit or any(not first <= frame <= last for frame in audit):
            raise ValueError(f"Invalid frame or audit range for {shot_id}")
        plans.append(plan)
    return plans


def source_signature(spec, blend):
    files = {blend, Path(__file__).resolve()}
    for raw in bpy.utils.blend_paths(absolute=True, packed=False):
        if raw != "<builtin>":
            files.add(Path(raw).resolve(strict=True))
    for raw in spec.get("inputs", []):
        files.add((PROJECT_ROOT / raw).resolve(strict=True))
    signature = hashlib.sha256(json.dumps(
        [bpy.app.version_string, bpy.app.build_hash.decode(), spec["render"]], sort_keys=True,
    ).encode())
    # Include each dependency path as well as its bytes so a relink invalidates the cache.
    for path in sorted(files):
        signature.update(os.fsencode(path))
        signature.update(bytes.fromhex(digest(path)))
    return signature


def shot_signature(source, plan):
    signature = source.copy()
    signature.update(json.dumps({key: plan[key] for key in ("frames", "camera")}, sort_keys=True).encode())
    return signature.hexdigest()


def verified(frame_path):
    checksum = frame_path.with_suffix(".sha256")
    try:
        return checksum.read_text(encoding="ascii").strip() == digest(frame_path)
    except (FileNotFoundError, UnicodeDecodeError):
        return False


def render_frame(scene, camera, frame, destination):
    pending = destination.with_name(f".{destination.stem}.{uuid4().hex}.png")
    checksum = pending.with_suffix(".sha256")
    try:
        scene.frame_set(frame)
        scene.camera = camera
        scene.render.filepath = str(pending)
        if 'FINISHED' not in bpy.ops.render.render(write_still=True):
            raise RuntimeError(f"Render did not complete for frame {frame}")
        with pending.open("rb") as stream:
            if stream.read(8) != b"\x89PNG\r\n\x1a\n":
                raise ValueError(f"Invalid PNG header: {pending}")
            stream.seek(-12, os.SEEK_END)
            if stream.read() != b"\x00\x00\x00\x00IEND\xaeB\x60\x82":
                raise ValueError(f"Incomplete PNG: {pending}")
        checksum.write_text(digest(pending) + "\n", encoding="ascii")
        pending.replace(destination)
        checksum.replace(destination.with_suffix(".sha256"))
    finally:
        pending.unlink(missing_ok=True)
        checksum.unlink(missing_ok=True)


def encode_preview(cache, first, last, scene, destination):
    from pipeline_v3.audio_finalizer import resolve_ffmpeg_binaries

    if destination.exists():
        raise FileExistsError(destination)
    ffmpeg, ffprobe = resolve_ffmpeg_binaries()
    pending = destination.with_name(f".{destination.stem}.{uuid4().hex}.mp4")
    try:
        subprocess.run([ffmpeg, "-v", "error", "-xerror", "-n", "-framerate",
                        str(scene.render.fps / scene.render.fps_base),
                        "-start_number", str(first), "-i", str(cache / "f_%04d.png"),
                        "-frames:v", str(last-first+1), "-an", "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(pending)], check=True)
        info = subprocess.check_output([ffprobe, "-v", "error", "-show_entries",
                                        "stream=nb_frames,width,height", "-of", "json", str(pending)])
        stream, = json.loads(info)["streams"]
        if (int(stream["nb_frames"]), stream["width"], stream["height"]) != (
            last-first+1, scene.render.resolution_x, scene.render.resolution_y
        ):
            raise ValueError(f"Incorrect preview frame count or dimensions: {pending}")
        subprocess.run([ffmpeg, "-v", "error", "-xerror", "-i", str(pending), "-f", "null", "-"], check=True)
        pending.rename(destination)
    finally:
        pending.unlink(missing_ok=True)


def main(argv):
    started = time.perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("plans", nargs="+")
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--frame", type=int)
    choice.add_argument("--range", type=int, nargs=2, metavar=("FIRST", "LAST"))
    choice.add_argument("--audit", action="store_true")
    choice.add_argument("--shot", action="store_true")
    parser.add_argument("--preview", type=Path)
    args = parser.parse_args(argv)
    spec_path = inside(args.spec, PROJECT_ROOT)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    plans = select_shots(spec, args.plans)
    if args.preview and (args.audit or len(plans) != 1):
        parser.error("Preview requires one shot and a contiguous range")

    cache_root = inside(spec["cache"], PROJECT_ROOT)
    preview = inside(args.preview, spec_path.parent) if args.preview else None
    if preview and (preview.suffix.lower() != ".mp4" or preview.exists()):
        parser.error("Preview requires an unused .mp4 path")
    blend = inside(spec["blend"], PROJECT_ROOT)
    bpy.ops.wm.open_mainfile(filepath=str(blend), load_ui=False)
    loaded = time.perf_counter()
    scene = bpy.context.scene
    width, height = spec["render"]["resolution"]
    samples = spec["render"]["samples"]
    if min(width, height, samples) <= 0 or width % 2 or height % 2:
        parser.error("Render resolution must be positive and even, with positive samples")
    source = source_signature(spec, blend)
    jobs = []
    for plan in plans:
        first, last = args.range or plan["frames"]
        if args.frame is not None:
            first = last = args.frame
        camera = scene.objects.get(plan["camera"])
        if (camera is None or camera.type != "CAMERA"
            or not plan["frames"][0] <= first <= last <= plan["frames"][1]
            or not scene.frame_start <= first <= last <= scene.frame_end):
            parser.error(f"Camera or frame range is absent from shot {plan['id']}")
        cache = cache_root / plan["id"] / shot_signature(source, plan)
        if not args.audit and last-first+1 > 4 and not all(
            verified(cache / f"f_{frame:04d}.png") for frame in plan["audit_frames"]
        ):
            parser.error(f"Render and inspect --audit frames first for {plan['id']}")
        frames = plan["audit_frames"] if args.audit else range(first, last+1)
        jobs.append((plan["id"], camera, cache, frames, first, last))

    scene.render.use_sequencer = False
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.use_file_extension = True
    scene.render.use_persistent_data = True
    scene.eevee.taa_render_samples = samples
    prepared = time.perf_counter()
    first_render = None
    summaries = []
    for shot_id, camera, cache, frames, first, last in jobs:
        shot_started = time.perf_counter()
        cache.mkdir(parents=True, exist_ok=True)
        rendered = []
        for frame in frames:
            destination = cache / f"f_{frame:04d}.png"
            if not verified(destination):
                frame_started = time.perf_counter()
                render_frame(scene, camera, frame, destination)
                if first_render is None:
                    first_render = time.perf_counter()-frame_started
                rendered.append(frame)
        if preview:
            encode_preview(cache, first, last, scene, preview)
        summary = dict(id=shot_id, camera=camera.name, rendered=rendered, reused=len(frames)-len(rendered),
                       seconds=time.perf_counter()-shot_started, cache=str(cache))
        summaries.append(summary)
        print("PLAN " + json.dumps(summary), flush=True)
    print("BATCH " + json.dumps(dict(plans=len(summaries), open_seconds=loaded-started,
          prepare_seconds=prepared-loaded, first_render_seconds=first_render,
          total_seconds=time.perf_counter()-started)), flush=True)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:])
