"""V3.1 Narrated Synchronization & Visual Signature ('Carimbo da Dúvida') Module.

Adapts the existing V3 scene (`cena_01_V3.blend`) to the real timestamps of the 18.72s working narration
(`audio/narracoes/EP001/testes/narracao_B_flash_lite_V1.wav`) defined in `timing.json`, WITHOUT rebuilding
the character, environment, or modeling pipeline.

Also creates and integrates:
1. Contextual 'No-Money Village' 3D emblem (`Selo_Sem_Dinheiro_Root`) during Phrase 2 ('E na vila dele, ninguém usava dinheiro').
2. Standalone reusable visual signature test 'Carimbo da Dúvida' (`objetos/carimbo_duvida.blend` / `Carimbo_Duvida_Root`)
   for side-by-side comparison (with and without signature) during Phrase 6 ('Nico... aí complicou.').
"""

import json
import math
import wave
from pathlib import Path
import bpy
import numpy as np

from . import config
from .primitives import (
    create_beveled_box,
    create_cylinder,
    create_empty,
    create_uv_sphere,
)
from .scene_setup import set_camera_cut_holds, set_interpolation

rad = math.radians


def ensure_collection(name: str, parent_col):
    """Return existing collection by name or create and link it to parent_col."""
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        parent_col.children.link(col)
    return col


def load_timing_json(timing_path: Path = None) -> dict:
    """Load timing.json from the repository root or episode folder."""
    if timing_path is None:
        timing_path = config.PROJECT_ROOT / "timing.json"
        if not timing_path.is_file():
            timing_path = config.EP001_DIR / "timing.json"
    return json.loads(Path(timing_path).read_text(encoding="utf-8"))


def generate_waveform_visualization(wav_path: Path, timing_data: dict, output_png: Path) -> Path:
    """Render a high-contrast waveform + RMS envelope PNG with phrase boundary markers from timing.json."""
    wav_path = Path(wav_path)
    output_png = Path(output_png)
    output_png.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(wav_path), "rb") as wf:
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    total_sec = float(timing_data["timeline_config"]["scene_duration_sec"])

    width, height = 1600, 520
    canvas = np.full((height, width, 4), (0.09, 0.10, 0.13, 1.0), dtype=np.float32)

    # Color-code phrase intervals in the background
    phrase_colors = [
        (0.18, 0.32, 0.52, 1.0),
        (0.16, 0.42, 0.34, 1.0),
        (0.44, 0.32, 0.14, 1.0),
        (0.48, 0.18, 0.20, 1.0),
        (0.16, 0.36, 0.56, 1.0),
        (0.38, 0.22, 0.48, 1.0),
    ]
    for idx, ph in enumerate(timing_data.get("phrases", [])):
        x0 = max(0, min(width - 1, int((ph["start_sec"] / total_sec) * width)))
        x1 = max(0, min(width, int((ph["end_sec"] / total_sec) * width)))
        col = phrase_colors[idx % len(phrase_colors)]
        canvas[40 : height - 40, x0:x1] = col
        # Bright boundary lines at start and end of each phrase
        canvas[30 : height - 30, max(0, x0 - 1) : min(width, x0 + 2)] = (0.95, 0.82, 0.25, 1.0)
        canvas[30 : height - 30, max(0, x1 - 1) : min(width, x1 + 2)] = (0.95, 0.82, 0.25, 1.0)

    # Vertical grid lines every 1.0 second
    for sec_i in range(1, int(total_sec) + 1):
        gx = int((sec_i / total_sec) * width)
        if 0 <= gx < width:
            canvas[40 : height - 40 : 4, gx] = (0.28, 0.30, 0.35, 1.0)

    # Center zero line
    mid_y = height // 2
    canvas[mid_y - 1 : mid_y + 1, :] = (0.35, 0.38, 0.44, 1.0)

    # Plot min/max waveform envelope per horizontal pixel column
    audio_dur = len(samples) / float(sr)
    audio_cols = int((audio_dur / total_sec) * width)
    half_h = int(height * 0.40)

    for cx in range(min(width, audio_cols)):
        t0 = (cx / float(width)) * total_sec
        t1 = ((cx + 1) / float(width)) * total_sec
        s0 = max(0, min(len(samples) - 1, int(t0 * sr)))
        s1 = max(s0 + 1, min(len(samples), int(t1 * sr)))
        chunk = samples[s0:s1]
        vmin = float(np.min(chunk))
        vmax = float(np.max(chunk))
        rms_v = float(np.sqrt(np.mean(chunk * chunk)))

        y_min = max(20, min(height - 20, int(mid_y + vmin * half_h)))
        y_max = max(20, min(height - 20, int(mid_y + vmax * half_h)))
        canvas[y_min : y_max + 1, cx] = (0.38, 0.86, 0.98, 1.0)

        y_rms_lo = max(20, min(height - 20, int(mid_y - rms_v * half_h)))
        y_rms_hi = max(20, min(height - 20, int(mid_y + rms_v * half_h)))
        canvas[y_rms_lo : y_rms_hi + 1, cx] = (0.98, 0.92, 0.35, 1.0)

    img = bpy.data.images.new("Waveform_Timing_V3_1", width=width, height=height, alpha=True)
    img.pixels.foreach_set(canvas.ravel())
    img.filepath_raw = str(output_png)
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)
    print(f"[OK] Saved waveform visualization: {output_png}")
    return output_png


def build_no_money_context_badge(col, mats):
    """Build a 3D 'No Money / Barter Only' badge (Gold Coin crossed out by Red Prohibition Slash) for Phrase 2."""
    existing = bpy.data.objects.get("Selo_Sem_Dinheiro_Root")
    if existing is not None:
        return existing

    # Placed in the clear open space between Nico and the cobbler stall in Shot 2 (in front of all stall posts)
    root = create_empty(
        "Selo_Sem_Dinheiro_Root",
        location=(-0.38, -0.62, 1.92),
        col=col,
        rot=(0.0, 0.0, rad(8)),
        empty_size=0.12,
    )

    # Outer bold red prohibition ring
    create_cylinder(
        "Selo_Sem_Dinheiro_AnelVermelho",
        radius1=0.42,
        radius2=0.42,
        depth=0.036,
        vertices=28,
        location=(0.0, 0.008, 0.0),
        mat=mats["Mat_sign_x_red"],
        col=col,
        parent=root,
        rot=(rad(90), 0.0, 0.0),
        bevel_width=0.010,
        shade_smooth=True,
    )
    # Cream circular backing plate
    create_cylinder(
        "Selo_Sem_Dinheiro_Fundo",
        radius1=0.35,
        radius2=0.35,
        depth=0.045,
        vertices=28,
        location=(0.0, 0.0, 0.0),
        mat=mats["Mat_sign_board"],
        col=col,
        parent=root,
        rot=(rad(90), 0.0, 0.0),
        bevel_width=0.010,
        shade_smooth=True,
    )
    # Gold Coin in the center
    create_cylinder(
        "Selo_Moeda_Dourada",
        radius1=0.23,
        radius2=0.23,
        depth=0.055,
        vertices=24,
        location=(0.0, -0.025, 0.0),
        mat=mats["Mat_new_shoe_gold"],
        col=col,
        parent=root,
        rot=(rad(90), 0.0, 0.0),
        bevel_width=0.01,
        shade_smooth=True,
    )
    # Embossed vertical '$' bar & S-bars on the coin
    create_beveled_box(
        "Selo_Moeda_Cifrao_Haste",
        size_xyz=(0.036, 0.03, 0.28),
        location=(0.0, -0.055, 0.0),
        mat=mats["Mat_wood_dark"],
        col=col,
        parent=root,
        bevel_width=0.004,
    )
    for idx, zp in enumerate((0.06, -0.06)):
        create_beveled_box(
            f"Selo_Moeda_Cifrao_Curva_{idx+1}",
            size_xyz=(0.13, 0.03, 0.042),
            location=(0.0, -0.055, zp),
            mat=mats["Mat_wood_dark"],
            col=col,
            parent=root,
            bevel_width=0.004,
        )

    # Bold Red Diagonal Prohibition Slash ('NO MONEY')
    create_beveled_box(
        "Selo_Sem_Dinheiro_FaixaProibicao",
        size_xyz=(0.74, 0.058, 0.095),
        location=(0.0, -0.068, 0.0),
        mat=mats["Mat_sign_x_red"],
        col=col,
        parent=root,
        rot=(0.0, rad(42), 0.0),
        bevel_width=0.012,
    )

    return root


