"""Automated Technical Test Suite for Pipeline V3 (Section 18).

Can be executed via Blender headless:
  blender.exe -b --factory-startup -P testes/test_pipeline_v3.py
"""

import ast
import hashlib
import json
import sys
from pathlib import Path
import bpy


def get_project_root() -> Path:
    here = Path(__file__).resolve()
    return here.parent.parent


PROJECT_ROOT = get_project_root()
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def test_01_python_syntax_and_relative_paths():
    """Verify syntax of all Python scripts and ensure no hardcoded user paths outside config/tests."""
    py_files = list(SCRIPTS_DIR.rglob("*.py")) + list((PROJECT_ROOT / "testes").rglob("*.py"))
    assert len(py_files) >= 15, f"Expected at least 15 Python files, found {len(py_files)}"
    for pf in py_files:
        src = pf.read_text(encoding="utf-8")
        ast.parse(src, filename=str(pf))
        # Ensure pipeline_v3 modules use pathlib.Path instead of hardcoded C:\Users paths
        if "pipeline_v3" in pf.parts:
            assert "C:\\Users" not in src and "c:\\Users" not in src, f"Hardcoded path in {pf}"
    print(f"[PASS] test_01_python_syntax_and_relative_paths ({len(py_files)} files verified)")


def test_02_module_imports():
    """Verify all pipeline_v3 modules and entry scripts import cleanly."""
    import build_scene
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
    assert config.FPS == 30
    assert config.RES_X == 1080
    assert config.RES_Y == 1920
    assert config.FRAME_END == 450
    print("[PASS] test_02_module_imports")


def test_03_legacy_backups_integrity():
    """Verify V1 and V2 legacy files are preserved intact in backups/legado with matching SHA-256."""
    manifest_path = PROJECT_ROOT / "backups" / "legado" / "MANIFESTO_MIGRACAO.json"
    assert manifest_path.is_file(), f"Missing migration manifest: {manifest_path}"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("migrated_files", [])
    assert len(files) >= 20, f"Expected at least 20 backed-up files in manifest, got {len(files)}"

    verified_copies = 0
    for entry in files:
        for copy_info in entry.get("copies", []):
            dest_rel = copy_info["destination"]
            # scripts/build_scene_v2.py was intentionally updated in Stage B to use pathlib.Path,
            # while backups/legado/build_scene_v2.py preserves the exact byte-for-byte original SHA-256!
            if dest_rel.startswith("backups/legado/"):
                b_path = PROJECT_ROOT / dest_rel
                assert b_path.is_file(), f"Missing backup file: {b_path}"
                actual_hash = sha256_file(b_path)
                assert actual_hash == entry["sha256"], f"SHA-256 mismatch on {b_path}"
                verified_copies += 1
    print(f"[PASS] test_03_legacy_backups_integrity ({verified_copies} legacy backup files SHA-256 verified)")


def test_04_idempotent_build_and_scene_parameters():
    """Verify building the V3 scene twice produces zero .001 duplicates and exact scene settings."""
    import build_scene

    # First build
    build_scene.build_complete_scene_v3(preset_name="preview_stills", opening_variant="A")
    count_first = len(bpy.data.objects)

    # Second build (idempotency check)
    build_scene.build_complete_scene_v3(preset_name="preview_stills", opening_variant="A")
    count_second = len(bpy.data.objects)

    assert count_first == count_second, f"Object count changed across runs: {count_first} vs {count_second}"
    dup_objs = [o.name for o in bpy.data.objects if ".001" in o.name]
    assert not dup_objs, f"Found duplicate .001 objects after re-run: {dup_objs}"

    scene = bpy.context.scene
    assert scene.render.fps == 30, f"Expected 30 FPS, got {scene.render.fps}"
    assert scene.render.resolution_x == 1080, f"Expected width 1080, got {scene.render.resolution_x}"
    assert scene.render.resolution_y == 1920, f"Expected height 1920, got {scene.render.resolution_y}"
    assert scene.frame_start == 1 and scene.frame_end == 450, "Expected frame range 1..450 (15.0s)"
    assert scene.camera is not None and scene.camera.name == "Camera_Principal", "Missing active Camera_Principal"

    required_cols = [
        "Col_Cenario_Vila",
        "Col_Feira_Barraca",
        "Col_Personagem_Nico",
        "Col_Props_Animados",
        "Col_Luzes_Cameras",
    ]
    for cname in required_cols:
        col = bpy.data.collections.get(cname)
        assert col is not None and len(col.objects) > 0, f"Missing or empty collection: {cname}"

    required_objs = [
        "Nico_Root",
        "Nico_Armature_V3",
        "Nico_Braco_Continuo_L",
        "Nico_Braco_Continuo_R",
        "Nico_Perna_Continua_L",
        "Nico_Perna_Continua_R",
        "Nico_Tenis_Corpo_R",
        "Nico_Tenis_SolaFrontal_R",
        "Nico_Tenis_MeiaInterna_R",
        "Nico_Sola_Descolada_Pivot_R",
        "Carrinho_Batatas_Root",
        "Saco_Batatas_Root",
        "Par_Sapatos_Novos_Root",
        "Placa_Recusa_X_Root",
        "Placa_Desejo_Leite_Root",
        "Camera_Principal",
        "Camera_Target",
    ]
    for oname in required_objs:
        assert bpy.data.objects.get(oname) is not None, f"Missing required object: {oname}"

    # Ensure V2's protruding red sphere defect (Nico_Dedao_Exposto_R) does NOT exist in V3
    assert bpy.data.objects.get("Nico_Dedao_Exposto_R") is None, "Legacy V2 protruding toe sphere still present!"
    print(f"[PASS] test_04_idempotent_build_and_scene_parameters ({count_second} objects, 0 duplicates)")


