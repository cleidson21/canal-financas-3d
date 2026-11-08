"""Main orchestrator script for building, animating, validating, and rendering V3 in Blender 5.2.3 LTS.

Usage from command line:
  blender.exe -b --factory-startup -P scripts/build_scene.py -- --mode build
  blender.exe -b --factory-startup -P scripts/build_scene.py -- --mode libraries
  blender.exe -b --factory-startup -P scripts/build_scene.py -- --mode audit-stills
  blender.exe -b --factory-startup -P scripts/build_scene.py -- --mode openings-test
  blender.exe -b --factory-startup -P scripts/build_scene.py -- --mode video-preview
  blender.exe -b --factory-startup -P scripts/build_scene.py -- --mode video-final
  blender.exe -b --factory-startup -P scripts/build_scene.py -- --mode all

Can also be executed directly inside Blender's Scripting tab (Run Script).
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

from pipeline_v3 import (
    config,
    scene_setup,
    primitives,
    materials_lighting,
    environment_fair,
    character_nico,
    anim_props,
    anim_character,
    cinematography,
    asset_library,
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
    asset_library,
    render_pipeline,
):
    importlib.reload(_mod)


def build_complete_scene_v3(preset_name="preview_stills", opening_variant="A"):
    """Build the complete V3 scene idempotently (village, fair, handcart, Nico V3, props, animations, and 7-shot camera)."""
    scene = bpy.context.scene
    scene_setup.clean_scene()
    cols = scene_setup.create_collections(scene)
    scene_setup.configure_scene_and_render(scene, preset_name=preset_name)

    # 1. Materials & 4-Point Lighting + Shoe Accent Light
    mats = materials_lighting.build_material_library()
    lights = materials_lighting.setup_world_and_lighting(scene, cols["Col_Luzes_Cameras"])

    # 2. Environment, Handcart & Cobbler Market Stall
    env = environment_fair.build_village_and_fair(cols, mats)

    # 3. Characters (Nico V3 with Armature skinning & fixed sneaker + Seller V3)
    nico = character_nico.build_character_nico(cols["Col_Personagem_Nico"], mats)
    seller = character_nico.build_character_seller(cols["Col_Feira_Barraca"], mats)

    # 4. Interactive Props & Story Symbols (40kg Potato Sack on Cart -> Counter 'PLOC!', Red X, Large Milk Icon)
    sack = anim_props.build_and_animate_potato_sack(cols["Col_Props_Animados"], mats)
    signs = anim_props.build_and_animate_refusal_and_milk_signs(cols["Col_Props_Animados"], mats)

    # 5. Character Animations
    anim_character.animate_nico(nico)
    anim_character.animate_seller(seller)

    # 6. 7-Shot Vertical 9:16 Cinematography
    cam_rig = cinematography.setup_and_animate_camera(
        scene, cols["Col_Luzes_Cameras"], opening_variant=opening_variant
    )

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
    parser = argparse.ArgumentParser(description="Build and render Nico 15s Animation V3 (Blender 5.2.3 LTS)")
    parser.add_argument(
        "--mode",
        choices=[
            "build",
            "libraries",
            "audit-stills",
            "openings-test",
            "video-preview",
            "video-final",
            "all",
        ],
        default="build",
        help="Execution mode",
    )
    parser.add_argument(
        "--opening",
        choices=["A", "B"],
        default="A",
        help="Cold open camera variant (A = Close-up shoe opening first, B = Wide stumble first)",
    )
    return parser.parse_args(argv)


def main():
    args = parse_cli_args()
    ep_dir = config.PROJECT_CACHE_DIR / "EP001" / "piloto_V3"
    blend_v3 = ep_dir / "cenas" / "cena_01_V3.blend"
    previews_v3_dir = ep_dir / "previews" / "v3"
    renders_v3_dir = ep_dir / "renders"
    videos_dir = ep_dir / "videos"
    mp4_preview = videos_dir / "preview_15s_V3_lowres.mp4"
    mp4_final = videos_dir / "preview_15s_V3.mp4"

    if args.mode in ("libraries", "all"):
        asset_library.build_all_reusable_libraries(ep_dir / "bibliotecas")

    if args.mode in ("openings-test", "all"):
        openings_dir = previews_v3_dir / "aberturas"
        for var in ("A", "B"):
            data_op = build_complete_scene_v3(preset_name="preview_stills", opening_variant=var)
            sc = data_op["scene"]
            render_pipeline.render_frame_list(
                sc,
                openings_dir,
                [(15, f"abertura_{var}_0_5s"), (45, f"abertura_{var}_1_5s"), (62, f"abertura_{var}_2_1s")],
                preset_name="preview_stills",
            )
            render_pipeline.render_mp4_animation(
                sc,
                videos_dir / f"abertura_{var}_3s.mp4",
                preset_name="preview_video",
                frame_start=1,
                frame_end=90,
            )

    preset = "final_video" if args.mode in ("video-final", "all") else "preview_stills"
    data = build_complete_scene_v3(preset_name=preset, opening_variant=args.opening)
    scene = data["scene"]

    script_file = SCRIPTS_DIR / "build_scene.py"
    render_pipeline.embed_script_in_blend(script_file)
    render_pipeline.save_blend_file(blend_v3)

    if args.mode in ("audit-stills", "all"):
        # Render character & shoe close-ups
        render_pipeline.render_character_and_shoe_closeups(
            scene, previews_v3_dir / "closeups", preset_name="high_stills"
        )
        # Render mandatory Section 17 audit timestamps (0.5s, 1.5s, 3.5s, 6.0s, 9.5s, 12.5s, 14.5s)
        render_pipeline.render_frame_list(
            scene, previews_v3_dir / "auditoria", config.MANDATORY_AUDIT_FRAMES, preset_name="high_stills"
        )
        # Render V2-equivalent frames (28, 75, 112, 190, 285, 352, 382, 430) for 1:1 comparison
        render_pipeline.render_frame_list(
            scene, previews_v3_dir, config.V2_EQUIVALENT_FRAMES, preset_name="high_stills"
        )
        # Generate side-by-side V2 vs. V3 contact sheet
        render_pipeline.generate_v2_v3_contact_sheet(
            config.EP001_PILOT_DIR / "previews" / "v2",
            previews_v3_dir,
            ep_dir / "previews" / "comparativo_V2_vs_V3.png",
        )
        render_pipeline.save_blend_file(blend_v3)

    if args.mode == "video-preview":
        render_pipeline.render_mp4_animation(scene, mp4_preview, preset_name="preview_video")

    if args.mode in ("video-final", "all"):
        render_pipeline.render_mp4_animation(scene, mp4_final, preset_name="final_video")
        scene_setup.configure_scene_and_render(scene, preset_name="final_video")
        render_pipeline.save_blend_file(blend_v3)


if __name__ == "__main__":
    main()