def build_carimbo_da_duvida_asset(col, mats):
    """Build the standalone reusable 'Carimbo da Dúvida' visual signature (3D Question Stamp Badge)."""
    existing = bpy.data.objects.get("Carimbo_Duvida_Root")
    if existing is not None:
        return existing

    # Positioned cleanly in the upper-left space next to Nico's cap in Shot 7 so it never touches his head/ear
    root = create_empty(
        "Carimbo_Duvida_Root",
        location=(-0.44, -0.52, 1.62),
        col=col,
        rot=(0.0, rad(-10), rad(12)),
        empty_size=0.10,
    )

    # Deep navy circular stamp base
    create_cylinder(
        "Carimbo_Duvida_Base",
        radius1=0.145,
        radius2=0.145,
        depth=0.032,
        vertices=20,
        location=(0.0, 0.0, 0.0),
        mat=mats["Mat_sign_milk_bg"],
        col=col,
        parent=root,
        rot=(rad(90), 0.0, 0.0),
        bevel_width=0.008,
        shade_smooth=True,
    )
    # Warm gold outer stamp ring
    create_cylinder(
        "Carimbo_Duvida_AnelOuro",
        radius1=0.162,
        radius2=0.162,
        depth=0.022,
        vertices=20,
        location=(0.0, 0.006, 0.0),
        mat=mats["Mat_new_shoe_gold"],
        col=col,
        parent=root,
        rot=(rad(90), 0.0, 0.0),
        bevel_width=0.006,
        shade_smooth=True,
    )

    # Sculpted 3D Question Mark ('?') in bright cream/white on the front of the stamp
    # Top hook of '?'
    hook_segments = [
        ((-0.032, -0.024, 0.048), (0.036, 0.028, 0.042), rad(-25)),
        ((0.0, -0.024, 0.072), (0.058, 0.028, 0.034), 0.0),
        ((0.036, -0.024, 0.048), (0.036, 0.028, 0.048), rad(15)),
        ((0.016, -0.024, 0.012), (0.036, 0.028, 0.046), rad(-32)),
        ((0.0, -0.024, -0.022), (0.034, 0.028, 0.038), 0.0),
    ]
    for idx, (loc, sz, ry) in enumerate(hook_segments):
        create_beveled_box(
            f"Carimbo_Interrogacao_Seg_{idx+1}",
            size_xyz=sz,
            location=loc,
            mat=mats["Mat_milk_white"],
            col=col,
            parent=root,
            rot=(0.0, ry, 0.0),
            bevel_width=0.006,
            shade_smooth=True,
        )

    # Bottom dot of '?'
    create_uv_sphere(
        "Carimbo_Interrogacao_Ponto",
        radius=0.022,
        segments=12,
        rings=10,
        location=(0.0, -0.024, -0.072),
        mat=mats["Mat_new_shoe_gold"],
        col=col,
        parent=root,
        scale_xyz=(1.0, 0.65, 1.0),
        shade_smooth=True,
    )

    return root


def save_standalone_carimbo_library(output_blend_path: Path):
    """Save the 'Carimbo da Dúvida' as an independent reusable .blend resource in objetos/carimbo_duvida.blend."""
    from . import materials_lighting, scene_setup

    scene = bpy.context.scene
    scene_setup.clean_scene()
    col = ensure_collection("Col_Carimbo_Duvida", scene.collection)
    mats_raw = materials_lighting.build_material_library()
    # Map Mat_ prefix keys so build_carimbo_da_duvida_asset works identically in standalone or opened scene
    mats = {f"Mat_{k}": v for k, v in mats_raw.items()}
    carimbo = build_carimbo_da_duvida_asset(col, mats)
    carimbo.location = (0.0, 0.0, 0.0)
    carimbo.rotation_euler = (0.0, 0.0, 0.0)

    output_blend_path = Path(output_blend_path).resolve()
    output_blend_path.parent.mkdir(parents=True, exist_ok=True)
    # Evita o erro de caminho do cache de miniaturas neste processo.
    bpy.context.preferences.filepaths.file_preview_type = 'NONE'
    bpy.ops.wm.save_as_mainfile(filepath=str(output_blend_path), relative_remap=True)
    print(f"[ASSET LIB OK] Saved standalone Carimbo da Dúvida library: {output_blend_path}")
    return output_blend_path


def _clear_object_anim(obj):
    """Remove existing keyframes/action from an object without touching its geometry or hierarchy."""
    if obj is not None and obj.animation_data is not None:
        obj.animation_data_clear()


def _key_transform(obj, frame, loc=None, rot=None, scale=None):
    """Insert location, rotation_euler, and/or scale keyframes on an object."""
    if obj is None:
        return
    f = int(round(frame))
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert(data_path="location", frame=f)
    if rot is not None:
        obj.rotation_euler = rot
        obj.keyframe_insert(data_path="rotation_euler", frame=f)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert(data_path="scale", frame=f)


def _set_facial_expression(nico, frame, state="neutral"):
    """Keyframe Nico's eyebrows and mouth for clear emotion synced to narration."""
    eb_l = nico["eyebrow_l"]
    eb_r = nico["eyebrow_r"]
    mouth = nico["mouth"]

    if state == "worried_shoe":
        _key_transform(eb_l, frame, loc=(-0.102, -0.228, 0.348), rot=(rad(-10), rad(-14), 0.0))
        _key_transform(eb_r, frame, loc=(0.102, -0.228, 0.348), rot=(rad(-10), rad(14), 0.0))
        _key_transform(mouth, frame, scale=(0.92, 1.0, 0.85))
    elif state == "surprised":
        _key_transform(eb_l, frame, loc=(-0.102, -0.228, 0.368), rot=(rad(-10), rad(8), 0.0))
        _key_transform(eb_r, frame, loc=(0.102, -0.228, 0.368), rot=(rad(-10), rad(-8), 0.0))
        _key_transform(mouth, frame, scale=(0.76, 1.1, 2.25))
    elif state == "happy_idea":
        _key_transform(eb_l, frame, loc=(-0.102, -0.228, 0.358), rot=(rad(-10), rad(6), 0.0))
        _key_transform(eb_r, frame, loc=(0.102, -0.228, 0.358), rot=(rad(-10), rad(-6), 0.0))
        _key_transform(mouth, frame, scale=(1.28, 1.0, 0.82))
    elif state == "effort":
        _key_transform(eb_l, frame, loc=(-0.102, -0.228, 0.336), rot=(rad(-10), rad(10), 0.0))
        _key_transform(eb_r, frame, loc=(0.102, -0.228, 0.336), rot=(rad(-10), rad(-10), 0.0))
        _key_transform(mouth, frame, scale=(1.10, 1.0, 0.72))
    elif state == "frustrated":
        _key_transform(eb_l, frame, loc=(-0.102, -0.228, 0.338), rot=(rad(-10), rad(16), 0.0))
        _key_transform(eb_r, frame, loc=(0.102, -0.228, 0.338), rot=(rad(-10), rad(-16), 0.0))
        _key_transform(mouth, frame, scale=(1.22, 1.0, 1.38))
    else:
        _key_transform(eb_l, frame, loc=(-0.102, -0.228, 0.342), rot=(rad(-10), 0.0, 0.0))
        _key_transform(eb_r, frame, loc=(0.102, -0.228, 0.342), rot=(rad(-10), 0.0, 0.0))
        _key_transform(mouth, frame, scale=(1.0, 1.0, 1.0))


def _lookup_existing_scene_refs():
    """Retrieve existing V3 character, seller, prop, and camera objects from bpy.data.objects."""
    objs = bpy.data.objects
    nico = {
        "root": objs.get("Nico_Root"),
        "armature": objs.get("Nico_Armature_V3"),
        "pelvis": objs.get("Nico_Pelvis"),
        "torso": objs.get("Nico_Torso"),
        "head": objs.get("Nico_Head"),
        "eyebrow_l": objs.get("Nico_Sobrancelha_L"),
        "eyebrow_r": objs.get("Nico_Sobrancelha_R"),
        "mouth": objs.get("Nico_Boca"),
        "arm_l": objs.get("Nico_Arm_L"),
        "forearm_l": objs.get("Nico_Forearm_L"),
        "arm_r": objs.get("Nico_Arm_R"),
        "forearm_r": objs.get("Nico_Forearm_R"),
        "leg_l": objs.get("Nico_Leg_L"),
        "knee_l": objs.get("Nico_Knee_L"),
        "foot_l": objs.get("Nico_Foot_L"),
        "leg_r": objs.get("Nico_Leg_R"),
        "knee_r": objs.get("Nico_Knee_R"),
        "foot_r": objs.get("Nico_Foot_R"),
        "damaged_sole": objs.get("Nico_Sola_Descolada_Pivot_R"),
    }
    seller = {
        "root": objs.get("Vendedor_Root"),
        "torso": objs.get("Vendedor_Torso"),
        "head": objs.get("Vendedor_Head"),
        "arm_l": objs.get("Vendedor_Arm_L"),
        "arm_r": objs.get("Vendedor_Arm_R"),
    }
    props = {
        "sack": objs.get("Saco_Batatas_Root"),
        "puffs": [objs.get(f"Poeira_Impacto_{i+1}") for i in range(6)],
        "x_sign": objs.get("Placa_Recusa_X_Root"),
        "milk_sign": objs.get("Placa_Desejo_Leite_Root"),
    }
    cam_rig = {
        "camera": objs.get("Camera_Principal"),
        "target": objs.get("Camera_Target"),
    }
    return nico, seller, props, cam_rig


