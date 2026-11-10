"""Modular camera & shot choreography entry point (delegates to pipeline_v3 without code duplication)."""

import sys
from pathlib import Path
import bpy

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from pipeline_v3 import cinematography


def configurar_camera_cena(opening_variant="A"):
    """Configure and keyframe the 7-shot vertical 9:16 camera rig on the active scene."""
    scene = bpy.context.scene
    col_lights = bpy.data.collections.get("Col_Luzes_Cameras") or scene.collection
    return cinematography.setup_and_animate_camera(scene, col_lights, opening_variant=opening_variant)


if __name__ == "__main__":
    configurar_camera_cena()

