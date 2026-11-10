"""Modular stage assembly entry point (delegates to pipeline_v3 without code duplication)."""

import sys
from pathlib import Path
import bpy

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from pipeline_v3 import character_nico, environment_fair, materials_lighting, scene_setup


def montar_cena_base(preset_name="preview_stills"):
    """Initialize scene collections, lighting, village environment, market stall, and characters."""
    scene = bpy.context.scene
    scene_setup.clean_scene()
    cols = scene_setup.create_collections(scene)
    scene_setup.configure_scene_and_render(scene, preset_name=preset_name)
    mats = materials_lighting.build_material_library()
    lights = materials_lighting.setup_world_and_lighting(scene, cols["Col_Luzes_Cameras"])
    env = environment_fair.build_village_and_fair(cols, mats)
    nico = character_nico.build_character_nico(cols["Col_Personagem_Nico"], mats)
    seller = character_nico.build_character_seller(cols["Col_Feira_Barraca"], mats)
    return {"scene": scene, "collections": cols, "materials": mats, "lights": lights, "env": env, "nico": nico, "seller": seller}


if __name__ == "__main__":
    montar_cena_base()