def retime_scene_to_timing_data(scene, timing_data: dict, include_carimbo: bool = False):
    """Re-keyframe the opened V3 scene to synchronize with all 6 phrases in timing.json."""
    fps = int(timing_data["timeline_config"]["fps"])
    frame_start = int(timing_data["timeline_config"]["scene_frame_start"])
    frame_end = int(timing_data["timeline_config"]["scene_frame_end"])

    scene.render.fps = fps
    scene.frame_start = frame_start
    scene.frame_end = frame_end

    phrases = {p["id"]: p for p in timing_data["phrases"]}
    p1, p2, p3, p4, p5, p6 = phrases[1], phrases[2], phrases[3], phrases[4], phrases[5], phrases[6]

    # Derive key frame numbers directly from timing.json so future voice replacements adapt automatically
    f_p1_start = p1["start_frame"]                                     # 12 (0.41s): "O sapato do Nico..."
    f_p1_peak = p1["peak_frame"]                                       # 27 (0.89s): "...sapato do Nico"
    f_p1_stumble_start = p1["sub_segments"][-1]["start_frame"]         # 58 (1.92s): "...pediu demissão."
    f_p1_end = p1["end_frame"]                                         # 85 (2.82s)
    f_cut_shot2 = int((f_p1_end + p2["start_frame"]) // 2) + 4         # 100 (3.33s): Cut to Village & Fair

    f_p2_start = p2["start_frame"]                                     # 106 (3.54s): "E na vila dele..."
    f_p2_nomoney = p2["sub_segments"][-1]["start_frame"] - 3           # 134 (4.47s): "...ninguém usava dinheiro."
    f_p2_end = p2["end_frame"]                                         # 171 (5.70s)
    f_cut_shot3a = p3["start_frame"] - 2                               # 187 (6.23s): Cut to Nico + Potato Cart

    f_p3_start = p3["start_frame"]                                     # 189 (6.30s): "Ele tinha um saco de batatas..."
    f_p3_batatas_end = p3["sub_segments"][0]["end_frame"]              # 238 (7.92s)
    f_cut_shot3b = f_p3_batatas_end + 1                                # 239 (7.97s): Cut to Heavy Walk
    f_p3_trocar_end = p3["sub_segments"][1]["end_frame"]               # 291 (9.70s): "...e achou que dava pra trocar"
    f_cut_shot4 = f_p3_trocar_end                                      # 291 (9.70s): Cut to Counter Arrival
    f_ploc = f_cut_shot4 + 7                                           # 298 (9.93s): "PLOC!" on counter
    f_p3_end = p3["end_frame"]                                         # 316 (10.54s): "...por um par novo."

    f_p4_start = p4["start_frame"]                                     # 332 (11.08s): "Só que o sapateiro..."
    f_p4_sapateiro_end = p4["sub_segments"][0]["end_frame"]            # 366 (12.21s)
    f_cut_shot5 = f_p4_sapateiro_end + 3                               # 369 (12.30s): Cut to Refusal Framing
    f_p4_nao_queria = p4["sub_segments"][-1]["start_frame"]            # 373 (12.44s): "...não queria batatas."
    f_p4_peak = p4["peak_frame"]                                       # 392 (13.07s)
    f_p4_end = p4["end_frame"]                                         # 413 (13.77s)

    f_p5_start = p5["start_frame"]                                     # 432 (14.41s): "Queria leite."
    f_cut_shot6 = f_p5_start                                           # 432 (14.41s): Focus on Milk Sign
    f_p5_peak = p5["peak_frame"]                                       # 451 (15.04s): Peak on "leite"
    f_p5_end = p5["end_frame"]                                         # 463 (15.44s)

    f_cut_shot7 = p6["start_frame"] - 4                                # 480 (16.00s): Cut to Nico Close-Up
    f_p6_start = p6["start_frame"]                                     # 484 (16.15s): "Nico..."
    f_p6_pause_start = p6["sub_segments"][1]["start_frame"]            # 505 (16.83s): "..."
    f_p6_complicou_start = p6["sub_segments"][-1]["start_frame"]       # 516 (17.20s): "aí complicou."
    f_p6_end = p6["end_frame"]                                         # 542 (18.05s)

    nico, seller, props, cam_rig = _lookup_existing_scene_refs()
    col_props = bpy.data.collections.get("Col_Props_Animados") or scene.collection
    mats = {m.name: m for m in bpy.data.materials}

    # Build/ensure V3.1 contextual No-Money badge and optional Carimbo da Dúvida
    no_money_badge = build_no_money_context_badge(col_props, mats)
    carimbo_badge = build_carimbo_da_duvida_asset(col_props, mats)

    # Clear previous V3 animations from all animated objects
    for group in (nico.values(), seller.values(), [props["sack"], props["x_sign"], props["milk_sign"]], props["puffs"], cam_rig.values(), [no_money_badge, carimbo_badge]):
        for obj in group:
            _clear_object_anim(obj)

    root = nico["root"]
    pelvis = nico["pelvis"]
    torso = nico["torso"]
    head = nico["head"]
    arm_l = nico["arm_l"]
    forearm_l = nico["forearm_l"]
    arm_r = nico["arm_r"]
    forearm_r = nico["forearm_r"]
    leg_l = nico["leg_l"]
    knee_l = nico["knee_l"]
    foot_l = nico["foot_l"]
    leg_r = nico["leg_r"]
    knee_r = nico["knee_r"]
    foot_r = nico["foot_r"]
    sole_r = nico["damaged_sole"]

    # ==========================================================================
    # 1. NICO ANIMATION SYNCED TO THE 6 PHRASES
    # ==========================================================================
    # PHRASE 1 (Frames 1..99 | 0.00s..3.30s): "O sapato do Nico pediu demissão."
    _key_transform(root, 1, loc=(-2.28, -0.62, 0.0), rot=(0.0, 0.0, rad(32)))
    _key_transform(pelvis, 1, loc=(0.0, 0.0, 0.78), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, 1, rot=(rad(6), 0.0, 0.0))
    _key_transform(head, 1, rot=(rad(10), 0.0, rad(-6)))
    _key_transform(arm_l, 1, rot=(rad(-14), rad(8), 0.0))
    _key_transform(forearm_l, 1, rot=(rad(-22), 0.0, 0.0))
    _key_transform(arm_r, 1, rot=(rad(12), rad(-8), 0.0))
    _key_transform(forearm_r, 1, rot=(rad(-20), 0.0, 0.0))
    _key_transform(leg_l, 1, rot=(rad(8), 0.0, 0.0))
    _key_transform(knee_l, 1, rot=(rad(6), 0.0, 0.0))
    _key_transform(foot_l, 1, rot=(rad(-8), 0.0, 0.0))
    _key_transform(leg_r, 1, rot=(rad(-14), 0.0, 0.0))
    _key_transform(knee_r, 1, rot=(rad(14), 0.0, 0.0))
    _key_transform(foot_r, 1, rot=(rad(-4), 0.0, 0.0))
    _key_transform(sole_r, 1, rot=(rad(12), 0.0, 0.0))
    _set_facial_expression(nico, 1, "neutral")

    # "O sapato do Nico" (frames 12..48): Right foot lifts and thin front sole peels wide open ("boca de jacaré")
    for fr_open, sole_ang in ((f_p1_start + 4, 29), (f_p1_peak + 8, 31)):
        _key_transform(root, fr_open, loc=(-2.16, -0.61, 0.0), rot=(0.0, 0.0, rad(34)))
        _key_transform(pelvis, fr_open, loc=(0.0, 0.0, 0.79), rot=(0.0, rad(-3), 0.0))
        _key_transform(torso, fr_open, rot=(rad(10), 0.0, rad(-4)))
        _key_transform(head, fr_open, rot=(rad(16), 0.0, rad(-8)))
        _key_transform(arm_l, fr_open, rot=(rad(-24), rad(12), 0.0))
        _key_transform(forearm_l, fr_open, rot=(rad(-35), 0.0, 0.0))
        _key_transform(arm_r, fr_open, rot=(rad(18), rad(-10), 0.0))
        _key_transform(forearm_r, fr_open, rot=(rad(-30), 0.0, 0.0))
        _key_transform(leg_l, fr_open, rot=(rad(4), 0.0, 0.0))
        _key_transform(knee_l, fr_open, rot=(rad(4), 0.0, 0.0))
        _key_transform(foot_l, fr_open, rot=(rad(-4), 0.0, 0.0))
        _key_transform(leg_r, fr_open, rot=(rad(-34), 0.0, 0.0))
        _key_transform(knee_r, fr_open, rot=(rad(28), 0.0, 0.0))
        _key_transform(foot_r, fr_open, rot=(rad(-10), 0.0, 0.0))
        _key_transform(sole_r, fr_open, rot=(rad(sole_ang), 0.0, 0.0))
        _set_facial_expression(nico, fr_open, "worried_shoe")

    # Snag on stepping stone right before "pediu demissão" (frame 52)
    f_snag = f_p1_stumble_start - 6
    _key_transform(root, f_snag, loc=(-2.04, -0.60, 0.0), rot=(0.0, 0.0, rad(38)))
    _key_transform(pelvis, f_snag, loc=(0.0, 0.0, 0.76), rot=(0.0, rad(4), 0.0))
    _key_transform(torso, f_snag, rot=(rad(16), rad(4), rad(-6)))
    _key_transform(head, f_snag, rot=(rad(20), 0.0, rad(-10)))
    _key_transform(leg_r, f_snag, rot=(rad(-26), 0.0, 0.0))
    _key_transform(knee_r, f_snag, rot=(rad(22), 0.0, 0.0))
    _key_transform(foot_r, f_snag, rot=(rad(-8), 0.0, 0.0))
    _key_transform(sole_r, f_snag, rot=(rad(32), 0.0, 0.0))
    _key_transform(sole_r, f_p1_stumble_start, rot=(rad(3), 0.0, 0.0))

    # Stumble peak right on "pediu demissão" (frame 68 / 2.27s)
    f_stumble_peak = f_p1_stumble_start + 10
    _key_transform(root, f_stumble_peak, loc=(-1.90, -0.58, 0.0), rot=(0.0, 0.0, rad(42)))
    _key_transform(pelvis, f_stumble_peak, loc=(0.0, 0.0, 0.70), rot=(rad(8), rad(-5), 0.0))
    _key_transform(torso, f_stumble_peak, rot=(rad(26), rad(-6), rad(8)))
    _key_transform(head, f_stumble_peak, rot=(rad(12), rad(6), rad(-12)))
    _key_transform(arm_l, f_stumble_peak, rot=(rad(-62), rad(34), rad(-18)))
    _key_transform(forearm_l, f_stumble_peak, rot=(rad(-48), 0.0, 0.0))
    _key_transform(arm_r, f_stumble_peak, rot=(rad(-48), rad(-36), rad(16)))
    _key_transform(forearm_r, f_stumble_peak, rot=(rad(-42), 0.0, 0.0))
    _key_transform(leg_l, f_stumble_peak, rot=(rad(-28), 0.0, 0.0))
    _key_transform(knee_l, f_stumble_peak, rot=(rad(44), 0.0, 0.0))
    _key_transform(foot_l, f_stumble_peak, rot=(rad(-16), 0.0, 0.0))
    _key_transform(leg_r, f_stumble_peak, rot=(rad(16), 0.0, 0.0))
    _key_transform(knee_r, f_stumble_peak, rot=(rad(24), 0.0, 0.0))
    _key_transform(foot_r, f_stumble_peak, rot=(rad(-22), 0.0, 0.0))
    _key_transform(sole_r, f_stumble_peak, rot=(rad(26), 0.0, 0.0))
    _set_facial_expression(nico, f_stumble_peak, "surprised")

    # Recover balance during Pause 1->2 (frames 86..99)
    for fr_rec in (f_p1_end + 3, f_cut_shot2 - 1):
        _key_transform(root, fr_rec, loc=(-1.82, -0.56, 0.0), rot=(0.0, 0.0, rad(34)))
        _key_transform(pelvis, fr_rec, loc=(0.0, 0.0, 0.77), rot=(0.0, 0.0, 0.0))
        _key_transform(torso, fr_rec, rot=(rad(12), 0.0, rad(-4)))
        _key_transform(head, fr_rec, rot=(rad(18), 0.0, rad(-8)))
        _key_transform(arm_l, fr_rec, rot=(rad(-18), rad(12), 0.0))
        _key_transform(forearm_l, fr_rec, rot=(rad(-32), 0.0, 0.0))
        _key_transform(arm_r, fr_rec, rot=(rad(-14), rad(-12), 0.0))
        _key_transform(forearm_r, fr_rec, rot=(rad(-28), 0.0, 0.0))
        _key_transform(leg_l, fr_rec, rot=(0.0, 0.0, 0.0))
        _key_transform(knee_l, fr_rec, rot=(0.0, 0.0, 0.0))
        _key_transform(foot_l, fr_rec, rot=(0.0, 0.0, 0.0))
        _key_transform(leg_r, fr_rec, rot=(rad(-24), 0.0, 0.0))
        _key_transform(knee_r, fr_rec, rot=(rad(20), 0.0, 0.0))
        _key_transform(foot_r, fr_rec, rot=(rad(-6), 0.0, 0.0))
        _key_transform(sole_r, fr_rec, rot=(rad(24), 0.0, 0.0))
        _set_facial_expression(nico, fr_rec, "worried_shoe")

    # PHRASE 2 (Frames 100..186 | 3.33s..6.20s): "E na vila dele, ninguém usava dinheiro."
    # Nico looks around at the village fair & cobbler stall, then toward his potato cart
    _key_transform(root, f_p2_start + 6, loc=(-1.76, -0.55, 0.0), rot=(0.0, 0.0, rad(24)))
    _key_transform(pelvis, f_p2_start + 6, loc=(0.0, 0.0, 0.78), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, f_p2_start + 6, rot=(rad(4), 0.0, rad(-10)))
    _key_transform(head, f_p2_start + 6, rot=(rad(-2), rad(-4), rad(-28)))
    _key_transform(arm_l, f_p2_start + 6, rot=(rad(-16), rad(14), 0.0))
    _key_transform(forearm_l, f_p2_start + 6, rot=(rad(-30), 0.0, 0.0))
    _key_transform(arm_r, f_p2_start + 6, rot=(rad(-20), rad(-14), 0.0))
    _key_transform(forearm_r, f_p2_start + 6, rot=(rad(-36), 0.0, 0.0))
    _key_transform(leg_r, f_p2_start + 6, rot=(rad(-16), 0.0, 0.0))
    _key_transform(knee_r, f_p2_start + 6, rot=(rad(14), 0.0, 0.0))
    _key_transform(foot_r, f_p2_start + 6, rot=(rad(-4), 0.0, 0.0))
    _key_transform(sole_r, f_p2_start + 6, rot=(rad(20), 0.0, 0.0))
    _set_facial_expression(nico, f_p2_start + 6, "neutral")

    # During "ninguém usava dinheiro" (frames 145..184): Nico glances at the No-Money sign & his potato cart
    _key_transform(root, f_p2_end + 8, loc=(-1.74, -0.54, 0.0), rot=(0.0, 0.0, rad(28)))
    _key_transform(head, f_p2_end + 8, rot=(rad(4), rad(4), rad(-10)))
    _set_facial_expression(nico, f_p2_end + 8, "worried_shoe")

    # PHRASE 3A (Frames 187..238 | 6.23s..7.93s): "Ele tinha um saco de batatas..."
    # Confident "Aha!" idea gesture pointing from potatoes to the stall (frames 194..216)
    for fr_idea in (f_p3_start + 5, f_p3_start + 27):
        _key_transform(root, fr_idea, loc=(-1.72, -0.54, 0.0), rot=(0.0, 0.0, rad(32)))
        _key_transform(pelvis, fr_idea, loc=(0.0, 0.0, 0.80), rot=(0.0, 0.0, 0.0))
        _key_transform(torso, fr_idea, rot=(rad(-4), 0.0, rad(-6)))
        _key_transform(head, fr_idea, rot=(rad(-6), rad(4), rad(-14)))
        _key_transform(arm_l, fr_idea, rot=(rad(-26), rad(14), 0.0))
        _key_transform(forearm_l, fr_idea, rot=(rad(-42), 0.0, 0.0))
        _key_transform(arm_r, fr_idea, rot=(rad(-68), rad(-16), rad(12)))
        _key_transform(forearm_r, fr_idea, rot=(rad(-52), 0.0, 0.0))
        _key_transform(leg_l, fr_idea, rot=(0.0, 0.0, 0.0))
        _key_transform(knee_l, fr_idea, rot=(0.0, 0.0, 0.0))
        _key_transform(foot_l, fr_idea, rot=(0.0, 0.0, 0.0))
        _key_transform(leg_r, fr_idea, rot=(rad(-12), 0.0, 0.0))
        _key_transform(knee_r, fr_idea, rot=(rad(12), 0.0, 0.0))
        _key_transform(foot_r, fr_idea, rot=(rad(-4), 0.0, 0.0))
        _key_transform(sole_r, fr_idea, rot=(rad(16), 0.0, 0.0))
        _set_facial_expression(nico, fr_idea, "happy_idea")

    # Anticipation squat to grab the 40kg sack off the wooden handcart (frame 227)
    f_squat = f_p3_batatas_end - 11
    _key_transform(root, f_squat, loc=(-1.56, -0.34, 0.0), rot=(0.0, 0.0, rad(18)))
    _key_transform(pelvis, f_squat, loc=(0.0, 0.0, 0.67), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, f_squat, rot=(rad(24), 0.0, 0.0))
    _key_transform(head, f_squat, rot=(rad(-8), 0.0, 0.0))
    _key_transform(arm_l, f_squat, rot=(rad(-56), rad(-16), 0.0))
    _key_transform(forearm_l, f_squat, rot=(rad(-38), 0.0, 0.0))
    _key_transform(arm_r, f_squat, rot=(rad(-56), rad(16), 0.0))
    _key_transform(forearm_r, f_squat, rot=(rad(-38), 0.0, 0.0))
    _key_transform(leg_l, f_squat, rot=(rad(-28), 0.0, 0.0))
    _key_transform(knee_l, f_squat, rot=(rad(52), 0.0, 0.0))
    _key_transform(foot_l, f_squat, rot=(rad(-24), 0.0, 0.0))
    _key_transform(leg_r, f_squat, rot=(rad(-28), 0.0, 0.0))
    _key_transform(knee_r, f_squat, rot=(rad(52), 0.0, 0.0))
    _key_transform(foot_r, f_squat, rot=(rad(-24), 0.0, 0.0))
    _key_transform(sole_r, f_squat, rot=(0.0, 0.0, 0.0))
    _set_facial_expression(nico, f_squat, "effort")

    # Heaves the 40kg sack against his chest (frame 238)
    _key_transform(root, f_p3_batatas_end, loc=(-1.42, -0.50, 0.0), rot=(0.0, 0.0, rad(78)))
    _key_transform(pelvis, f_p3_batatas_end, loc=(0.0, 0.0, 0.76), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, f_p3_batatas_end, rot=(rad(-8), 0.0, 0.0))
    _key_transform(head, f_p3_batatas_end, rot=(rad(8), 0.0, rad(-12)))
    _key_transform(arm_l, f_p3_batatas_end, rot=(rad(-54), rad(-20), 0.0))
    _key_transform(forearm_l, f_p3_batatas_end, rot=(rad(-62), 0.0, 0.0))
    _key_transform(arm_r, f_p3_batatas_end, rot=(rad(-54), rad(20), 0.0))
    _key_transform(forearm_r, f_p3_batatas_end, rot=(rad(-62), 0.0, 0.0))
    _key_transform(leg_l, f_p3_batatas_end, rot=(0.0, 0.0, 0.0))
    _key_transform(knee_l, f_p3_batatas_end, rot=(rad(8), 0.0, 0.0))
    _key_transform(foot_l, f_p3_batatas_end, rot=(rad(-8), 0.0, 0.0))
    _key_transform(leg_r, f_p3_batatas_end, rot=(0.0, 0.0, 0.0))
    _key_transform(knee_r, f_p3_batatas_end, rot=(rad(8), 0.0, 0.0))
    _key_transform(foot_r, f_p3_batatas_end, rot=(rad(-8), 0.0, 0.0))
    _key_transform(sole_r, f_p3_batatas_end, rot=(0.0, 0.0, 0.0))
    _set_facial_expression(nico, f_p3_batatas_end, "effort")

    # PHRASE 3B (Frames 239..290 | 7.97s..9.67s): "...e achou que dava pra trocar..."
    # 4 grounded heavy steps from X = -1.42 to X = 0.02 (13 frames per step = 52 frames: 238 -> 290)
    walk_x_start = -1.42
    walk_x_end = 0.02
    num_steps = 4
    step_dur = 13

    for s in range(num_steps + 1):
        fr = f_p3_batatas_end + s * step_dur
        t = s / float(num_steps)
        wx = walk_x_start + (walk_x_end - walk_x_start) * t
        wy = -0.50 + 0.02 * t
        yaw = rad(74) if s < num_steps else rad(48)

        _key_transform(root, fr, loc=(wx, wy, 0.0), rot=(0.0, 0.0, yaw))
        _key_transform(pelvis, fr, loc=(0.0, 0.0, 0.775), rot=(0.0, rad(3 if s % 2 == 0 else -3), 0.0))
        _key_transform(torso, fr, rot=(rad(-7), rad(-3 if s % 2 == 0 else 3), rad(4 if s % 2 == 0 else -4)))
        _key_transform(head, fr, rot=(rad(6), 0.0, rad(-16)))
        _key_transform(arm_l, fr, rot=(rad(-54), rad(-20), 0.0))
        _key_transform(forearm_l, fr, rot=(rad(-62), 0.0, 0.0))
        _key_transform(arm_r, fr, rot=(rad(-54), rad(20), 0.0))
        _key_transform(forearm_r, fr, rot=(rad(-62), 0.0, 0.0))

        if s == num_steps:
            _key_transform(leg_l, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(knee_l, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(foot_l, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(leg_r, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(knee_r, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(foot_r, fr, rot=(0.0, 0.0, 0.0))
            _key_transform(sole_r, fr, rot=(0.0, 0.0, 0.0))
        elif s % 2 == 0:
            _key_transform(leg_l, fr, rot=(rad(-24), 0.0, 0.0))
            _key_transform(knee_l, fr, rot=(rad(10), 0.0, 0.0))
            _key_transform(foot_l, fr, rot=(rad(12), 0.0, 0.0))
            _key_transform(leg_r, fr, rot=(rad(22), 0.0, 0.0))
            _key_transform(knee_r, fr, rot=(rad(18), 0.0, 0.0))
            _key_transform(foot_r, fr, rot=(rad(-16), 0.0, 0.0))
            _key_transform(sole_r, fr, rot=(rad(20), 0.0, 0.0))
        else:
            _key_transform(leg_l, fr, rot=(rad(22), 0.0, 0.0))
            _key_transform(knee_l, fr, rot=(rad(18), 0.0, 0.0))
            _key_transform(foot_l, fr, rot=(rad(-16), 0.0, 0.0))
            _key_transform(leg_r, fr, rot=(rad(-24), 0.0, 0.0))
            _key_transform(knee_r, fr, rot=(rad(10), 0.0, 0.0))
            _key_transform(foot_r, fr, rot=(rad(10), 0.0, 0.0))
            _key_transform(sole_r, fr, rot=(rad(4), 0.0, 0.0))

        if s < num_steps:
            fr_mid = fr + step_dur // 2
            _key_transform(pelvis, fr_mid, loc=(0.0, 0.0, 0.735), rot=(0.0, 0.0, 0.0))
            if s % 2 == 0:
                _key_transform(leg_l, fr_mid, rot=(rad(2), 0.0, 0.0))
                _key_transform(knee_l, fr_mid, rot=(rad(18), 0.0, 0.0))
                _key_transform(foot_l, fr_mid, rot=(rad(-16), 0.0, 0.0))
                _key_transform(leg_r, fr_mid, rot=(rad(-18), 0.0, 0.0))
                _key_transform(knee_r, fr_mid, rot=(rad(36), 0.0, 0.0))
                _key_transform(foot_r, fr_mid, rot=(rad(-10), 0.0, 0.0))
                _key_transform(sole_r, fr_mid, rot=(rad(28), 0.0, 0.0))
            else:
                _key_transform(leg_l, fr_mid, rot=(rad(-18), 0.0, 0.0))
                _key_transform(knee_l, fr_mid, rot=(rad(36), 0.0, 0.0))
                _key_transform(foot_l, fr_mid, rot=(rad(-10), 0.0, 0.0))
                _key_transform(leg_r, fr_mid, rot=(rad(2), 0.0, 0.0))
                _key_transform(knee_r, fr_mid, rot=(rad(18), 0.0, 0.0))
                _key_transform(foot_r, fr_mid, rot=(rad(-16), 0.0, 0.0))
                _key_transform(sole_r, fr_mid, rot=(0.0, 0.0, 0.0))

    # PHRASE 3C (Frames 291..331 | 9.70s..11.03s): "...por um par novo."
    # Effort heave onto counter (frame 293) -> "PLOC!" landing (frame 298) -> proud offer gesture (frames 306..364)
    _key_transform(root, f_cut_shot4 + 2, loc=(0.02, -0.46, 0.0), rot=(0.0, 0.0, rad(44)))
    _key_transform(pelvis, f_cut_shot4 + 2, loc=(0.0, 0.0, 0.81), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, f_cut_shot4 + 2, rot=(rad(-12), 0.0, rad(-6)))
    _key_transform(head, f_cut_shot4 + 2, rot=(rad(-6), 0.0, rad(-10)))
    _key_transform(arm_l, f_cut_shot4 + 2, rot=(rad(-78), rad(-12), 0.0))
    _key_transform(forearm_l, f_cut_shot4 + 2, rot=(rad(-45), 0.0, 0.0))
    _key_transform(arm_r, f_cut_shot4 + 2, rot=(rad(-78), rad(12), 0.0))
    _key_transform(forearm_r, f_cut_shot4 + 2, rot=(rad(-45), 0.0, 0.0))
    _set_facial_expression(nico, f_cut_shot4 + 2, "effort")

    _key_transform(pelvis, f_ploc, loc=(0.0, 0.0, 0.76), rot=(0.0, 0.0, 0.0))
    _key_transform(torso, f_ploc, rot=(rad(8), 0.0, rad(-4)))

    for fr_offer in (f_ploc + 8, f_p4_sapateiro_end):
        _key_transform(root, fr_offer, loc=(0.00, -0.48, 0.0), rot=(0.0, 0.0, rad(36)))
        _key_transform(pelvis, fr_offer, loc=(0.0, 0.0, 0.78), rot=(0.0, 0.0, 0.0))
        _key_transform(torso, fr_offer, rot=(rad(4), 0.0, rad(-10)))
        _key_transform(head, fr_offer, rot=(rad(-4), 0.0, rad(-16)))
        _key_transform(arm_r, fr_offer, rot=(rad(-64), rad(-18), rad(-12)))
        _key_transform(forearm_r, fr_offer, rot=(rad(-28), 0.0, 0.0))
        _key_transform(arm_l, fr_offer, rot=(rad(-22), rad(14), 0.0))
        _key_transform(forearm_l, fr_offer, rot=(rad(-46), 0.0, 0.0))
        _key_transform(leg_r, fr_offer, rot=(rad(-10), 0.0, 0.0))
        _key_transform(knee_r, fr_offer, rot=(rad(10), 0.0, 0.0))
        _key_transform(foot_r, fr_offer, rot=(rad(-4), 0.0, 0.0))
        _key_transform(sole_r, fr_offer, rot=(rad(16), 0.0, 0.0))
        _set_facial_expression(nico, fr_offer, "happy_idea")

    # PHRASE 4 (Frames 332..431 | 11.08s..14.37s): "Só que o sapateiro não queria batatas."
    # When Red X pops on "não queria batatas" (frame 375), Nico recoils in surprise
    for fr_x in (f_p4_nao_queria + 3, f_p5_start - 4):
        _key_transform(root, fr_x, loc=(-0.05, -0.48, 0.0), rot=(0.0, 0.0, rad(28)))
        _key_transform(pelvis, fr_x, loc=(0.0, 0.0, 0.76), rot=(0.0, 0.0, 0.0))
        _key_transform(torso, fr_x, rot=(rad(-8), 0.0, rad(6)))
        _key_transform(head, fr_x, rot=(rad(-10), 0.0, rad(-18)))
        _key_transform(arm_l, fr_x, rot=(rad(-52), rad(14), 0.0))
        _key_transform(forearm_l, fr_x, rot=(rad(-64), 0.0, 0.0))
        _key_transform(arm_r, fr_x, rot=(rad(-52), rad(-14), 0.0))
        _key_transform(forearm_r, fr_x, rot=(rad(-64), 0.0, 0.0))
        _set_facial_expression(nico, fr_x, "surprised")

    # PHRASE 5 (Frames 432..479 | 14.41s..15.97s): "Queria leite."
    for fr_milk in (f_p5_start + 6, f_cut_shot7 - 2):
        _key_transform(root, fr_milk, loc=(-0.05, -0.48, 0.0), rot=(0.0, 0.0, rad(24)))
        _key_transform(pelvis, fr_milk, loc=(0.0, 0.0, 0.77), rot=(0.0, 0.0, 0.0))
        _key_transform(torso, fr_milk, rot=(rad(-6), 0.0, rad(4)))
        _key_transform(head, fr_milk, rot=(rad(-12), rad(4), rad(-22)))
        _key_transform(arm_l, fr_milk, rot=(rad(-58), rad(14), 0.0))
        _key_transform(forearm_l, fr_milk, rot=(rad(-68), 0.0, 0.0))
        _key_transform(arm_r, fr_milk, rot=(rad(-58), rad(-14), 0.0))
        _key_transform(forearm_r, fr_milk, rot=(rad(-68), 0.0, 0.0))
        _set_facial_expression(nico, fr_milk, "surprised")

    # PHRASE 6 (Frames 480..576 | 16.00s..19.20s): "Nico... aí complicou."
    # "Nico..." (484..505): Looks from Milk Sign down to his 40kg sack of potatoes on the counter
    _key_transform(root, f_p6_start, loc=(-0.05, -0.48, 0.0), rot=(0.0, 0.0, rad(20)))
    _key_transform(head, f_p6_start, rot=(rad(-12), rad(4), rad(-22)))
    _set_facial_expression(nico, f_p6_start, "surprised")

    _key_transform(head, f_p6_pause_start, rot=(rad(12), rad(-4), rad(-26)))
    _key_transform(arm_l, f_p6_pause_start, rot=(rad(-32), rad(14), 0.0))
    _key_transform(forearm_l, f_p6_pause_start, rot=(rad(-52), 0.0, 0.0))
    _key_transform(arm_r, f_p6_pause_start, rot=(rad(-32), rad(-14), 0.0))
    _key_transform(forearm_r, f_p6_pause_start, rot=(rad(-52), 0.0, 0.0))
    _set_facial_expression(nico, f_p6_pause_start, "worried_shoe")

    # "aí complicou." (516..542) + visual hold to 576: Comic frustrated shrug toward camera!
    for fr_end in (f_p6_complicou_start + 6, f_p6_end, frame_end):
        _key_transform(root, fr_end, loc=(-0.05, -0.48, 0.0), rot=(0.0, 0.0, rad(18)))
        _key_transform(pelvis, fr_end, loc=(0.0, 0.0, 0.73), rot=(0.0, 0.0, 0.0))
        _key_transform(torso, fr_end, rot=(rad(8), rad(-3), 0.0))
        _key_transform(head, fr_end, rot=(rad(4), rad(8), rad(-8)))
        _key_transform(arm_l, fr_end, rot=(rad(-20), rad(18), rad(-6)))
        _key_transform(forearm_l, fr_end, rot=(rad(-46), 0.0, 0.0))
        _key_transform(arm_r, fr_end, rot=(rad(-20), rad(-18), rad(6)))
        _key_transform(forearm_r, fr_end, rot=(rad(-46), 0.0, 0.0))
        _key_transform(leg_l, fr_end, rot=(rad(-6), 0.0, 0.0))
        _key_transform(knee_l, fr_end, rot=(rad(12), 0.0, 0.0))
        _key_transform(foot_l, fr_end, rot=(rad(-6), 0.0, 0.0))
        _key_transform(leg_r, fr_end, rot=(rad(-14), 0.0, 0.0))
        _key_transform(knee_r, fr_end, rot=(rad(16), 0.0, 0.0))
        _key_transform(foot_r, fr_end, rot=(rad(-6), 0.0, 0.0))
        _key_transform(sole_r, fr_end, rot=(rad(18), 0.0, 0.0))
        _set_facial_expression(nico, fr_end, "frustrated")

    for k, part in nico.items():
        if k != "armature" and part is not None:
            set_interpolation(part, interpolation="BEZIER")

    # ==========================================================================
    # 2. SELLER ANIMATION SYNCED TO PHRASES 3C, 4 & 5
    # ==========================================================================
    s_head = seller["head"]
    s_torso = seller["torso"]
    s_arm_l = seller["arm_l"]
    s_arm_r = seller["arm_r"]

    _key_transform(s_head, 1, rot=(0.0, 0.0, rad(-20)))
    _key_transform(s_torso, 1, rot=(0.0, 0.0, 0.0))
    _key_transform(s_arm_l, 1, rot=(rad(-10), rad(8), 0.0))
    _key_transform(s_arm_r, 1, rot=(rad(-10), rad(-8), 0.0))

    # Looks down at 40kg potato sack landing on counter (frame 302)
    _key_transform(s_head, f_ploc + 4, rot=(rad(22), 0.0, rad(-18)))
    _key_transform(s_torso, f_ploc + 4, rot=(rad(8), 0.0, 0.0))

    # "Só que o sapateiro..." (frames 332..366): Shakes head NO vigorously!
    _key_transform(s_head, f_p4_start + 2, rot=(rad(10), 0.0, rad(-36)))
    _key_transform(s_head, f_p4_start + 13, rot=(rad(10), 0.0, rad(8)))
    _key_transform(s_head, f_p4_start + 24, rot=(rad(10), 0.0, rad(-36)))
    _key_transform(s_head, f_p4_start + 34, rot=(rad(8), 0.0, rad(4)))
    _key_transform(s_head, f_p4_nao_queria + 4, rot=(rad(6), 0.0, rad(-14)))

    # Raises left arm on "não queria batatas" (Red X) and right arm on "Queria leite" (Milk Sign)
    _key_transform(s_arm_l, f_p4_nao_queria, rot=(rad(-68), rad(16), 0.0))
    _key_transform(s_arm_r, f_p4_nao_queria, rot=(rad(-14), rad(-8), 0.0))
    _key_transform(s_arm_r, f_p5_start + 2, rot=(rad(-78), rad(-20), 0.0))
    _key_transform(s_head, f_p5_start + 6, rot=(rad(-6), 0.0, rad(-8)))

    # Settle during Phrase 6
    _key_transform(s_arm_l, f_cut_shot7, rot=(rad(-18), rad(10), 0.0))
    _key_transform(s_arm_r, f_cut_shot7, rot=(rad(-18), rad(-10), 0.0))
    _key_transform(s_head, frame_end, rot=(rad(4), 0.0, rad(-15)))

    for part in seller.values():
        if part is not None:
            set_interpolation(part, interpolation="BEZIER")

    # ==========================================================================
    # 3. POTATO SACK & COUNTER DUST PUFFS SYNCED TO PHRASE 3
    # ==========================================================================
    sack = props["sack"]
    cx, cy, cz = config.POSITIONS["sack_on_cart"]
    cnt_x, cnt_y, cnt_z = config.POSITIONS["sack_on_counter"]

    sack_keys = [
        # Sitting on wooden handcart from Frame 1 until Nico squats to grab it at frame 225
        (1, (cx, cy, cz), (1.0, 1.0, 1.0), (0.0, 0.0, rad(-8))),
        (f_squat - 2, (cx, cy, cz), (1.0, 1.0, 1.0), (0.0, 0.0, rad(-8))),
        (f_squat, (cx - 0.02, cy - 0.06, cz - 0.02), (1.06, 1.04, 0.92), (rad(8), 0.0, rad(-4))),
        (f_p3_batatas_end, (-1.28, -0.50, 0.78), (0.96, 0.96, 1.05), (rad(14), rad(-6), 0.0)),

        # Carried during the 4 heavy steps (frames 239..290)
        (f_p3_batatas_end + 7, (-1.10, -0.50, 0.83), (1.0, 1.0, 1.0), (rad(12), rad(4), 0.0)),
        (f_p3_batatas_end + 13, (-0.92, -0.50, 0.76), (1.03, 1.02, 0.96), (rad(15), rad(-4), 0.0)),
        (f_p3_batatas_end + 20, (-0.70, -0.49, 0.83), (1.0, 1.0, 1.0), (rad(12), rad(4), 0.0)),
        (f_p3_batatas_end + 26, (-0.50, -0.49, 0.76), (1.03, 1.02, 0.96), (rad(15), rad(-4), 0.0)),
        (f_p3_batatas_end + 33, (-0.30, -0.48, 0.83), (1.0, 1.0, 1.0), (rad(12), rad(4), 0.0)),
        (f_p3_batatas_end + 39, (-0.12, -0.48, 0.76), (1.03, 1.02, 0.96), (rad(15), rad(-4), 0.0)),
        (f_p3_batatas_end + 46, (0.04, -0.46, 0.83), (1.0, 1.0, 1.0), (rad(12), rad(3), 0.0)),
        (f_cut_shot4, (0.18, -0.42, 0.80), (1.0, 1.0, 1.0), (rad(10), 0.0, 0.0)),

        # Heave and "PLOC!" onto counter at frame 298 ("por um par novo")
        (f_cut_shot4 + 3, (0.44, -0.32, 1.18), (0.94, 0.94, 1.08), (rad(-8), rad(6), rad(-6))),
        (f_ploc, (cnt_x, cnt_y, cnt_z), (1.24, 1.20, 0.74), (rad(4), rad(-4), rad(-10))),
        (f_ploc + 5, (cnt_x, cnt_y, cnt_z), (0.93, 0.94, 1.10), (rad(-2), rad(2), rad(-10))),
        (f_ploc + 11, (cnt_x, cnt_y, cnt_z), (1.0, 1.0, 1.0), (0.0, 0.0, rad(-10))),
        (frame_end, (cnt_x, cnt_y, cnt_z), (1.0, 1.0, 1.0), (0.0, 0.0, rad(-10))),
    ]
    for fr, loc, sc, rot in sack_keys:
        _key_transform(sack, fr, loc=loc, rot=rot, scale=sc)
    set_interpolation(sack, interpolation="BEZIER")

    for i, puff in enumerate(props["puffs"]):
        if puff is None:
            continue
        ang = i * (2.0 * math.pi / 6.0)
        dx = math.cos(ang) * 0.34
        dy = math.sin(ang) * 0.26
        puff_keys = [
            (1, (cnt_x, cnt_y, cnt_z + 0.02), (0.001, 0.001, 0.001)),
            (f_ploc - 2, (cnt_x, cnt_y, cnt_z + 0.02), (0.001, 0.001, 0.001)),
            (f_ploc + 3, (cnt_x + dx * 0.55, cnt_y + dy * 0.55, cnt_z + 0.08), (1.15, 1.15, 0.85)),
            (f_ploc + 14, (cnt_x + dx, cnt_y + dy, cnt_z + 0.14), (0.001, 0.001, 0.001)),
            (frame_end, (cnt_x + dx, cnt_y + dy, cnt_z + 0.14), (0.001, 0.001, 0.001)),
        ]
        for fr, loc, sc in puff_keys:
            _key_transform(puff, fr, loc=loc, scale=sc)
        set_interpolation(puff, interpolation="BEZIER")

    # ==========================================================================
    # 4. STORY SIGNS: NO-MONEY BADGE (PHRASE 2), RED X (PHRASE 4), MILK (PHRASE 5), CARIMBO (PHRASE 6)
    # ==========================================================================
    # A. No-Money Village Contextual Badge ("E na vila dele, ninguém usava dinheiro", frames 134..185)
    no_money_badge.location = (-0.38, -0.62, 1.92)
    nm_keys = [
        (1, (0.001, 0.001, 0.001), (0.0, 0.0, rad(8))),
        (f_p2_nomoney - 2, (0.001, 0.001, 0.001), (0.0, 0.0, rad(8))),
        (f_p2_nomoney + 7, (1.22, 1.22, 1.22), (0.0, rad(8), rad(8))),
        (f_p2_nomoney + 13, (0.94, 0.94, 0.94), (0.0, rad(-4), rad(8))),
        (f_p2_nomoney + 18, (1.0, 1.0, 1.0), (0.0, 0.0, rad(8))),
        (f_cut_shot3a - 4, (1.0, 1.0, 1.0), (0.0, 0.0, rad(8))),
        (f_cut_shot3a, (0.001, 0.001, 0.001), (0.0, 0.0, rad(8))),
        (frame_end, (0.001, 0.001, 0.001), (0.0, 0.0, rad(8))),
    ]
    for fr, sc, rot in nm_keys:
        _key_transform(no_money_badge, fr, rot=rot, scale=sc)
    set_interpolation(no_money_badge, interpolation="BEZIER")

    # B. Red X Sign ("...não queria batatas", frame 373 -> peak 382 -> settle 392; recedes slightly when Milk pops)
    x_root = props["x_sign"]
    if x_root is not None:
        x_root.location = (0.58, -0.26, 1.76)
    x_keys = [
        (1, (0.001, 0.001, 0.001), (0.0, 0.0, rad(8))),
        (f_p4_nao_queria - 1, (0.001, 0.001, 0.001), (0.0, 0.0, rad(8))),
        (f_p4_nao_queria + 9, (1.28, 1.28, 1.28), (0.0, rad(8), rad(8))),
        (f_p4_nao_queria + 14, (0.92, 0.92, 0.92), (0.0, rad(-4), rad(8))),
        (f_p4_peak, (1.0, 1.0, 1.0), (0.0, 0.0, rad(8))),
        (f_p5_start, (1.0, 1.0, 1.0), (0.0, 0.0, rad(8))),
        (f_p5_start + 10, (0.76, 0.76, 0.76), (0.0, 0.0, rad(8))),
        (frame_end, (0.76, 0.76, 0.76), (0.0, 0.0, rad(8))),
    ]
    for fr, sc, rot in x_keys:
        _key_transform(x_root, fr, rot=rot, scale=sc)
    set_interpolation(x_root, interpolation="BEZIER")

    # C. Large Milk Sign ("Queria leite.", frame 432 -> peak 443 -> settle 451 on "leite")
    m_root = props["milk_sign"]
    if m_root is not None:
        m_root.location = (1.30, -0.24, 1.94)
    m_keys = [
        (1, (0.001, 0.001, 0.001), (0.0, 0.0, rad(-10))),
        (f_p5_start, (0.001, 0.001, 0.001), (0.0, 0.0, rad(-10))),
        (f_p5_start + 10, (1.22, 1.22, 1.22), (0.0, rad(-8), rad(-10))),
        (f_p5_start + 15, (0.92, 0.92, 0.92), (0.0, rad(4), rad(-10))),
        (f_p5_peak, (0.98, 0.98, 0.98), (0.0, 0.0, rad(-10))),
        (frame_end, (0.98, 0.98, 0.98), (0.0, 0.0, rad(-10))),
    ]
    for fr, sc, rot in m_keys:
        _key_transform(m_root, fr, rot=rot, scale=sc)
    set_interpolation(m_root, interpolation="BEZIER")

    # D. Optional Visual Signature "Carimbo da Dúvida" (Phrase 6: "Nico... aí complicou", frames 507..576)
    carimbo_badge.location = (-0.44, -0.52, 1.62)
    if include_carimbo:
        carimbo_keys = [
            (1, (0.001, 0.001, 0.001), (0.0, rad(-10), rad(12))),
            (f_p6_pause_start + 2, (0.001, 0.001, 0.001), (0.0, rad(-26), rad(12))),
            (f_p6_pause_start + 7, (1.26, 1.26, 1.26), (0.0, rad(-6), rad(12))),
            (f_p6_complicou_start, (0.92, 0.92, 0.92), (0.0, rad(-14), rad(12))),
            (f_p6_complicou_start + 5, (1.0, 1.0, 1.0), (0.0, rad(-10), rad(12))),
            (frame_end, (1.0, 1.0, 1.0), (0.0, rad(-10), rad(12))),
        ]
    else:
        carimbo_keys = [
            (1, (0.001, 0.001, 0.001), (0.0, rad(-10), rad(12))),
            (frame_end, (0.001, 0.001, 0.001), (0.0, rad(-10), rad(12))),
        ]
    for fr, sc, rot in carimbo_keys:
        _key_transform(carimbo_badge, fr, rot=rot, scale=sc)
    set_interpolation(carimbo_badge, interpolation="BEZIER")

    # ==========================================================================
    # 5. 7-SHOT CAMERA DIRECTION SYNCED TO THE 6 PHRASES
    # ==========================================================================
    cam_obj = cam_rig["camera"]
    target = cam_rig["target"]

    shots = [
        # Shot 1 (Frames 1..99 | Phrase 1: "O sapato do Nico pediu demissão.")
        # Starts in tight close-up of the shoe peeling open (1..42), then pulls back for the stumble (42..99)
        (1, (-1.68, -2.02, 0.40), (-2.12, -0.66, 0.22)),
        (f_p1_peak + 8, (-1.62, -1.92, 0.36), (-2.04, -0.66, 0.20)),
        (f_snag, (-1.68, -2.55, 0.64), (-2.00, -0.62, 0.48)),
        (f_stumble_peak, (-1.80, -3.82, 1.05), (-1.94, -0.58, 0.78)),
        (f_cut_shot2 - 1, (-1.78, -3.82, 1.06), (-1.88, -0.56, 0.80)),

        # Shot 2 (Frames 100..186 | Phrase 2: "E na vila dele, ninguém usava dinheiro.")
        # Wide contextual shot of the rustic village, fair stall, No-Money badge, and Nico by the potato cart
        (f_cut_shot2, (-0.62, -8.65, 1.88), (-0.44, 0.15, 1.24)),
        (f_p2_nomoney + 12, (-0.58, -8.50, 1.85), (-0.42, 0.12, 1.24)),
        (f_cut_shot3a - 1, (-0.64, -8.10, 1.78), (-0.48, 0.05, 1.18)),

        # Shot 3A (Frames 187..238 | Phrase 3A: "Ele tinha um saco de batatas...")
        # Medium-Full shot on Nico & the 40kg potato sack on the wooden handcart -> Idea & Squat Pickup
        (f_cut_shot3a, (-1.66, -4.35, 1.28), (-1.64, -0.22, 0.86)),
        (f_squat - 4, (-1.64, -4.28, 1.26), (-1.60, -0.24, 0.86)),
        (f_p3_batatas_end, (-1.54, -4.22, 1.25), (-1.46, -0.35, 0.84)),

        # Shot 3B (Frames 239..290 | Phrase 3B: "...e achou que dava pra trocar...")
        # Dynamic tracking shot of Nico walking with the heavy 40kg sack toward the stall
        (f_cut_shot3b, (-1.15, -3.88, 1.12), (-1.22, -0.48, 0.78)),
        (f_cut_shot3b + 26, (-0.52, -3.88, 1.14), (-0.56, -0.48, 0.78)),
        (f_cut_shot4 - 1, (-0.12, -3.92, 1.16), (-0.16, -0.48, 0.80)),

        # Shot 4 (Frames 291..368 | Phrase 3C "...por um par novo." + Phrase 4A "Só que o sapateiro...")
        # Barter counter framing: "PLOC!" sack landing, Nico pointing to new shoes, Seller shaking head NO
        (f_cut_shot4, (0.48, -5.05, 1.56), (0.68, -0.18, 1.12)),
        (f_p3_end, (0.50, -5.02, 1.56), (0.68, -0.18, 1.12)),
        (f_cut_shot5 - 1, (0.52, -5.02, 1.56), (0.70, -0.18, 1.14)),

        # Shot 5 (Frames 369..431 | Phrase 4B: "...não queria batatas.")
        # Refusal framing: Red X pops over the potato sack while Nico recoils
        (f_cut_shot5, (0.52, -5.45, 1.60), (0.60, -0.20, 1.32)),
        (f_p4_peak, (0.52, -5.48, 1.60), (0.60, -0.20, 1.32)),
        (f_cut_shot6 - 1, (0.52, -5.48, 1.60), (0.60, -0.20, 1.32)),

        # Shot 6 (Frames 432..479 | Phrase 5: "Queria leite.")
        # Punch-in / pan emphasis toward the Large 3D Milk Sign (keeping Nico, X, and Milk Sign inside 9:16)
        (f_cut_shot6, (0.66, -5.65, 1.64), (0.78, -0.20, 1.38)),
        (f_p5_peak, (0.68, -5.62, 1.65), (0.80, -0.20, 1.40)),
        (f_cut_shot7 - 1, (0.68, -5.62, 1.65), (0.80, -0.20, 1.40)),

        # Shot 7 (Frames 480..576 | Phrase 6: "Nico... aí complicou.")
        # Medium Close-Up of Nico's comic frustration reaction + potato sack (and optional Carimbo da Dúvida)
        (f_cut_shot7, (0.08, -3.90, 1.34), (0.16, -0.36, 1.22)),
        (f_p6_complicou_start, (0.06, -3.84, 1.30), (0.12, -0.38, 1.18)),
        (frame_end, (0.06, -3.82, 1.30), (0.12, -0.38, 1.18)),
    ]

    for fr, c_loc, t_loc in shots:
        _key_transform(cam_obj, fr, loc=c_loc)
        _key_transform(target, fr, loc=t_loc)

    cut_hold_frames = [
        f_cut_shot2 - 1,
        f_cut_shot3a - 1,
        f_cut_shot3b - 1,
        f_cut_shot4 - 1,
        f_cut_shot5 - 1,
        f_cut_shot6 - 1,
        f_cut_shot7 - 1,
    ]
    set_camera_cut_holds(cam_obj, cut_hold_frames)
    set_camera_cut_holds(target, cut_hold_frames)

    return {
        "key_audit_frames": [
            (f_p1_peak + 8, "01_frase1_sapato_abrindo"),
            (f_stumble_peak, "02_frase1_pediu_demissao_tropeco"),
            (f_p2_nomoney + 16, "03_frase2_vila_sem_dinheiro"),
            (f_p3_start + 15, "04_frase3a_ideia_saco_batatas"),
            (f_cut_shot3b + 20, "05_frase3b_caminhada_trocar"),
            (f_ploc + 12, "06_frase3c_balcao_par_novo"),
            (f_p4_peak, "07_frase4_nao_queria_batatas_x"),
            (f_p5_peak, "08_frase5_queria_leite"),
            (f_p6_complicou_start + 14, "09_frase6_nico_ai_complicou"),
        ]
    }


def setup_vse_narration_audio(scene, wav_path: Path):
    """Attach the working WAV narration at Frame 1 in Blender's VSE and enable AAC audio output for MP4 renders."""
    wav_path = Path(wav_path).resolve()
    if not wav_path.is_file():
        raise FileNotFoundError(f"Missing narration WAV file: {wav_path}")

    if not scene.sequence_editor:
        scene.sequence_editor_create()
    se = scene.sequence_editor
    strips = se.strips if hasattr(se, "strips") else se.sequences

    # Remove any previous narration strips to stay idempotent
    for s in list(strips):
        if s.type == "SOUND" or s.name.startswith("Narracao_"):
            strips.remove(s)

    snd_strip = strips.new_sound(
        name="Narracao_Trabalho_EP001",
        filepath=str(wav_path),
        channel=1,
        frame_start=1,
    )
    snd_strip.volume = 1.0

    # Configure FFmpeg audio muxing (AAC 192 kbps, preserving original pitch and timing)
    scene.render.ffmpeg.audio_codec = "AAC"
    scene.render.ffmpeg.audio_bitrate = 192
    print(f"[AUDIO SYNC OK] Attached VSE sound strip '{snd_strip.name}' ({wav_path.name})")
    return snd_strip


def render_narrated_mp4_preview(scene, output_mp4_path: Path, wav_path: Path, preset_name="preview_video") -> Path:
    """Render a low-resolution MP4 preview and finalize/verify its AAC audio via FFmpeg + FFprobe."""
    from . import audio_finalizer
    from .scene_setup import configure_scene_and_render

    out_mp4 = Path(output_mp4_path).resolve()
    audio_finalizer.assert_not_protected_video(out_mp4)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    raw_video_mp4 = out_mp4.with_name(f"{out_mp4.stem}_raw_h264.mp4")

    orig_start, orig_end = scene.frame_start, scene.frame_end
    configure_scene_and_render(scene, preset_name=preset_name)
    scene.frame_start = orig_start
    scene.frame_end = orig_end
    setup_vse_narration_audio(scene, wav_path)

    scene.render.image_settings.media_type = "VIDEO"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    scene.render.ffmpeg.gopsize = 15
    scene.render.ffmpeg.audio_codec = "NONE"

    scene.render.filepath = str(raw_video_mp4)
    bpy.ops.render.render(animation=True)

    expected_dur = float(scene.frame_end - scene.frame_start + 1) / float(scene.render.fps)
    try:
        audio_finalizer.finalize_mp4_with_narration(
            video_mp4_path=raw_video_mp4,
            wav_path=Path(wav_path),
            output_mp4_path=out_mp4,
            expected_duration_sec=expected_dur,
        )
    finally:
        if raw_video_mp4.is_file():
            raw_video_mp4.unlink()

    print(f"[OK] Rendered and verified narrated MP4 preview: {out_mp4}")
    return out_mp4


def generate_carimbo_comparison_sheet(img_without_path: Path, img_with_path: Path, output_path: Path) -> Path:
    """Create a side-by-side comparison PNG of Phrase 6 WITHOUT vs. WITH the 'Carimbo da Dúvida' signature."""
    img_without_path = Path(img_without_path)
    img_with_path = Path(img_with_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cell_w, cell_h = 540, 960
    pad = 16
    sheet_w = cell_w * 2 + pad * 3
    sheet_h = cell_h + pad * 2 + 12

    canvas = np.full((sheet_h, sheet_w, 4), (0.09, 0.10, 0.12, 1.0), dtype=np.float32)

    def _load_scaled(p: Path):
        im = bpy.data.images.load(str(p), check_existing=False)
        im.scale(cell_w, cell_h)
        arr = np.empty(cell_w * cell_h * 4, dtype=np.float32)
        im.pixels.foreach_get(arr)
        bpy.data.images.remove(im)
        return arr.reshape((cell_h, cell_w, 4))

    arr_no = _load_scaled(img_without_path)
    arr_yes = _load_scaled(img_with_path)

    y0 = pad
    x_no = pad
    x_yes = pad * 2 + cell_w

    # Top accent bar: blue for Sem Assinatura, gold for Com Assinatura ('Carimbo da Dúvida')
    canvas[y0 + cell_h : y0 + cell_h + 8, x_no : x_no + cell_w] = (0.20, 0.56, 0.92, 1.0)
    canvas[y0 + cell_h : y0 + cell_h + 8, x_yes : x_yes + cell_w] = (0.98, 0.78, 0.16, 1.0)

    canvas[y0 : y0 + cell_h, x_no : x_no + cell_w] = arr_no
    canvas[y0 : y0 + cell_h, x_yes : x_yes + cell_w] = arr_yes

    out_im = bpy.data.images.new("Comparativo_Carimbo_Duvida", width=sheet_w, height=sheet_h, alpha=True)
    out_im.pixels.foreach_set(canvas.ravel())
    out_im.filepath_raw = str(output_path)
    out_im.file_format = "PNG"
    out_im.save()
    bpy.data.images.remove(out_im)
    print(f"[OK] Saved Carimbo da Dúvida comparison sheet: {output_path}")
    return output_path