def test_05_reusable_blend_libraries_and_main_scene():
    """Verify all reusable .blend libraries and cena_01_V3.blend exist and open cleanly in Blender."""
    expected_blends = [
        PROJECT_ROOT / "personagens" / "nico_base.blend",
        PROJECT_ROOT / "cenarios" / "feira.blend",
        PROJECT_ROOT / "cenarios" / "vila.blend",
        PROJECT_ROOT / "objetos" / "batatas.blend",
        PROJECT_ROOT / "objetos" / "sapatos.blend",
        PROJECT_ROOT / "objetos" / "fichas.blend",
        PROJECT_ROOT / "arquivo" / "EP001" / "piloto" / "cenas" / "cena_01_V3.blend",
        PROJECT_ROOT / "arquivo" / "EP001" / "piloto" / "cenas" / "cena_01_V2.blend",
    ]
    for bp in expected_blends:
        assert bp.is_file() and bp.stat().st_size > 50_000, f"Missing or invalid .blend file: {bp}"
        bpy.ops.wm.open_mainfile(filepath=str(bp))
        assert len(bpy.data.objects) > 0, f"Opened .blend has 0 objects: {bp}"
    print(f"[PASS] test_05_reusable_blend_libraries_and_main_scene ({len(expected_blends)} .blend files verified)")


def test_06_rendered_outputs_and_videos():
    """Verify rendered audit stills, close-ups, contact sheet, and MP4 videos."""
    ep_dir = PROJECT_ROOT / "arquivo" / "EP001" / "piloto"
    audit_dir = ep_dir / "previews" / "v3" / "auditoria"
    closeups_dir = ep_dir / "previews" / "v3" / "closeups"
    contact_sheet = ep_dir / "previews" / "comparativo_V2_vs_V3.png"

    audit_pngs = list(audit_dir.glob("*.png"))
    closeup_pngs = list(closeups_dir.glob("*.png"))
    assert len(audit_pngs) >= 7, f"Expected 7 mandatory audit stills, found {len(audit_pngs)}"
    assert len(closeup_pngs) >= 4, f"Expected 4 closeup stills, found {len(closeup_pngs)}"
    assert contact_sheet.is_file() and contact_sheet.stat().st_size > 50_000, "Missing V2 vs V3 contact sheet"

    # Check MP4 videos if already rendered
    videos_dir = ep_dir / "videos"
    mp4_final = videos_dir / "preview_15s_V3.mp4"
    if mp4_final.is_file():
        assert mp4_final.stat().st_size > 100_000, f"Final MP4 too small: {mp4_final}"
        scene = bpy.context.scene
        if not scene.sequence_editor:
            scene.sequence_editor_create()
        se = scene.sequence_editor
        strip_coll = se.strips if hasattr(se, "strips") else se.sequences
        strip = strip_coll.new_movie(name="CheckMP4", filepath=str(mp4_final), channel=1, frame_start=1)
        assert strip.frame_final_duration == 450, f"Expected 450 frames in MP4, got {strip.frame_final_duration}"
        strip_coll.remove(strip)
        print(f"[PASS] test_06_rendered_outputs_and_videos (stills + 450-frame MP4 verified)")
    else:
        print(f"[PASS] test_06_rendered_outputs_and_videos (stills & contact sheet verified)")


def run_all_tests():
    print("=" * 72)
    print("RUNNING PIPELINE V3 AUTOMATED TECHNICAL TEST SUITE")
    print("=" * 72)
    test_01_python_syntax_and_relative_paths()
    test_02_module_imports()
    test_03_legacy_backups_integrity()
    test_04_idempotent_build_and_scene_parameters()
    test_05_reusable_blend_libraries_and_main_scene()
    test_06_rendered_outputs_and_videos()
    print("=" * 72)
    print("ALL PIPELINE V3 TESTS PASSED SUCCESSFULLY!")
    print("=" * 72)


if __name__ == "__main__":
    run_all_tests()
