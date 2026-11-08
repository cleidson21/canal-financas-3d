"""Reusable Blender Asset Library generator for canal-financas-3d (Section 11 & Section 14).

Generates real, non-empty, Asset-Browser-ready .blend files:
- personagens/nico_base.blend
- cenarios/vila.blend
- cenarios/feira.blend
- objetos/batatas.blend
- objetos/sapatos.blend
- objetos/fichas.blend
"""

from pathlib import Path
import bpy
from . import (
    anim_props,
    character_nico,
    environment_fair,
    materials_lighting,
    scene_setup,
)


def _save_library_blend(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Use relative paths when saving library .blend files
    # Evita o erro de caminho do cache de miniaturas neste processo.
    bpy.context.preferences.filepaths.file_preview_type = 'NONE'
    bpy.ops.wm.save_as_mainfile(filepath=str(path), relative_remap=True)
    print(f"[ASSET LIB OK] Saved reusable library: {path}")


def build_all_reusable_libraries(output_root: Path):
    """Generate all standalone reusable .blend asset libraries with real 3D models and materials."""
    scene = bpy.context.scene

    # 1. personagens/nico_base.blend
    scene_setup.clean_scene()
    cols = scene_setup.create_collections(scene)
    scene_setup.configure_scene_and_render(scene, preset_name="preview_stills")
    mats = materials_lighting.build_material_library()
    materials_lighting.setup_world_and_lighting(scene, cols["Col_Luzes_Cameras"])
    nico = character_nico.build_character_nico(cols["Col_Personagem_Nico"], mats)
    nico["root"].location = (0.0, 0.0, 0.0)
    nico["root"].rotation_euler = (0.0, 0.0, 0.0)
    _save_library_blend(output_root / "personagens" / "nico_base.blend")

    # 2. cenarios/vila.blend & cenarios/feira.blend
    scene_setup.clean_scene()
    cols = scene_setup.create_collections(scene)
    scene_setup.configure_scene_and_render(scene, preset_name="preview_stills")
    mats = materials_lighting.build_material_library()
    materials_lighting.setup_world_and_lighting(scene, cols["Col_Luzes_Cameras"])
    environment_fair.build_village_and_fair(cols, mats)
    try:
        cols["Col_Cenario_Vila"].asset_mark()
        cols["Col_Feira_Barraca"].asset_mark()
    except Exception:
        pass
    _save_library_blend(output_root / "cenarios" / "feira.blend")
    _save_library_blend(output_root / "cenarios" / "vila.blend")

    # 3. objetos/batatas.blend (40kg Burlap Potato Sack)
    scene_setup.clean_scene()
    cols = scene_setup.create_collections(scene)
    mats = materials_lighting.build_material_library()
    sack = anim_props.build_potato_sack_geometry(cols["Col_Props_Animados"], mats, start_pos=(0.0, 0.0, 0.0))
    try:
        sack.asset_mark()
        cols["Col_Props_Animados"].asset_mark()
    except Exception:
        pass
    _save_library_blend(output_root / "objetos" / "batatas.blend")

    # 4. objetos/sapatos.blend (Pair of New Display Sneakers)
    scene_setup.clean_scene()
    cols = scene_setup.create_collections(scene)
    mats = materials_lighting.build_material_library()
    shoes = environment_fair.build_pair_of_new_shoes(
        "Par_Sapatos_Biblioteca", (0.0, 0.0, 0.0), 0.0, mats, cols["Col_Props_Animados"]
    )
    try:
        shoes.asset_mark()
        cols["Col_Props_Animados"].asset_mark()
    except Exception:
        pass
    _save_library_blend(output_root / "objetos" / "sapatos.blend")

    # 5. objetos/fichas.blend (Refusal Red X & Milk Desire 3D Signs)
    scene_setup.clean_scene()
    cols = scene_setup.create_collections(scene)
    mats = materials_lighting.build_material_library()
    signs = anim_props.build_story_signs_geometry(cols["Col_Props_Animados"], mats)
    signs["x_sign"].location = (-0.55, 0.0, 0.0)
    signs["milk_sign"].location = (0.55, 0.0, 0.0)
    try:
        signs["x_sign"].asset_mark()
        signs["milk_sign"].asset_mark()
        cols["Col_Props_Animados"].asset_mark()
    except Exception:
        pass
    _save_library_blend(output_root / "objetos" / "fichas.blend")

