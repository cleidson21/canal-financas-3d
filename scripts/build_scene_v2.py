"""Main orchestrator script for building, animating, validating, and rendering cena_01_V2.blend in Blender 5.2 LTS.

Updated for the modular V3 repository structure using pathlib.Path.
Usage from command line:
  blender.exe -b --factory-startup -P scripts/build_scene_v2.py -- --mode build
  blender.exe -b --factory-startup -P scripts/build_scene_v2.py -- --mode stills
  blender.exe -b --factory-startup -P scripts/build_scene_v2.py -- --mode video-preview
  blender.exe -b --factory-startup -P scripts/build_scene_v2.py -- --mode video-final
"""

import argparse
import importlib
import sys
from pathlib import Path
import bpy


def resolve_project_root() -> Path:
    """Resolve the repository root consistently whether run via CLI or inside Blender's Text Editor."""
    if "__file__" in globals():
        p = Path(__file__).resolve()
        if p.parent.name == "scripts":
            return p.parent.parent
        for parent in p.parents:
            if (parent / "scripts").is_dir() and (parent / "episodios").is_dir():
                return parent
    if bpy.data.filepath:
        bp = Path(bpy.data.filepath).resolve()
        for parent in bp.parents:
            if (parent / "scripts").is_dir() and (parent / "episodios").is_dir():
                return parent
    cwd = Path.cwd().resolve()
    if (cwd / "scripts").is_dir():
        return cwd
    return cwd


PROJECT_ROOT = resolve_project_root()
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from pipeline_v2 import (
    config,
    scene_setup,
    primitives,
    materials_lighting,
    environment_fair,
    character_nico,
    anim_props,
    anim_character,
    cinematography,
    render_pipeline,
)

for _mod in (
    config,
    scene_setup,
    primitives,
    materials_lighting,
    environment_fair,
    character_nico,
    anim_props,
    anim_character,
    cinematography,
    render_pipeline,
):
    importlib.reload(_mod)


def build_complete_scene(preset_name="preview_stills"):
    """Build the entire V2 low-poly village, fair, Nico, props, animation, lighting, and camera idempotently."""
    scene = bpy.context.scene
    scene_setup.clean_scene()
    cols = scene_setup.create_collections(scene)
    scene_setup.configure_scene_and_render(scene, preset_name=preset_name)

    mats = materials_lighting.build_material_library()
    lights = materials_lighting.setup_world_and_lighting(scene, cols["Col_Luzes_Cameras"])
    env = environment_fair.build_village_and_fair(cols, mats)
    nico = character_nico.build_character_nico(cols["Col_Personagem_Nico"], mats)
    seller = character_nico.build_character_seller(cols["Col_Feira_Barraca"], mats)

    sack = anim_props.build_and_animate_potato_sack(cols["Col_Props_Animados"], mats)
    signs = anim_props.build_and_animate_refusal_and_milk_signs(cols["Col_Props_Animados"], mats)

    anim_character.animate_nico(nico)
    anim_character.animate_seller(seller)
    cam_rig = cinematography.setup_and_animate_camera(scene, cols["Col_Luzes_Cameras"])

    scene.frame_set(1)
    return {
        "scene": scene,
        "collections": cols,
        "materials": mats,
        "lights": lights,
        "environment": env,
        "nico": nico,
        "seller": seller,
        "sack": sack,
        "signs": signs,
        "camera_rig": cam_rig,
    }


def parse_cli_args():
    """Parse arguments passed after '--' in Blender CLI."""
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    parser = argparse.ArgumentParser(description="Build and render Nico 15s Low-Poly Animation V2")
    parser.add_argument(
        "--mode",
        choices=["build", "stills", "video-preview", "video-final", "all"],
        default="build",
        help="Execution mode",
    )
    return parser.parse_args(argv)


def main():
    args = parse_cli_args()
    from pipeline_v3.config import PROJECT_CACHE_DIR

    ep_dir = PROJECT_CACHE_DIR / "EP001" / "piloto_V2"
    blend_out = str(ep_dir / "cenas" / "cena_01_V2.blend")
    previews_dir = str(ep_dir / "previews" / "v2")
    mp4_out = str(ep_dir / "videos" / "preview_15s_V2.mp4")

    preset = "final_video" if args.mode in ("video-final", "all") else "preview_stills"
    data = build_complete_scene(preset_name=preset)
    scene = data["scene"]

    script_file = str(SCRIPTS_DIR / "build_scene_v2.py")
    render_pipeline.embed_script_in_blend(script_file)
    render_pipeline.save_blend_file(blend_out)

    if args.mode in ("stills", "all"):
        render_pipeline.render_representative_frames(scene, previews_dir, preset_name="preview_stills")
        render_pipeline.save_blend_file(blend_out)

    if args.mode == "video-preview":
        render_pipeline.render_mp4_animation(scene, mp4_out, preset_name="preview_video")

    if args.mode in ("video-final", "all"):
        render_pipeline.render_mp4_animation(scene, mp4_out, preset_name="final_video")
        scene_setup.configure_scene_and_render(scene, preset_name="final_video")
        render_pipeline.save_blend_file(blend_out)


if __name__ == "__main__":
    main()
