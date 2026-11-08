"""Modular character and prop animation entry point (delegates to pipeline_v3 without code duplication)."""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from pipeline_v3 import anim_character, anim_props


def animar_cena(cols, mats, nico, seller):
    """Build and keyframe interactive props and character animations on an initialized V3 scene."""
    sack = anim_props.build_and_animate_potato_sack(cols["Col_Props_Animados"], mats)
    signs = anim_props.build_and_animate_refusal_and_milk_signs(cols["Col_Props_Animados"], mats)
    anim_character.animate_nico(nico)
    anim_character.animate_seller(seller)
    return {"sack": sack, "signs": signs}

